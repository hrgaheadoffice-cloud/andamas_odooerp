from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    work_order_id = fields.Many2one(comodel_name="work.order", string="Work Order", required=False, )
