from odoo import fields,models,api

class stockMove(models.Model):
    _inherit = 'stock.move'

    cogs_price = fields.Float()