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


    def unlink(self):
        self.write({'posted_before': False})
        # for alldata in self:
        #     account_partial_reconcile_ids = alldata.mapped(
        #         lambda x: (x.line_ids.matched_debit_ids + x.line_ids.matched_debit_ids))
        #     reconciled_moves = account_partial_reconcile_ids.credit_move_id.move_id + \
        #         account_partial_reconcile_ids.debit_move_id.move_id
        #     account_partial_reconcile_ids.unlink()
        #     for lines in alldata.line_ids:
        #         lines.analytic_line_ids.unlink()
        #     moves_to_unlink = reconciled_moves or alldata
        #     moves_to_unlink.button_draft()
        #     moves_to_unlink.unlink()
        return super(AccountMove,self).unlink()
