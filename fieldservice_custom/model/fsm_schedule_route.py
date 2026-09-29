from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class FSMScheduleRoute(models.Model):
    _name = 'fsm.schedule.route'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = 'id desc'

    @api.depends('route_change', 'route_change_2', 'route_change_3', 'route_change_4', 'route_change_5')
    def _compute_amount(self):
        for line in self:
            line.balance_cost = 1
            balance = line.route_cost - line.route_change_cost
            balance_2 = line.route_cost_2 - line.route_change_cost_2
            balance_3 = line.route_cost_3 - line.route_change_cost_3
            balance_4 = line.route_cost_4 - line.route_change_cost_4
            balance_5 = line.route_cost_5 - line.route_change_cost_5
            line.update({
                'balance_cost': balance,
                'balance_cost_2': balance_2,
                'balance_cost_3': balance_3,
                'balance_cost_4': balance_4,
                'balance_cost_5': balance_5
            })

    created_by = fields.Many2one('res.users', default=lambda self: self.env.uid)
    date = fields.Datetime('Date & Time', default=fields.Datetime.now)
    shift = fields.Selection([
        ('day', 'Day'),
        ('night', 'Night')
    ])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('close', 'Closed')
    ], default='draft')

    route = fields.Many2one('fsm.orders', 'Main Route 1', domain="[('state', '=', 'progress')]")
#    route_cost = fields.Float('Transporter Cost', related='route.cost', readonly=1, store=1)
    route_change = fields.Many2one('fsm.orders', 'Change Route 1', domain="[('state', '=', 'progress')]")
#     route_change_cost = fields.Float('Transporter Cost', related='route_change.cost', readonly=1, store=1)
#     balance_cost = fields.Float('Balance Transporter Cost', compute='_compute_amount', readonly=1, store=1)
    route_2 = fields.Many2one('fsm.orders', 'Main Route 2', domain="[('state', '=', 'progress')]")
#     route_cost_2 = fields.Float('Transporter Cost', related='route_2.cost', readonly=1, store=1)
    route_change_2 = fields.Many2one('fsm.orders', 'Change Route 2', domain="[('state', '=', 'progress')]")
#     route_change_cost_2 = fields.Float('Transporter Cost', related='route_change_2.cost', readonly=1, store=1)
#     balance_cost_2 = fields.Float('Balance Transporter Cost', compute='_compute_amount', readonly=1, store=1)
    route_3 = fields.Many2one('fsm.orders', 'Main Route 3', domain="[('state', '=', 'progress')]")
#     route_cost_3 = fields.Float('Transporter Cost', related='route_3.cost', readonly=1, store=1)
    route_change_3 = fields.Many2one('fsm.orders', 'Change Route 3', domain="[('state', '=', 'progress')]")
#     route_change_cost_3 = fields.Float('Transporter Cost', related='route_change_3.cost', readonly=1, store=1)
#     balance_cost_3 = fields.Float('Balance Transporter Cost', compute='_compute_amount', readonly=1, store=1)
    route_4 = fields.Many2one('fsm.orders', 'Main Route 4', domain="[('state', '=', 'progress')]")
#     route_cost_4 = fields.Float('Transporter Cost', related='route_4.cost', readonly=1, store=1)
    route_change_4 = fields.Many2one('fsm.orders', 'Change Route 4', domain="[('state', '=', 'progress')]")
#     route_change_cost_4 = fields.Float('Transporter Cost', related='route_change_4.cost', readonly=1, store=1)
#     balance_cost_4 = fields.Float('Balance Transporter Cost', compute='_compute_amount', readonly=1, store=1)
    route_5 = fields.Many2one('fsm.orders', 'Main Route 5', domain="[('state', '=', 'progress')]")
#     route_cost_5 = fields.Float('Transporter Cost', related='route_5.cost', readonly=1, store=1)
    route_change_5 = fields.Many2one('fsm.orders', 'Change Route 5', domain="[('state', '=', 'progress')]")
#     route_change_cost_5 = fields.Float('Transporter Cost', related='route_change_5.cost', readonly=1, store=1)
#     balance_cost_5 = fields.Float('Balance Transporter Cost', compute='_compute_amount', readonly=1, store=1)
    order_ids = fields.Char()

    def action_confirm(self):
        self.state = 'confirm'

    def action_close(self):
        self.state = 'close'
