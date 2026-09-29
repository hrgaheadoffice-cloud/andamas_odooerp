from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class FSMRoutes(models.Model):
    _name = 'fsm.routes'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Route Code")
    loading_location = fields.Many2one('fsm.locations', "Loading Location", domain=[('category', 'in', ['loading', 'both'])])
    unloading_location = fields.Many2one('fsm.locations', "Unloading Location", domain=[('category', 'in', ['unloading', 'both'])])
    distance = fields.Float("Distance (KM)")
    duration = fields.Float("Duration (Hours)")
    salary_route = fields.Float("Salary Route")
    price_route = fields.Float("Price Route")

    @api.model
    def create(self, vals):
        res = super(FSMRoutes, self).create(vals)
        res.name = f"{res.loading_location.code or res.loading_location.name} - {res.unloading_location.code or res.unloading_location.name}"
        return res
