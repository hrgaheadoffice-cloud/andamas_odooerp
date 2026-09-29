from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class FSMTopUp(models.Model):
    _name = 'fsm.top.up'

    created_by = fields.Many2one('res.users', 'Created by', default=lambda self: self.env.uid, readonly=1, store=1)
    date = fields.Datetime(string='Date & Time', default=fields.Datetime.now, store=True)
    approval = fields.Many2one('hr.employee')
    remaining_amount = fields.Float()
    remaining_amount_date = fields.Datetime()
    top_up_amount = fields.Float()
    total_transporter_cost = fields.Float()
    description = fields.Text()

