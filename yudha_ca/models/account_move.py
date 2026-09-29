# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    ca_id = fields.Many2one('cash.advance',string='Cash Advance',index=True,ondelete='restrict')
    settelment_id = fields.Many2one('settelment',string='Settelement',index=True,ondelete='restrict')

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cadet_id = fields.Many2one('cash.advance.line', string='Cash Advance Line',index=True,ondelete='restrict')
    settelment_id = fields.Many2one('settelment.line',string='Settlement Line',index=True,ondelete='restrict')

class AccountAccount(models.Model):
    _inherit = "account.account"

