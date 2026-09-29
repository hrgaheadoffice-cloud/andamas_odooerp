import datetime

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    purchase_request_ids = fields.One2many(comodel_name="purchase.request", inverse_name="mrp_id", string="Purchase Requests", required=False, )

    def action_create_purchase_request(self):
        product_jasa = self.env['product.product'].search([('type', '=', 'service')], limit=1)
        pr_line = self.env['purchase.request.line'].create({
            'date_required': datetime.datetime.now(),
            'product_id': product_jasa.id
        })
        return {
            'name': 'Create Purchase Request',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.request',
            # 'views': [(view.id, 'form')],
            # 'view_id': view.id,
            'target': 'new',
            'context': {
                'default_mrp_id': self.id,
                'default_line_ids': pr_line.ids
            }
        }
