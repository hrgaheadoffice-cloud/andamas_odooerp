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

    reimbursement_ho_id = fields.Many2one('reimbursement.ho',string='Reimbursement',index=True,ondelete='restrict')

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    reimbursement_ho_ids = fields.Many2one('reimbursement.holine', string='Reimbursement Line',index=True,ondelete='restrict')

class AccountAccount(models.Model):
    _inherit = "account.account"