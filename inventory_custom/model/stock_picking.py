from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    purchase_request_ids = fields.One2many(comodel_name="purchase.request", inverse_name="picking_id", string="Purchase Request", required=False, )

    def action_create_purchase_request(self):
        # product_jasa = self.env['product.product'].search([('type', '=', 'service')], limit=1)
        # pr_line = self.env['purchase.request.line'].create({
        #     'date_required': datetime.datetime.now(),
        #     'product_id': product_jasa.id
        # })
        return {
            'name': 'Create Purchase Request',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.request',
            # 'views': [(view.id, 'form')],
            # 'view_id': view.id,
            'target': 'new',
            'context': {}
        }


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_name = fields.Char(related='product_id.name')


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    product_name = fields.Char(related='product_id.name')

