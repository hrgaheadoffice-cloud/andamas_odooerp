from odoo import models, fields

class FSMDisciplinary(models.Model):
    _inherit = "fsm.root"

    name = fields.Char(string='Disciplinary Name', required=True)
    description = fields.Text(string='Description')
