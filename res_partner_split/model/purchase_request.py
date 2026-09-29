from odoo import api, fields, models


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order'

    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        domain="[('supplier_rank', '>', 0)]",
        required=True,
    )
