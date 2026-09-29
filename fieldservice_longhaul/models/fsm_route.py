# -*- coding: utf-8 -*-
from odoo import fields, models, api

class CustomFSMRoute(models.Model):
    _inherit = "fsm.route"

    brand = fields.Char("Brand")
    loading_location = fields.Char("Loading Location")
    loading_location_code = fields.Char("Loading Location Code")
    unloading_location = fields.Char("Unloading Location")
    unloading_location_code = fields.Char("Unloading Location Code")
    distance = fields.Float("Distance")
    est_time = fields.Float("Est. Time")
    hauling_expense = fields.Float("Hauling Expense")