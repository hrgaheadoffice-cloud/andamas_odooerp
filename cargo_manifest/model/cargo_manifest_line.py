from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('qty_received', 'order_id.picking_ids.state')
    def _compute_qty_done(self):
        for me in self:
            if me.qty_cm:
                me.qty_receive_done = False
            elif me.product_qty == me.qty_received:
                me.qty_receive_done = True
            else:
                if me.order_id.picking_ids.filtered(lambda x: x.state == 'assigned'):
                    me.qty_receive_done = False
                else:
                    me.qty_receive_done = True

    cm = fields.Many2one('cargo.manifest')
    wo_id = fields.Many2one('work.order', 'No WO', readonly=1)
    equipment_id = fields.Char('Unit Code', readonly=1)
    requestor = fields.Char(readonly=1)
    qty_cm = fields.Float('Qty Cargo')
    remarks = fields.Char()
    qty_receive_done = fields.Boolean(compute='_compute_qty_done', store=1)

