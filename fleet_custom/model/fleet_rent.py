from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class FleetRent(models.Model):
    _inherit = 'fleet.rent'

    is_customer = fields.Boolean()
    is_vendor = fields.Boolean()
    partner_id = fields.Many2one('res.partner', domain=lambda self: self.compute_partner_id())
    rental_location = fields.Char()
    duration = fields.Char(compute='_compute_duration', store=1)
    fleet_rent_detail_ids = fields.One2many('fleet.rent.detail',
                                            'fleet_rent_id',
                                            string='Fleet Rent Detail')
    rent_amt = fields.Monetary(string='Rental Vehicle Rent',
                               currency_field='currency_id',
                               store=1,
                               compute='_amount_all')

    @api.depends('fleet_rent_detail_ids.subtotal')
    def _amount_all(self):
        for rec in self:
            rent_amt = 0.0
            for line in rec.fleet_rent_detail_ids:
                rent_amt += line.subtotal
            rec.update({
                'rent_amt': rent_amt
            })

    @api.depends('date_end')
    def _compute_duration(self):
        for rec in self:
            duration = 0
            if rec.date_end and rec.date_start:
                duration = str((datetime.date(rec.date_end) - datetime.date(rec.date_start)).days) + ' days'
            rec.duration = duration
            # to get the number, use duration.split(' ')[0]

    @api.model
    def compute_partner_id(self):
        domain = []
        ctx = self.env.context
        if ctx.get('default_is_customer'):
            domain = [('customer_rank', '>', 0)]
        elif ctx.get('default_is_vendor'):
            domain = [('supplier_rank', '>', 0)]
        return domain

    @api.model
    def hide_menu(self):
        menu_to_hide = [
            "fleet.fleet_vehicles",
            "fleet.menu_fleet_reporting",
            "fleet.fleet_configuration",
            "fleet_rent.menu_vehicle_rent"
        ]
        for menu in menu_to_hide:
            try:
                menu_obj = self.env.ref(menu)
                menu_obj.update({
                    'active': False
                })
            except:
                pass
        return


class FleetRentDetail(models.Model):
    _name = 'fleet.rent.detail'

    @api.depends('price', 'duration')
    def _compute_amount(self):
        for line in self:
            subtotal = line.price * line.duration
            line.update({
                'subtotal': subtotal
            })

    equipment_id = fields.Many2one('master_asset_maintenance', 'Unit Code')
    price = fields.Float()
    duration = fields.Float('Duration (days)', precision_digits=0)
    subtotal = fields.Float(compute='_compute_amount', store=1, readonly=1)
    fleet_rent_id = fields.Many2one('fleet.rent',
                                    string='Rental Vehicle')


class MaintenanceCost(models.Model):
    _inherit = 'maintenance.cost'

    @api.depends('price', 'quantity')
    def _compute_amount(self):
        for line in self:
            subtotal = line.price * line.quantity
            line.update({
                'cost': subtotal
            })

    product_id = fields.Many2one('product.template')
    quantity = fields.Float()
    uom = fields.Many2one('uom.uom')
    price = fields.Float()
    cost = fields.Float('Subtotal', compute='_compute_amount')
