from odoo import api, fields, models
from datetime import datetime


class FuelConsumption(models.Model):
    _name = 'fuel.consumption'
    _rec_name = 'id'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.depends('product_price', 'fuel_qty')
    def _compute_total_price(self):
        for line in self:
            total_price = line.product_price * line.fuel_qty
            line.update({
                'total_price': total_price
            })

    @api.depends('hm', 'km')
    def _compute_hm_km(self):
        for rec in self:
            rec.hm_km = str(rec.hm) + "/" + str(rec.km)

    name = fields.Char()
    created_by = fields.Char()
    date = fields.Datetime(string='Date & Time', default=fields.Datetime.now, store=True)
    equipment_id = fields.Many2one('master_asset_maintenance', 'Unit Code')
    driver = fields.Char()
    hm = fields.Float()
    km = fields.Float()
    hm_km = fields.Char('HM/KM', compute=_compute_hm_km)
    product_id = fields.Many2one('product.product', 'Product')
    product_price = fields.Float('Price')
    begin_balance = fields.Float('Fuel Begin (L)')
    fuel_qty = fields.Float()
    final_balance = fields.Float('Fuel Balance (L)')
    total_price = fields.Float(compute=_compute_total_price)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm')
    ], default='draft')
    operation = fields.Char()

    plotting = fields.Many2one(related="equipment_id.plotting_location",string='Plotting Location', store=1)
    fuel_truck = fields.Many2one('master_asset_maintenance', string='Fuel Truck')
    fuel_man = fields.Char()
    shift = fields.Char()
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    no_ticket = fields.Char()
    fuel_source = fields.Many2one('fuel.source')
    owner = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
    ], 'Fuel Owner', related='fuel_source.owner')

    def fuel_consumption_journal(self):
        move = self.env['account.move']
        journal_id = self.env['account.journal'].search([('name', '=', 'Inventory Valuation'), ('company_id', '=', self.company_id.id)]).id

        generate_data_line = [
            (0, 0, {
                'account_id': self.fuel_source.incoming_account.id,
                'credit': self.total_price,
                'name': self.operation
            }),
            (0, 0, {
                'account_id': self.equipment_id.category.outgoing_account.id,
                'debit': self.total_price,
            }),
        ]
        generate_data = {
            'ref': '%s - %s' % (self.operation, self.name),
            'journal_id': journal_id,
            'line_ids': generate_data_line,
        }
        move_id = move.create(generate_data)
        move_id.action_post()
        return


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('fuel.consumption.seq')
        res = super(FuelConsumption, self).create(vals)
        if 'TRUCK' in res.equipment_id.category.name and res.plotting.name == 'LDP-SPGA':
            last_timesheet = self.env['tbl_mnt_timesheet_equipment'].search([('name', '=', res.equipment_id.id)], order='id desc', limit=1)
            timesheet = self.env['tbl_mnt_timesheet_equipment'].create({
                'tanggal': res.date,
                'shift': res.shift,
                'name': res.equipment_id.id,
                'hm_akhir': res.hm
            })
            if last_timesheet:
                date_diff = res.date.day - last_timesheet.tanggal.day
                ewh = (res.hm - last_timesheet.hm_akhir) / (date_diff if date_diff > 0 else 1)
                timesheet.update({
                    'hm_awal': last_timesheet.hm_akhir,
                    'ewh': ewh
                    })
        return res

    def action_submit(self):
        # location_id = self.env['stock.location'].sudo().search([('name', '=', 'Stock'), ('usage', '=', 'internal'), ('company_id', '=', self.company_id.id)], limit=1)
        if self.owner == 'internal':
            location_dest_id = self.env.ref('stock.stock_location_customers')
            moves = self.env['stock.move'].create({
                'name': self.name,
                'product_id': self.product_id.id,
                'product_uom_qty': self.fuel_qty,
                'product_uom': self.product_id.uom_id.id,
                'product_uom_category_id': self.product_id.uom_id.category_id.id,
                'location_id': self.fuel_source.stock.id,
                'location_dest_id': location_dest_id.id,
                'quantity_done': self.fuel_qty,
                'company_id': self.env.company.id,
                'consumption_id': self.id
            })
            # context = dict(self.env.context or {})
            # if context.get('move_id'):
            #     move_id = context['move_id']
            #     moves.update({
            #         'account_move_ids': [(6, 0, [move_id])]
            #     })
            moves._action_done()
        else:
            self.fuel_consumption_journal()
        self.state = 'confirm'

    @api.onchange('product_id')
    def _onchange_price_qty(self):
        for line in self:
            if line.product_id:
                product_price = line.product_id.standard_price
                line.update({
                    'product_price': product_price,
                })

    @api.onchange('fuel_source')
    def _onchange_price_qty(self):
        for line in self:
            if line.fuel_source:
                begin_balance = line.fuel_source.quantity
                product_id = line.fuel_source.product_id
                product_price = product_id.standard_price
                line.update({
                    'product_id': product_id,
                    'begin_balance': begin_balance,
                    'product_price': product_price,
                })


class FuelConsumeOperation(models.Model):
    _name = 'fuel.consumption.operation'

    name = fields.Char('Operation')
    incomming_account = fields.Many2one('account.account', 'Incomming Account')
    outgoing_account = fields.Many2one('account.account', 'Outgoing Account')
