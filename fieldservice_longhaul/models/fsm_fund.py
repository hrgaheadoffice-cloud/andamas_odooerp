from odoo import models, fields

class FSMFund(models.Model):
    _name = 'fieldservice_custom.fund'
    _description = 'Fund'

    name = fields.Char(string='Fund Name', required=True)
    amount = fields.Float(string='Amount')
