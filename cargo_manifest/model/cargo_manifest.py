from odoo import api, fields, models


class CargoManifest(models.Model):
    _name = 'cargo.manifest'
    _order = 'reg_date ASC'

    # def _default_cm_name(self):
    #     name = self.env['ir.sequence'].next_by_code('cm') or 'New'
    #     return name

    name = fields.Char(readonly=True)
    reg_date = fields.Datetime('Date')
    user_id = fields.Many2one('res.users', 'Created by', default=lambda self: self.env.user)
    description = fields.Text()
    transport = fields.Char()
    driver = fields.Char()
    ship_from = fields.Char()
    ship_to = fields.Char()
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancel', 'Cancelled')
    ], default='draft')
    purchase_order_line = fields.Many2many('purchase.order.line', 'cm', string='Product', domain=[('state', '=', 'purchase'), ('qty_receive_done', '!=', True)])

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('cm') or 'New'
        res = super(CargoManifest, self).create(vals)
        return res

    def action_confirm(self):
        self.state = 'confirm'

    def action_cancel(self):
        self.state = 'cancel'
