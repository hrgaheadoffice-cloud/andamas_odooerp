from odoo import api, fields, models, _


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    delivery_address = fields.Char()