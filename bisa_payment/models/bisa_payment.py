# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class Bisapayment(models.Model):
    _inherit = 'account.payment'

    is_sundry = fields.Boolean('Sundry')
    sundry_account_id = fields.Many2one('account.account', string='Sundry Account', help="The sundry account.")
    is_multi = fields.Boolean('Multi')
    multi_account_id = fields.Many2one('account.account', string='Multi Account', help="The Multi account.")
    is_sundry_multi = fields.Boolean('Multi Account')
    sundry_multi_id = fields.One2many('tbl_sundry_multi', 'sundry_multi_ids', 'Multi Account')
    manual_currency_rate_active = fields.Boolean('Apply Manual Exchange')
    total_sundry = fields.Float('Total Sundry', compute='_compute_sundry')

    @api.depends('sundry_multi_id.amount')
    def _compute_sundry(self):
        """
        Compute the amounts of the Kurs.
        """
        if self.sundry_multi_id:
            for sund in self.sundry_multi_id:
                self.total_sundry += sund.amount
        else:
            self.total_sundry = 0.0

    @api.model
    # def create(self, values):
    #     if values['is_sundry_multi']:
    #         if values['total_sundry'] != values['amount']:
    #             raise UserError('Total Sundry tidak boleh berbeda dengan Amount')
    #     return super(Bisapayment, self).create(values)
    def create(self, values):
        if 'is_sundry_multi' in values:
            if values['is_sundry_multi']:
                if values['total_sundry'] != values['amount']:
                    raise UserError('Total Sundry tidak boleh berbeda dengan Amount')
        return super(Bisapayment, self).create(values)

    @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer', 'is_sundry', 'sundry_account_id')
    def _compute_destination_account_id(self):
        self.destination_account_id = False
        for pay in self:

            if pay.is_internal_transfer:
                pay.destination_account_id = pay.journal_id.company_id.transfer_account_id
            elif pay.partner_type == 'customer':
                # Receive money from invoice or send money to refund it.
                if pay.partner_id:
                    pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_receivable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        ('company_id', '=', pay.company_id.id),
                        ('internal_type', '=', 'receivable'),
                    ], limit=1)
            elif pay.partner_type == 'supplier':
                # Send money to pay a bill or receive money to refund it.
                if pay.partner_id:
                    pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_payable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        ('company_id', '=', pay.company_id.id),
                        ('internal_type', '=', 'payable'),
                    ], limit=1)
            if pay.is_sundry:
                pay.destination_account_id = pay.sundry_account_id.id



    def _seek_for_lines(self):
        ''' Helper used to dispatch the journal items between:
        - The lines using the temporary liquidity account.
        - The lines using the counterpart account.
        - The lines being the write-off lines.
        :return: (liquidity_lines, counterpart_lines, writeoff_lines)
        '''
        self.ensure_one()

        liquidity_lines = self.env['account.move.line']
        counterpart_lines = self.env['account.move.line']
        writeoff_lines = self.env['account.move.line']

        for line in self.move_id.line_ids:
            if line.account_id in (self.journal_id.payment_debit_account_id, self.journal_id.payment_credit_account_id):
                liquidity_lines += line
            elif line.account_id.internal_type != 'liquidity' or line.partner_id == line.company_id.partner_id:
                counterpart_lines += line
            else:
                writeoff_lines += line

        return liquidity_lines, counterpart_lines, writeoff_lines


    def _synchronize_from_moves(self, changed_fields):
        ''' Update the account.payment regarding its related account.move.
        Also, check both models are still consistent.
        :param changed_fields: A set containing all modified fields on account.move.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):

            # After the migration to 14.0, the journal entry could be shared between the account.payment and the
            # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
            if pay.move_id.statement_line_id:
                continue

            move = pay.move_id
            move_vals_to_write = {}
            payment_vals_to_write = {}

            if 'journal_id' in changed_fields:
                if pay.journal_id.type not in ('bank', 'cash'):
                    raise UserError(_("A payment must always belongs to a bank or cash journal."))

            if 'line_ids' in changed_fields:
                all_lines = move.line_ids
                liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                if not pay.is_sundry and not pay.is_sundry_multi:

                    if len(liquidity_lines) != 1 or len(counterpart_lines) != 1:
                        raise UserError(_(
                            "The journal entry %s reached an invalid state relative to its payment.\n"
                            "To be consistent, the journal entry must always contains:\n"
                            "- one journal item involving the outstanding payment/receipts account.\n"
                            "- one journal item involving a receivable/payable account.\n"
                            "- optional journal items, all sharing the same account.\n\n"
                        ) % move.display_name)

                    if writeoff_lines and len(writeoff_lines.account_id) != 1:
                        raise UserError(_(
                            "The journal entry %s reached an invalid state relative to its payment.\n"
                            "To be consistent, all the write-off journal items must share the same account."
                        ) % move.display_name)

                    if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                        raise UserError(_(
                            "The journal entry %s reached an invalid state relative to its payment.\n"
                            "To be consistent, the journal items must share the same currency."
                        ) % move.display_name)

                    if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
                        raise UserError(_(
                            "The journal entry %s reached an invalid state relative to its payment.\n"
                            "To be consistent, the journal items must share the same partner."
                        ) % move.display_name)

                    if not pay.is_internal_transfer:
                        if counterpart_lines.account_id.user_type_id.type == 'receivable':
                            payment_vals_to_write['partner_type'] = 'customer'
                        else:
                            payment_vals_to_write['partner_type'] = 'supplier'

                    liquidity_amount = liquidity_lines.amount_currency

                    move_vals_to_write.update({
                        'currency_id': liquidity_lines.currency_id.id,
                        'partner_id': liquidity_lines.partner_id.id,
                    })
                    payment_vals_to_write.update({
                        'amount': abs(liquidity_amount),
                        'currency_id': liquidity_lines.currency_id.id,
                        'destination_account_id': counterpart_lines.account_id.id,
                        'partner_id': liquidity_lines.partner_id.id,
                    })
                    if liquidity_amount > 0.0:
                        payment_vals_to_write.update({'payment_type': 'inbound'})
                    elif liquidity_amount < 0.0:
                        payment_vals_to_write.update({'payment_type': 'outbound'})

            move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
            pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))

    @api.model
    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            # if all the invoices selected share the same currency, record the paiement in that currency too
            invoice_currency = self.invoice_ids[0].currency_id
        if self.manual_currency_rate_active:
            if self.manual_currency_rate == 0.0:
                raise Warning(_('Exchange Rate not 0.0'))
            else:
                debit, credit, amount_currency, currency_id = aml_obj.with_context(
                    date=self.payment_date).compute_amount_fields_custom(self, amount, self.currency_id,
                                                                         self.company_id.currency_id, invoice_currency)
                # raise Warning(_(amount_currency))
        else:
            debit, credit, amount_currency, currency_id = aml_obj.with_context(
                date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
            # debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
        move = self.env['account.move'].create(self._get_move_vals())

        # Write line corresponding to invoice payment

        if self.is_sundry:
            account_move_line_obj = self.env['account.move.line']
            self.destination_account_id = self.env.sundry_account_id

            if self.sundry_multi_id:
                if self.payment_type == 'inbound':
                    data4 = aml_obj.create({
                        'name': self.name,
                        'date': self.payment_date,
                        'journal_id': self.journal_id.id,
                        'account_id': self.journal_id.default_debit_account_id.id,
                        'move_id': move.id,
                        'date_maturity': self.payment_date,
                        'debit': self.amount,
                        'partner_id': self.payment_type in ('inbound', 'outbound') and self.env[
                            'res.partner']._find_accounting_partner(self.partner_id).id or False,
                        'amount_currency': amount_currency or False,
                        'payment_id': self.id,

                    })

                    for sund in self.sundry_multi_id:
                        if sund.amount < 0:
                            data5 = aml_obj.create({
                                'name': self.name,
                                'date': self.payment_date,
                                'journal_id': self.journal_id.id,
                                'account_id': sund.sundry_account_id.id,
                                'analytic_account_id': sund.analytic_id.id,
                                'cost_center_id': sund.cost_center_id.id,
                                'move_id': move.id,
                                'date_maturity': self.payment_date,
                                'debit': sund.amount * -1,
                                'partner_id': self.payment_type in ('inbound', 'outbound') and self.env[
                                    'res.partner']._find_accounting_partner(self.partner_id).id or False,
                                'amount_currency': amount_currency or False,
                                'payment_id': self.id,
                            })

                        else:
                            data5 = aml_obj.create({
                                'name': self.name,
                                'date': self.payment_date,
                                'journal_id': self.journal_id.id,
                                'account_id': sund.sundry_account_id.id,
                                'analytic_account_id': sund.analytic_id.id,
                                'cost_center_id': sund.cost_center_id.id,
                                'move_id': move.id,
                                'date_maturity': self.payment_date,
                                'credit': sund.amount,
                                'partner_id': self.payment_type in ('inbound', 'outbound') and self.env[
                                    'res.partner']._find_accounting_partner(self.partner_id).id or False,
                                'amount_currency': amount_currency or False,
                                'payment_id': self.id,
                            })

                if self.payment_type == 'outbound':
                    data4 = aml_obj.create({
                        'name': self.name,
                        'date': self.payment_date,
                        'journal_id': self.journal_id.id,
                        'account_id': self.journal_id.default_debit_account_id.id,
                        'move_id': move.id,
                        'date_maturity': self.payment_date,
                        'credit': self.amount,
                        'partner_id': self.payment_type in ('inbound', 'outbound') and self.env[
                            'res.partner']._find_accounting_partner(self.partner_id).id or False,
                        # 'amount_currency': amount_currency or False,
                        'payment_id': self.id,

                    })

                    for sund in self.sundry_multi_id:
                        if sund.amount < 0:
                            data5 = aml_obj.create({
                                'name': self.name,
                                'date': self.payment_date,
                                'journal_id': self.journal_id.id,
                                'account_id': sund.sundry_account_id.id,
                                'analytic_account_id': sund.analytic_id.id,
                                'cost_center_id': sund.cost_center_id.id,
                                'move_id': move.id,
                                'date_maturity': self.payment_date,
                                'credit': sund.amount * -1,
                                'partner_id': self.payment_type in ('inbound', 'outbound') and self.env[
                                    'res.partner']._find_accounting_partner(self.partner_id).id or False,
                                # 'amount_currency': amount_currency or False,
                                'payment_id': self.id,

                            })
                        else:
                            data5 = aml_obj.create({
                                'name': self.name,
                                'date': self.payment_date,
                                'journal_id': self.journal_id.id,
                                'account_id': sund.sundry_account_id.id,
                                'analytic_account_id': sund.analytic_id.id,
                                'cost_center_id': sund.cost_center_id.id,
                                'move_id': move.id,
                                'date_maturity': self.payment_date,
                                'debit': sund.amount,
                                'partner_id': self.payment_type in ('inbound', 'outbound') and self.env[
                                    'res.partner']._find_accounting_partner(self.partner_id).id or False,
                                # 'amount_currency': amount_currency or False,
                                'payment_id': self.id,

                            })

            else:
                if self.payment_type == 'inbound':
                    data4 = aml_obj.create({
                        'name': self.name,
                        'date': self.payment_date,
                        'journal_id': self.journal_id.id,
                        'account_id': self.journal_id.default_debit_account_id.id,
                        'move_id': move.id,
                        'date_maturity': self.payment_date,
                        'debit': self.amount,
                        'partner_id': self.payment_type in ('inbound', 'outbound') and self.env[
                            'res.partner']._find_accounting_partner(self.partner_id).id or False,
                        'amount_currency': amount_currency or False,
                        'payment_id': self.id,

                    })

                if self.payment_type == 'outbound':
                    data4 = aml_obj.create({
                        'name': self.name,
                        'date': self.payment_date,
                        'journal_id': self.journal_id.id,
                        'account_id': self.journal_id.default_debit_account_id.id,
                        'move_id': move.id,
                        'date_maturity': self.payment_date,
                        'credit': self.amount,
                        'partner_id': self.payment_type in ('inbound', 'outbound') and
                                      self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
                        # 'amount_currency': amount_currency or False,
                        'payment_id': self.id,

                    })

                counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
                counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
                counterpart_aml_dict.update({'currency_id': currency_id})
                counterpart_aml = aml_obj.create(counterpart_aml_dict)

        else:

            counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
            counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
            counterpart_aml_dict.update({'currency_id': currency_id})
            counterpart_aml = aml_obj.create(counterpart_aml_dict)

        if not self.is_sundry:
            # Reconcile with the invoices
            if self.payment_difference_handling == 'reconcile' and self.payment_difference:
                writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
                amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(
                    self.payment_difference, self.currency_id, self.company_id.currency_id)[2:]
                # the writeoff debit and credit must be computed from the invoice residual in company currency
                # minus the payment amount in company currency, and not from the payment difference in the payment currency
                # to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
                total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
                total_payment_company_signed = self.currency_id.with_context(date=self.payment_date).compute(
                    self.amount, self.company_id.currency_id)
                if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
                    amount_wo = total_payment_company_signed - total_residual_company_signed
                else:
                    amount_wo = total_residual_company_signed - total_payment_company_signed
                debit_wo = amount_wo > 0 and amount_wo or 0.0
                credit_wo = amount_wo < 0 and -amount_wo or 0.0
                writeoff_line['name'] = _('Counterpart')
                writeoff_line['account_id'] = self.writeoff_account_id.id
                writeoff_line['debit'] = debit_wo
                writeoff_line['credit'] = credit_wo
                writeoff_line['amount_currency'] = amount_currency_wo
                writeoff_line['currency_id'] = currency_id
                writeoff_line = aml_obj.create(writeoff_line)
                if counterpart_aml['debit']:
                    counterpart_aml['debit'] += credit_wo - debit_wo
                if counterpart_aml['credit']:
                    counterpart_aml['credit'] += debit_wo - credit_wo
                counterpart_aml['amount_currency'] -= amount_currency_wo

            self.invoice_ids.register_payment(counterpart_aml)

            # Write counterpart lines
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0
            liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
            aml_obj.create(liquidity_aml_dict)

        move.post()

        if self.is_advance:
            if not self.adv_account_id:
                raise UserError(_("Account Advance Belum Diisi"))

        if self.is_sundry:
            if self.is_sundry_multi:
                if self.total_sundry != self.amount:
                    # raise UserError(_(self.total_sundry))
                    raise UserError(_("Total Amount Multi Account Sundry\n TIDAK SAMA\n dengan amount pembayaran"))

            else:
                if not self.sundry_account_id:
                    raise UserError(_("Account Sundry Belum Diisi"))

        return move

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}

        if not self.journal_id.payment_debit_account_id or not self.journal_id.payment_credit_account_id:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set on the %s journal.",
                self.journal_id.display_name))

        # Compute amounts.
        write_off_amount_currency = write_off_line_vals.get('amount', 0.0)

        if self.payment_type == 'inbound':
            # Receive money.
            liquidity_amount_currency = self.amount
        elif self.payment_type == 'outbound':
            # Send money.
            liquidity_amount_currency = -self.amount
            write_off_amount_currency *= -1
        else:
            liquidity_amount_currency = write_off_amount_currency = 0.0

        write_off_balance = self.currency_id._convert(
            write_off_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        liquidity_balance = self.currency_id._convert(
            liquidity_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
        counterpart_balance = -liquidity_balance - write_off_balance
        currency_id = self.currency_id.id

        if self.is_internal_transfer:
            if self.payment_type == 'inbound':
                liquidity_line_name = _('Transfer to %s', self.journal_id.name)
            else: # payment.payment_type == 'outbound':
                liquidity_line_name = _('Transfer from %s', self.journal_id.name)
        else:
            liquidity_line_name = self.payment_reference

        # Compute a default label to set on the journal items.

        payment_display_name = self._prepare_payment_display_name()

        default_line_name = self.env['account.move.line']._get_default_line_name(
            _("Internal Transfer") if self.is_internal_transfer else payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
            self.amount,
            self.currency_id,
            self.date,
            partner=self.partner_id,
        )

        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name or default_line_name,
                'date_maturity': self.date,
                'amount_currency': liquidity_amount_currency,
                'currency_id': currency_id,
                'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.journal_id.payment_credit_account_id.id if liquidity_balance < 0.0 else self.journal_id.payment_debit_account_id.id,
            },
            # Receivable / Payable.
            {
                'name': self.payment_reference or default_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.destination_account_id.id,
            },
        ]

        if self.is_sundry_multi:
            line_vals_list = [
                # Liquidity line.
                {
                    'name': liquidity_line_name or default_line_name,
                    'date_maturity': self.date,
                    'amount_currency': liquidity_amount_currency,
                    'currency_id': currency_id,
                    'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                    'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': self.journal_id.payment_credit_account_id.id if liquidity_balance < 0.0 else self.journal_id.payment_debit_account_id.id,
                }
            ]

            if self.payment_type == 'outbound':
                for line in self.sundry_multi_id:
                    line_vals_list.append({
                        'name': liquidity_line_name or default_line_name,
                        'debit': line.amount,
                        'account_id': line.sundry_account_id.id,
                        'cost_center_id': line.cost_center_id.id,
                        'analytic_account_id': line.analytic_id.id,
                        'partner_id': self.partner_id.id
                    })

            elif self.payment_type == 'inbound':
                for line in self.sundry_multi_id:
                    line_vals_list.append({
                        'name': liquidity_line_name or default_line_name,
                        'credit': line.amount,
                        'account_id': line.sundry_account_id.id,
                        'cost_center_id': line.cost_center_id.id,
                        'analytic_account_id': line.analytic_id.id,
                        'partner_id': self.partner_id.id
                    })

        if not self.currency_id.is_zero(write_off_amount_currency):
            # Write-off line.
            line_vals_list.append({
                'name': write_off_line_vals.get('name') or default_line_name,
                'amount_currency': write_off_amount_currency,
                'currency_id': currency_id,
                'debit': write_off_balance if write_off_balance > 0.0 else 0.0,
                'credit': -write_off_balance if write_off_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': write_off_line_vals.get('account_id'),
            })
        return line_vals_list


class tbl_sundry_multi(models.Model):
    _name = 'tbl_sundry_multi'

    sundry_multi_ids = fields.Many2one('account.payment', 'Multi Account')
    sundry_account_id = fields.Many2one('account.account', string="Sundry Account",
                                            domain=[('deprecated', '=', False)], copy=False, required=True)
    cost_center_id = fields.Many2one(
            'account.cost.center',
            string='Cost Center',
            index=True)
    analytic_id = fields.Many2one('account.analytic.account', string='Budget Code')
    amount = fields.Float("Amount")



               





