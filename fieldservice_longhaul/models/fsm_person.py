from odoo import fields, models, api

class FsmPerson(models.Model):
    _inherit = "fsm.person"

    nip = fields.Char(string='NIP')
    unit_code = fields.Char(string='Unit Code')
    status_pegawai = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], string='Status Pegawai')
