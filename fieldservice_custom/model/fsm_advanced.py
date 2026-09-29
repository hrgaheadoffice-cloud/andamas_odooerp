from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class FSMAdvanced(models.Model):
    _name = 'fsm.advanced'

    transporter_task_id = fields.Many2one('fsm.transporter.task', 'No. Transporter Task')
    nip = fields.Char('NIP', related='transporter_task_id.nip')
    driver_id = fields.Many2one('hr.employee', 'Driver Name', related='transporter_task_id.driver_id')
    equipment_id = fields.Many2one('master_asset_maintenance', 'Unit Code', related='transporter_task_id.equipment_id')

