from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    parent_id = fields.Many2one('hr.employee', 'Supervisor', compute="_compute_parent_id", store=True, readonly=False,
                                domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    coach_id = fields.Many2one(
        'hr.employee', 'Manager', compute='_compute_coach', store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help='Select the "Employee" who is the coach of this employee.\n'
             'The "Coach" has no specific rights or responsibilities by default.')
