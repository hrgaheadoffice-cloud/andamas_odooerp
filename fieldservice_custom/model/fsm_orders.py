from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class FSMOrders(models.Model):
    _name = 'fsm.orders'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = 'id desc'

    date = fields.Datetime('Date & Time', default=fields.Datetime.now)
    sale_order_id = fields.Char('Physical SPK')
    name = fields.Char('No. Transporter Order', readonly=1, store=1, default='New')
    route_id = fields.Many2one(related='product_route.route_id', required=1)
    cost = fields.Float()
    status = fields.Char()
    created_by = fields.Many2one('res.users', readonly=1, store=1, default=lambda self: self.env.uid)
    transporter_type = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
    ], related='product_route.transporter_type', readonly=1)
    # freight_product = fields.Many2one('fsm.freight.product', required=1)
    product_route = fields.Many2one('fsm.route.fares', required=1)
    loading_location = fields.Many2one(related='product_route.loading_location', readonly=1)
    unloading_location = fields.Many2one(related='product_route.unloading_location', readonly=1)
    distance = fields.Float(related='product_route.distance', readonly=1)
    total_qty = fields.Float('Total Quantity')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'Progress'),
        ('close', 'Closed')
    ], default='draft')
    achieve_qty = fields.Float()

    @api.model
    def create(self, vals):
        route_id = vals['product_route']
        route_name = self.env['fsm.route.fares'].search([('id', '=', route_id)], limit=1).name
        # freight_product = self.env['fsm.freight.product'].browse(vals['freight_product']).name
        vals['name'] = '{}/{}'.format(self.env['ir.sequence'].next_by_code('fsm.order.seq'), route_name)
        return super(FSMOrders, self).create(vals)

    def action_progress(self):
        self.state = 'progress'

    def action_close(self):
        self.state = 'close'


class FSMFreightProduct(models.Model):
    _name = 'fsm.freight.product'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char()
