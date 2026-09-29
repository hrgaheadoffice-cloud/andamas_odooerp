from odoo import api, fields, models


class InventoryCalculation(models.Model):
    _name = 'inventory.calculation'
    _rec_name = 'id'

    date = fields.Date()
    begin_qty = fields.Float('Beginning Quantity')
    begin_val = fields.Float('Beginning Value')
    begin_avg_val = fields.Float()
    quantity = fields.Float('Quantity In')
    value = fields.Float('Value In')
    avail_qty = fields.Float('Avail Quantity', compute='_compute_vals')
    avail_val = fields.Float('Avail Value', compute='_compute_vals')
    average_value = fields.Float()
    sales_qty = fields.Float('Sales Quantity')
    sales_val = fields.Float('Sales Value')
    close_qty = fields.Float('Ending Quantity', compute='_compute_vals')
    close_val = fields.Float('Ending Value', compute='_compute_vals')

    def _compute_vals(self):
        for me in self:
            me.avail_qty = me.begin_qty + me.quantity
            me.avail_val = me.begin_val + me.value
            me.close_qty = me.begin_qty + me.quantity - me.sales_qty
            me.close_val = me.begin_val + me.value - me.sales_val

