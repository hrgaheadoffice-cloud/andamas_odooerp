from odoo import api, fields, models


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    picking_id = fields.Many2one(comodel_name="stock.picking", string="Stock Picking", required=False, )

