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

    cashrequest_id = fields.Many2one('cash.request',string='Cash Request',index=True,ondelete='restrict')

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    cashrequest_ids = fields.Many2one('cash.request.line', string='Cash Request Line',index=True,ondelete='restrict')

class AccountAccount(models.Model):
    _inherit = "account.account"