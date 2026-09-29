from odoo import api, fields, models
from datetime import datetime


class PartCanibal(models.Model):

    _name = 'part.canibal'

    work_order_id = fields.Many2one(comodel_name="work.order", string="Work Order", required=False, )
    date_time = fields.Datetime('Date & Time',default=datetime.today())
    work_order_name = fields.Many2one('work.order', string="No. Work Order", store=True, domain="[('status', 'in', ('draft','open') )]")
    origin_unit_code = fields.Many2one('master_asset_maintenance', 'Origin Unit Code', related='work_order_name.equipment_id')
    part_name = fields.Many2one('product.template', string="Part Name", store=True)
    component = fields.Many2one('component', string="Component", store=True)
    mecanic = fields.Many2one('hr.employee', string="Mechanic", store=True, domain="[('job_id.name', 'in', ['Mechanic', 'Mechanic Assistant'])]")
    uom = fields.Many2one(string='UOM', related='part_name.uom_id')
    qty = fields.Float(string='Quantity')


