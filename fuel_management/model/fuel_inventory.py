from odoo import api, fields, models


class FuelInventory(models.Model):
    _name = 'fuel.inventory'

    date = fields.Datetime()
    stock_in = fields.Float()
    stock_out = fields.Float()
    stock_start = fields.Float()
    stock_end = fields.Float()
    type = fields.Char()
