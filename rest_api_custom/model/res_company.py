from odoo import api, fields, models


class Company(models.Model):
    _inherit = 'res.company'

    code = fields.Char()
