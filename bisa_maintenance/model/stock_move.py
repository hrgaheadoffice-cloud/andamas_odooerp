from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    work_order_id = fields.Many2one(comodel_name="work.order", string="Work Order", required=False, )
    component = fields.Many2one('component')
    price = fields.Float()
    total_price = fields.Float()
    full_available = fields.Float(related="product_id.qty_available")
    coa = fields.Selection([
        ('backlog', 'Backlog'),
        ('stock', 'Stock'),
        ('part_service', 'Part Service'),
        ('lubrication', 'Lubrication'),
        ('tools', 'Tools'),
        ('wheel_tyre', 'Wheel & Tyre'),
        ('workshop', 'Workshop'),
        ('consumable', 'Consumable'),
    ], 'COA')
    equipment_id = fields.Many2one(related='work_order_id.equipment_id')
    hm_km = fields.Char(related='work_order_id.hm_km')
    part_number = fields.Char(related='product_id.default_code')
    is_wo_to_pr = fields.Boolean()

    @api.model_create_single
    def create(self, vals):
        if 'work_order_id' in vals:
            if vals['work_order_id']:
                work_order = self.env['work.order'].browse(vals['work_order_id'])
                vals['name'] = work_order.name
        return super(StockMove, self).create(vals)

    @api.onchange('product_uom_qty', 'price')
    def onchange_total(self):
        if not self.product_uom_qty or not self.price:
            return
        self.total_price = self.product_uom_qty * self.price
        return

    @api.onchange('product_id')
    def onchange_price(self):
        if not self.product_id:
            return
        self.price = self.product_id.standard_price
        return