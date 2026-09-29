# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError, AccessError


class AccountPaymentRegisterBisa(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payments(self):
        self.ensure_one()
        batches = self._get_batches()

        to_reconcile = []
        if self.can_edit_wizard and (len(batches[0]['lines']) == 1 or self.group_payment):
            payment_vals = self._create_payment_vals_from_wizard()
            payment_vals_list = [payment_vals]
            to_reconcile.append(batches[0]['lines'])
        else:
            # Don't group payments: Create one batch per move.
            if not self.group_payment:
                new_batches = []
                for batch_result in batches:
                    for line in batch_result['lines']:
                        new_batches.append({
                            **batch_result,
                            'lines': line,
                        })
                batches = new_batches

            payment_vals_list = []
            for batch_result in batches:
                payment_vals_list.append(self._create_payment_vals_from_batch(batch_result))
                to_reconcile.append(batch_result['lines'])

        payments = self.env['account.payment'].create(payment_vals_list)
        #raise UserError(_(week[skrg.weekday()]))
        if payments.payment_type == 'outbound':
           payments.state = "2confirm"
           domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]

           for recon in self.line_ids.filtered_domain(domain):
               recons = self.env['tbl_payment_reconcile']
               recons.create({ 
                        'details': payments.id,
                        'move_line': recon.id,
                    })
               recon.move_id.status_tukar_faktur="done"

        else:
           payments.action_post()
           domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
           for payment, lines in zip(payments, to_reconcile):
              payment_lines = payment.line_ids.filtered_domain(domain)
              for account in payment_lines.account_id:
                  (payment_lines + lines)\
                      .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
                      .reconcile()
           #payments.state = "posted"
        return payments

