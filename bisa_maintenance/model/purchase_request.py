from odoo import api, fields, models


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    work_order_id = fields.Many2one(comodel_name="work.order", string="Work Order", required=False, )
    mrp_id = fields.Many2one(comodel_name="mrp.production", string="Manufacturing Order", required=False, )

    def action_create_po(self):
        res = super(PurchaseRequest, self).action_create_po()
        po_id = res['res_id']
        po = self.env['purchase.order'].browse(po_id)
        po.work_order_id = self.work_order_id.id
        return res
