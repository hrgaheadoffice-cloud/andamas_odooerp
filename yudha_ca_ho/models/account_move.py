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

    ca_ho_id = fields.Many2one('cash.advance.ho',string='Cash Advance',index=True,ondelete='restrict')
    settelment_ho_id = fields.Many2one('settelment.ho',string='Settelement',index=True,ondelete='restrict')

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cadet_ho_id = fields.Many2one('cash.advance.holine', string='Cash Advance Line',index=True,ondelete='restrict')
    settelment_ho_id = fields.Many2one('settelment.holine',string='Settlement Line',index=True,ondelete='restrict')

class AccountAccount(models.Model):
    _inherit = "account.account"

