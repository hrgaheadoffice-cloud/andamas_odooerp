from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class FSMTransporterCost(models.Model):
    _name = 'fsm.transporter.cost'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = 'route_id'

    @api.depends('meal_cost', 'fuel_cost', 'other_cost')
    def _compute_amount(self):
        for line in self:
            cost = line.meal_cost + line.fuel_cost + line.other_cost
            line.update({
                'cost': cost
            })

    route_id = fields.Many2one('fsm.routes', 'Route Code')
    loading_location = fields.Many2one(related='route_id.loading_location', readonly=1)
    unloading_location = fields.Many2one(related='route_id.unloading_location', readonly=1)
    distance = fields.Float(related='route_id.distance', readonly=1)
    duration = fields.Float(related='route_id.duration', readonly=1)
    cost = fields.Float('Transporter Cost', compute='_compute_amount', readonly=1, store=1)
    meal_cost = fields.Float()
    fuel_cost = fields.Float()
    other_cost = fields.Float()
    brand = fields.Char()
    salary_route = fields.Float("Salary Route", compute='_compute_salary_route', readonly=1, store=1)
    price_route = fields.Float("Price Route", compute='_compute_salary_route', readonly=1, store=1)

    @api.depends('route_id')
    def _compute_salary_route(self):
        for me in self:
            salary_routes = me.route_id.salary_route * me.route_id.distance
            price_routes = me.route_id.price_route * me.route_id.distance

            me.update({
                'salary_route': salary_routes,
                'price_route': price_routes
            })
        return
