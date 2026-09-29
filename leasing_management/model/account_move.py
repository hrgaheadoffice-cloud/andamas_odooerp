# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import api, fields, models, _

class AccountMoveleasing(models.Model):
    _inherit = 'account.move'

    lm_journal_voucher_id = fields.Many2one('lm.journal.voucher',string='Leasing Journal Voucher',index=True,ondelete='restrict')

class AccountMoveLineLM(models.Model):
    _inherit = 'account.move.line'

    lm_journal_voucher_ids = fields.Many2one('lm.journal.voucher.line', string='Leasing Journal Voucher Line',index=True,ondelete='restrict')