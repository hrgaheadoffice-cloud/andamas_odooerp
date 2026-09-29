from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    noi_id = fields.Many2one('noi',string='NOI',index=True,ondelete='restrict')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    noi_ids = fields.Many2one('noi.line', string='NOI Line',index=True,ondelete='restrict')
