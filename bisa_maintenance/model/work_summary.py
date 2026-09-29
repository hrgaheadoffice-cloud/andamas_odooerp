from odoo import api, fields, models
from datetime import datetime


class WorkSummary(models.Model):
    _name = "work.summary"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char('Reference No.')
    equipment_id = fields.Many2one('master_asset_maintenance', 'Unit Code', readonly='False')
    maintenance_type = fields.Selection(selection=[
        ('corrective', 'Unschedule'),
        ('preventive', 'Schedule'),
        ('accident', 'Accident')
    ], default='corrective')
    date = fields.Datetime(string='Date & Time BD', readonly=True, store=True)
    work_order_rfu = fields.Datetime('Date & Time RFU', readonly=1)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('cancel', 'Cancel')
    ], default='draft', string="Status")

    def action_submit(self):
        self.state = 'submit'

    def action_cancel(self):
        self.state = 'cancel'