from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    known_by = fields.Boolean()
    checked_by = fields.Boolean()

