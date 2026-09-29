from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class FSMRouteFares(models.Model):
    _name = 'fsm.route.fares'

    name = fields.Char("Product Route")
    loading_location = fields.Many2one(related='route_id.loading_location', readonly=1)
    unloading_location = fields.Many2one(related='route_id.unloading_location', readonly=1)
    distance = fields.Float(related='route_id.distance', string='Distance (KM)', readonly=1)
    duration = fields.Float("Duration (Hours)")
    salary_route = fields.Float("Salary Route")
    price_route = fields.Float("Price Route")
    transporter_type = fields.Selection(string='Transporter Type', selection=[
        ('internal', 'Internal'),
        ('external', 'External')],
        copy=False, index=True, tracking=True, default='internal')
    route_id = fields.Many2one('fsm.routes', 'Route Code', required=1)
    freight_product = fields.Many2one('fsm.freight.product', required=1)


    @api.model
    def create(self, vals):
        res = super(FSMRouteFares, self).create(vals)
        res.name = f"{res.route_id.name}/{res.freight_product.name}"
        return res
