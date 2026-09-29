from odoo import api, fields, models
from datetime import datetime


class FuelStock(models.Model):
    _name = 'fuel.stock'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    created_by = fields.Many2one('res.users', 'Created by', default=lambda self: self.env.uid, readonly=1, store=1)
    date = fields.Datetime(string='Date & Time', default=datetime.today(), readonly=True, store=True)
    product_id = fields.Many2one('product.template', 'Product')
    vendor = fields.Many2one('res.partner')
    truck = fields.Char()
    operator = fields.Char()
    begin_balance = fields.Float('Fuel Begin')
    refueling = fields.Float('Refueling (L)', compute='_compute_amount_requested')
    final_balance = fields.Float('Fuel Balance')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm')
    ], default='draft')
    seal_number = fields.Char('No. Seal')
    baps_number = fields.Char('No. BAPS')
    refueling_detail = fields.One2many('detail.refueling', 'fuel_stock_id')

    def action_submit(self):
        self.state = 'confirm'
        for refueling in self.refueling_detail:
            refueling.field_destination.tank_quantity += refueling.quantity
    #
    # @api.model
    # @api.onchange('refueling_detail')
    # def _compute_refueling(self):
    #     for rec in self:
    #         details = self.env['detail.refueling'].search([('fuel_stock_id','=', self.id)])
    #         fuel = 0.0
    #         for detail in details:
    #             fuel += detail.quantity
    #         self.refueling = fuel

    @api.depends('refueling_detail.quantity')
    def _compute_amount_requested(self):
        for advance in self:
            advance.refueling = sum(advance.refueling_detail.mapped('quantity'))


class DetailRefueling(models.Model):
    _name = 'detail.refueling'

    fuel_stock_id = fields.Many2one(comodel_name='fuel.stock', readonly=True)
    field_destination = fields.Many2one('fuel.source')
    quantity = fields.Float('Quantity')


class FuelSource(models.Model):
    _name = 'fuel.source'

    name = fields.Char('Fuel Name')
    owner = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
    ], 'Fuel Owner')
    product_id = fields.Many2one('product.product', 'Product')
    stock = fields.Many2one('stock.location', 'Fuel Stock')
    quantity = fields.Float('Fuel Quantity', compute='_compute_qty')
    price = fields.Float()
    # tank_quantity = fields.Integer('Tank Quantity')
    incoming_account = fields.Many2one('account.account', 'Incoming Account')
    # outgoing_account = fields.Many2one('account.account', 'Outgoing Account')
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    @api.onchange('product_id', 'stock')
    def _onchange_price_qty(self):
        for line in self:
            if line.stock and line.product_id:
                quantity = self.env['stock.quant'].search([('product_id', '=', line.product_id.id), ('location_id', '=', line.stock.id)]).available_quantity
                line.update({
                    'quantity': quantity,
                    'price': line.product_id.standard_price
                })
            elif line.product_id:
                quantity = line.product_id.qty_available
                line.update({
                    'quantity': quantity,
                    'price': line.product_id.standard_price
                })

    def _compute_qty(self):
        for line in self:
            self.quantity = 0
            if line.stock and line.product_id:
                quantity = self.env['stock.quant'].search([('product_id', '=', line.product_id.id), ('location_id', '=', line.stock.id)]).available_quantity
                line.update({
                    'quantity': quantity,
                })

