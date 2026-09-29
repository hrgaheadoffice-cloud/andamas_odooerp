from odoo import api, fields, models, _


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def action_replenish(self):
        view = self.env.ref("purchase_request.view_purchase_request_form")
        line_vals = {
            'product_id': self.product_id.id,
            'product_qty': self.qty_to_order,
            'estimated_price_unit': self.product_id.list_price
        }
        return {
            'name': _('Purchase Request'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'purchase.request',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_line_ids': [[0, 0, line_vals]]
            }
        }
