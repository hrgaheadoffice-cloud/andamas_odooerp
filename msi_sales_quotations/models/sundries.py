# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models

import math


class msi_account_payment(models.Model):
    _inherit = 'account.payment'

    departemen = fields.Many2one('account.analytic.tag', 'Departemen')
    is_advance = fields.Boolean('Transaksi Advance')
    adv_settlement_id = fields.Many2one('tbl_msi_acc_settlement', 'Advance')
    status_nomor = fields.Char('Status Penomoran', default='draft')
    penomoran = fields.Char('Nomor', readonly=True)
    adv_account_id = fields.Many2one('account.account', string="Account", domain=[('deprecated', '=', False)],
                                     copy=False)
    is_sundry = fields.Boolean('Is Sundry')
    sundry_account_id = fields.Many2one('account.account', string="Sundry Account", domain=[('deprecated', '=', False)],
                                        copy=False)
    is_sundry_multi = fields.Boolean('Multi Account')
    sundry_multi_id = fields.One2many('tbl_sundry_multi', 'sundry_multi_ids', 'Multi Account')
    total_sundry = fields.Float('Total Sundry', compute='_compute_sundry')

    terbilang = fields.Char(string="Terbilang :", compute="_compute_terbilang", required=False)
    manual_currency_rate_active = fields.Boolean('Apply Manual Exchange')
    manual_currency_rate = fields.Float('Rate', digits=(12, 20), compute='_compute_kurs', store=True)
    manual_rate = fields.Float('Kurs', digits=(12, 2), default=0)

    @api.depends('sundry_multi_id.amount')
    def _compute_sundry(self):
        """
        Compute the amounts of the Kurs.
        """
        if self.sundry_multi_id:
            for sund in self.sundry_multi_id:
                self.total_sundry += sund.amount

    @api.depends('manual_rate')
    def _compute_kurs(self):
        """
        Compute the amounts of the Kurs.
        """
        for record in self:
            if record.manual_rate == 0:
                record.manual_currency_rate = 0
            else:
                record.manual_currency_rate = 1 / record.manual_rate

    @api.model
    def default_get(self, fields):
        rec = super(msi_account_payment, self).default_get(fields)
        invoice_defaults = rec.get('invoice_ids')
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            # rec['manual_currency_rate_active'] = invoice['manual_currency_rate_active']
            # rec['manual_rate'] = invoice['manual_rate']
        return rec

    @api.model
    def create(self, vals):
        res = super(msi_account_payment, self).create(vals)
        company_id = self.env['res.company']._company_default_get('account.payment')
        if res.manual_currency_rate_active:
            if res.manual_currency_rate == 0.0:
                raise Warning(_('Exchange Rate Field is required , please fill that.'))
            if res.currency_id == company_id.currency_id:
                raise Warning(
                    _('Company currency and invoice currency same, You can not added manual Exchange rate in same currency.'))
        return res

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

    def _write(self, values):
        res = super(msi_account_payment, self)._write(values)
        company_id = self.env['res.company']._company_default_get('account.payment')
        for i in self:
            if i.manual_currency_rate_active:
                if i.manual_currency_rate == 0.0:
                    raise Warning(_('Exchange Rate Field is required , please fill that.'))
                if i.currency_id == company_id.currency_id:
                    raise Warning(
                        _('Company currency and invoice currency same, You can not added manual Exchange rate in same currency.'))
            if i.is_sundry == True and i.is_sundry_multi == True:
                if i.total_sundry != i.amount:
                    raise UserError(_('Total Sundry Berbeda dengan Amount'))

        return res

    def _create_transfer_entry(self, amount):
        """ Create the journal entry corresponding to the 'incoming money' part of an internal transfer, return the reconciliable move line
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)

        if self.manual_currency_rate_active:
            if self.manual_currency_rate == 0.0:
                raise Warning(_('Exchange Rate not 0.0'))
            else:
                debit, credit, amount_currency, dummy = aml_obj.with_context(
                    date=self.payment_date).compute_amount_fields_custom(self, amount, self.currency_id,
                                                                         self.company_id.currency_id)
        else:
            debit, credit, amount_currency, dummy = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(
                amount, self.currency_id, self.company_id.currency_id)

        amount_currency = self.destination_journal_id.currency_id and self.currency_id.with_context(
            date=self.payment_date).compute(amount, self.destination_journal_id.currency_id) or 0

        dst_move = self.env['account.move'].create(self._get_move_vals(self.destination_journal_id))

        dst_liquidity_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, dst_move.id)
        dst_liquidity_aml_dict.update({
            'name': _('Transfer from %s') % self.journal_id.name,
            'account_id': self.destination_journal_id.default_credit_account_id.id,
            'currency_id': self.destination_journal_id.currency_id.id,
            'payment_id': self.id,
            'journal_id': self.destination_journal_id.id})
        aml_obj.create(dst_liquidity_aml_dict)

        transfer_debit_aml_dict = self._get_shared_move_line_vals(credit, debit, 0, dst_move.id)
        transfer_debit_aml_dict.update({
            'name': self.name,
            'payment_id': self.id,
            'account_id': self.company_id.transfer_account_id.id,
            'journal_id': self.destination_journal_id.id})
        if self.currency_id != self.company_id.currency_id:
            transfer_debit_aml_dict.update({
                'currency_id': self.currency_id.id,
                'amount_currency': -self.amount,
            })
        transfer_debit_aml = aml_obj.create(transfer_debit_aml_dict)
        dst_move.post()
        return transfer_debit_aml

    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id', 'manual_currency_rate')
    def _compute_payment_difference(self):
        if len(self.invoice_ids) == 0:
            return
        if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
            self.payment_difference = self.amount - self._compute_total_invoices_amount()
        else:
            self.payment_difference = self._compute_total_invoices_amount() - self.amount

    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        if self.invoice_ids:
            self.destination_account_id = self.invoice_ids[0].account_id.id
        elif self.payment_type == 'transfer':
            if not self.company_id.transfer_account_id.id:
                raise UserError(
                    _('There is no Transfer Account defined in the accounting settings. Please define one to be able to confirm this transfer.'))
            self.destination_account_id = self.company_id.transfer_account_id.id
        elif self.partner_id:
            if self.partner_type == 'customer':
                self.destination_account_id = self.partner_id.property_account_receivable_id.id
            else:
                self.destination_account_id = self.partner_id.property_account_payable_id.id
        elif self.partner_type == 'customer':
            default_account = self.env['ir.property'].search([
                ('name', '=', 'property_account_receivable_id'),
                ('res_id', '=', 'res.partner'),
            ], limit=1)
            self.destination_account_id = default_account.value_reference.id if default_account else False
        elif self.partner_type == 'supplier':
            default_account = self.env['ir.property'].search([
                ('name', '=', 'property_account_payable_id'),
                ('res_id', '=', 'res.partner'),
            ], limit=1)
            self.destination_account_id = default_account.value_reference.id if default_account else False

        if self.is_advance:
            self.destination_account_id = self.adv_account_id.id

        if self.is_sundry:
            self.destination_account_id = self.sundry_account_id.id

    def set_penomoran(self):
        bulan = self.payment_date.strftime("%m")
        tahun = self.payment_date.strftime("%y")
        cari = self.env['account.journal'].search([('id', '=', self.journal_id.id)], )
        if self.payment_type == 'inbound':
            self.penomoran = cari.code + '.IN/' + str(bulan) + str(tahun) + '/' + str(cari.sequence_int + 1)

        if self.payment_type == 'outbound':
            self.penomoran = cari.code + '.OUT/' + str(bulan) + str(tahun) + '/' + str(cari.sequence_int + 1)

        if self.payment_type == 'transfer':
            self.penomoran = cari.code + '.TRANSFER/' + str(bulan) + str(tahun) + '/' + str(cari.sequence_int + 1)

        cari.sequence_int = cari.sequence_int + 1

        self.status_nomor = 'done'

    @api.depends('amount')
    def _compute_terbilang(self):
        for r in self:
            if r.amount:
                r.terbilang = r.currency_id.milyar_juta_ribu(int(r.amount))

    def _get_counterpart_move_line_vals_new(self, invoice=False):
        if self.payment_type == 'transfer':
            name = self.name
        else:
            name = ''
            if self.partner_type == 'customer':
                if self.payment_type == 'inbound':
                    name += _("Customer Payment")
                elif self.payment_type == 'outbound':
                    name += _("Customer Credit Note")
            elif self.partner_type == 'supplier':
                if self.payment_type == 'inbound':
                    name += _("Vendor Credit Note")
                elif self.payment_type == 'outbound':
                    name += _("Vendor Payment")
            if invoice:
                name += ': '
                for inv in invoice:
                    if inv.move_id:
                        name += inv.number + ', '
                name = name[:len(name) - 2]
        return {
            'name': name,
            'account_id': self.destination_account_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }


class msi_account_journal(models.Model):
    _inherit = 'account.journal'

    sequence_int = fields.Integer(help='Used to order Journals in the dashboard view')


class MsiAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def compute_amount_fields_custom(self, obj, amount, src_currency, company_currency, invoice_currency=False):
        """ Helper function to compute value for fields debit/credit/amount_currency based on an amount and the currencies given in parameter"""
        amount_currency = False
        currency_id = False
        if src_currency and src_currency != company_currency:
            amount_currency = amount
            if obj.manual_currency_rate != 0:
                amount = amount_currency / obj.manual_currency_rate
            currency_id = src_currency.id
        debit = amount > 0 and amount or 0.0
        credit = amount < 0 and -amount or 0.0
        if invoice_currency and invoice_currency != company_currency and not amount_currency:
            amount_currency = amount / obj.manual_currency_rate
            currency_id = invoice_currency.id

        return debit, credit, amount_currency, currency_id


class account_abstract_payment(models.AbstractModel):
    _inherit = "account.abstract.payment"

    def _compute_total_invoices_amount(self):
        """ Compute the sum of the residual of invoices, expressed in the payment currency """
        payment_currency = self.currency_id or self.journal_id.currency_id or self.journal_id.company_id.currency_id
        invoices = self.env['account.invoice'].browse(self._context.get('active_ids'))
        if all(inv.currency_id == payment_currency for inv in invoices):
            total = sum(invoices.mapped('residual_signed'))
        else:
            if not self.manual_currency_rate_active:
                total = 0
                for inv in invoices:
                    if inv.company_currency_id != payment_currency:
                        total += inv.company_currency_id.with_context(date=self.payment_date).compute(
                            inv.residual_company_signed, payment_currency)
                    else:
                        total += inv.residual_company_signed
            else:
                total = 0
                for inv in invoices:
                    total += inv.residual * self.manual_currency_rate
        return abs(total)


class tbl_sundry_multi(models.Model):
    _name = 'tbl_sundry_multi'

    sundry_multi_ids = fields.Many2one('account.payment', 'Multi Account')
    sundry_account_id = fields.Many2one('account.account', string="Sundry Account", domain=[('deprecated', '=', False)],
                                        copy=False, required=True)
    cost_center_id = fields.Many2one(
        'account.cost.center',
        string='Cost Center',
        index=True)
    analytic_id = fields.Many2one('account.analytic.account', string='Budget Code')
    amount = fields.Float("Amount")
