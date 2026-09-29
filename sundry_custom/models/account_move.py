from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    sundry_id = fields.Many2one('sundry',string='Sundry',index=True,ondelete='restrict')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sundry_ids = fields.Many2one('sundry.line', string='Sundry Line',index=True,ondelete='restrict')
