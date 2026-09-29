# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
class RegisterPaymentho(models.TransientModel):
    _name = 'register.payment.howiz'
    _description = 'Register Payment hoWizard'

    def _get_default_currency_id(self):
        return self.env.company.currency_id.id

    @api.depends('journal_id')
    def _compute_available_partner_bank_ids(self):
        for alldata in self:
            allbank = self.env['res.partner.bank'].sudo().search([])
            databank = []
            for mybank in allbank:
                myjournal = mybank.journal_id.filtered(lambda x: x.id == alldata.journal_id.id)
                if myjournal:
                    for alljurnal in myjournal:
                        databank.append(alljurnal.bank_account_id.id)
            if databank != []:
                caribank = self.env['res.partner.bank'].sudo().search([('id','in',databank)])
                alldata.available_partner_bank_ids = [(6,0,caribank.ids)]
            else:
                alldata.available_partner_bank_ids = False


    journal_id = fields.Many2one('account.journal',string='Journal', store=True, readonly=False,
        compute='_compute_journal_id',
        domain=lambda self: self._domain_very_important())

    def _domain_very_important(self):
        domain = []
        context = dict(self.env.context or {})
        if context.get('active_model') == 'cash.advance.ho':
            domain = [('company_id', '=', self.env.company.id), ('type', 'in', ('bank', 'cash'))]
        if context.get('active_model') == 'settelment.ho':
            settlement_id = self.env['settelment.ho'].search([('id', '=', context.get('active_id'))])
            if settlement_id.over_due == 0:
                journal_id = settlement_id.journal_id
                domain = [('company_id', '=', self.env.company.id), ('id', '=', journal_id.id)]
            else:
                domain = [('company_id', '=', self.env.company.id), ('type', 'in', ('bank', 'cash'))]
        return domain

    available_partner_bank_ids = fields.Many2many(
        comodel_name='res.partner.bank',
        compute='_compute_available_partner_bank_ids',
        store=False
    )
    partner_bank_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string="Recipient Bank Account",
        readonly=False,
        domain="[('id', 'in', available_partner_bank_ids)]",
    )
    amount = fields.Float(digits='Account',string='Amount', tracking=5)
    currency_id = fields.Many2one('res.currency', 'Currency', default=_get_default_currency_id, required=True)
    company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.company)
    payment_date = fields.Date('Payment Date')
    communication = fields.Text('Memo')
    ca_ho_id = fields.Many2one('cash.advance.ho',string='CA ID')
    settelment_ho_id = fields.Many2one('settelment.ho',string='Settelement')
    line_ids = fields.Many2many('account.move.line', 'register_payment_howiz_move_line_rel', 'wizard_id',
        string="Journal items", readonly=True, copy=False,)
    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money'),
    ], string='Payment Type', copy=False)
    partner_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Vendor'),
    ], store=True, copy=False)
    partner_id = fields.Many2one('res.partner',
        string="Customer/Vendor", copy=False, ondelete='restrict')
    payment_difference = fields.Monetary(
        compute='_compute_payment_difference')
    payment_difference_handling = fields.Selection([
        ('open', 'Keep open'),
        ('reconcile', 'Mark as fully paid'),
    ], default='open', string="Payment Difference Handling")

    @api.depends('amount','ca_ho_id','settelment_ho_id')
    def _compute_payment_difference(self):
        for wizard in self:
            if wizard.ca_ho_id and not wizard.settelment_ho_id:
                wizard.payment_difference = 0
            else:
                wizard.payment_difference =  wizard.settelment_ho_id.over_due


    @api.depends('company_id')
    def _compute_journal_id(self):
        for wizard in self:
                wizard.journal_id = self.env['account.journal'].search([
                    ('type', 'in', ('bank', 'cash')),
                    ('company_id', '=', wizard.company_id.id),
                ], limit=1)

    @api.model
    def default_get(self, default_fields):
        res = super(RegisterPaymentho, self).default_get(default_fields)
        mymodel =  self._context.get('active_model')
        activeid =  self._context.get('active_ids')
        if mymodel == 'cash.advance.ho':
            myca = self.env['cash.advance.ho'].sudo().browse(activeid)
            res['ca_ho_id'] = myca.id
            res['amount'] = myca.amount_ca
            res['payment_type'] = 'outbound'
            res['partner_type'] = 'customer'
            res['payment_difference_handling'] = 'open'
            res['communication'] = myca.name
        elif mymodel == 'settelment.ho':
            mysettel = self.env['settelment.ho'].sudo().browse(activeid)
            res['settelment_ho_id'] = activeid
            res['payment_type'] = 'outbound'
            res['partner_type'] = 'customer'
            res['payment_difference_handling'] = 'open'
            res['amount'] =mysettel.over_due
            res['communication'] = mysettel.name
        return res

    def _post_payments(self, to_process, edit_mode=False):
        payments = self.env['account.payment']
        for vals in to_process:
            payments |= vals['payment']
        payments.action_post()

    def _reconcile_payments(self, to_process, edit_mode=False):
        domain = [
            ('parent_state', '=', 'posted'),
            ('account_internal_type', 'in', ('receivable', 'payable')),
            ('reconciled', '=', False),
        ]
        for vals in to_process:
            payment_lines = vals['payment'].line_ids.filtered_domain(domain)
            lines = vals['to_reconcile']

            for account in payment_lines.account_id:
                (payment_lines + lines)\
                    .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
                    .reconcile()
    @api.model
    def _get_line_batch_key(self, line):
        move = line.move_id
        partner_bank_account = self.env['res.partner.bank']
        if move.is_invoice(include_receipts=True):
            partner_bank_account = move.partner_bank_id._origin
        if self.ca_ho_id:
            return {
                'partner_id': line.partner_id.id,
                'account_id': line.account_id.id,
                'currency_id': line.currency_id.id,
                'ca_ho_id': self.ca_ho_id.id,
                'partner_bank_id': partner_bank_account.id,
                'partner_type': 'supplier',
                'payment_type': 'inbound' if line.balance > 0.0 else 'outbound',
            }
        else:
            return {
                'partner_id': line.partner_id.id,
                'account_id': line.account_id.id,
                'currency_id': line.currency_id.id,
                'ca_ho_id': self.ca_ho_id.id,
                'partner_bank_id': partner_bank_account.id,
                'partner_type': 'customer' if line.account_internal_type == 'receivable' else 'supplier',
                'payment_type': 'inbound' if line.balance > 0.0 else 'outbound',
            }

    def _get_batches(self):
        self.ensure_one()

        lines = self.line_ids._origin

        if len(lines.company_id) > 1:
            raise UserError(_("You can't create payments for entries belonging to different companies."))
        if not lines:
            raise UserError(_("You can't open the register payment wizard without at least one receivable/payable line."))

        batches = {}
        for line in lines:
            batch_key = self._get_line_batch_key(line)

            serialized_key = '-'.join(str(v) for v in batch_key.values())
            batches.setdefault(serialized_key, {
                'key_values': batch_key,
                'lines': self.env['account.move.line'],
            })
            batches[serialized_key]['lines'] += line

        return list(batches.values())

    def _init_payments(self, to_process, edit_mode=False):
        payments = self.env['account.payment'].create([x['create_vals'] for x in to_process])
        for payment, vals in zip(payments, to_process):
            vals['payment'] = payment
            if edit_mode:
                lines = vals['to_reconcile']
                if payment.currency_id != lines.currency_id:
                    liquidity_lines, counterpart_lines, writeoff_lines = payment._seek_for_lines()
                    source_balance = abs(sum(lines.mapped('amount_residual')))
                    if liquidity_lines[0].balance:
                        payment_rate = liquidity_lines[0].amount_currency / liquidity_lines[0].balance
                    else:
                        payment_rate = 0.0
                    source_balance_converted = abs(source_balance) * payment_rate
                    payment_balance = abs(sum(counterpart_lines.mapped('balance')))
                    payment_amount_currency = abs(sum(counterpart_lines.mapped('amount_currency')))
                    if not payment.currency_id.is_zero(source_balance_converted - payment_amount_currency):
                        continue
                    delta_balance = source_balance - payment_balance
                    if self.company_currency_id.is_zero(delta_balance):
                        continue
                    debit_lines = (liquidity_lines + counterpart_lines).filtered('debit')
                    credit_lines = (liquidity_lines + counterpart_lines).filtered('credit')

                    if debit_lines and credit_lines:
                        payment.move_id.write({'line_ids': [
                            (1, debit_lines[0].id, {'debit': debit_lines[0].debit + delta_balance}),
                            (1, credit_lines[0].id, {'credit': credit_lines[0].credit + delta_balance}),
                        ]})
        return payments
    def _create_payment_vals_from_wizard(self):
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'destination_account_id': self.line_ids[0].account_id.id
        }

        if not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == 'reconcile':
            payment_vals['write_off_line_vals'] = {
                'name': self.writeoff_label,
                'amount': self.payment_difference,
                'account_id': self.writeoff_account_id.id,
            }
        return payment_vals

    def action_create_payments(self):
        self.ensure_one()
        if self.ca_ho_id and not self.settelment_ho_id:
            setdet = []
            self.partner_id = self.ca_ho_id.request_by.id
            mysettel = self.env['settelment.ho'].sudo().create({'ca_ho_id': self.ca_ho_id.id,
                                                             'amount_ca': self.ca_ho_id.amount_ca,
                                                            'request_by': self.ca_ho_id.request_by.id,
                                                            'prepaid_by': self.ca_ho_id.prepaid_by.id,
                                                            'verify_by': self.ca_ho_id.verify_by.id,
                                                             'state': 'draft',
                                                             'journal_id': self.journal_id.id
                                                             })
            myline = self.create_ca_jurnal(self.ca_ho_id)
            prec = self.company_id.currency_id.decimal_places
            move_vals = {
                'ref': self.ca_ho_id.name,
                'date': self.payment_date,
                'journal_id': self.journal_id.id,
                'ca_ho_id': self.ca_ho_id.id,
                'line_ids': myline,
                'is_noi_ho': False,
                'is_sundry': False,
                'name': '/',
                'move_type': 'entry',
                'partner_id': self.ca_ho_id.request_by.id,
                'invoice_date': self.payment_date,
                'currency_id': self.ca_ho_id.currency_id.id,
            }
            mybill = self.env['account.move'].with_context(default_is_noi_ho=False,default_is_sundry_site=False).create(move_vals)
            mybill.action_post()
            # self.write({'line_ids': mybill.line_ids.ids})
            # batches = self._get_batches()
            # edit_mode = False
            # to_process = []
            # payment_vals = self._create_payment_vals_from_wizard()
            # to_process.append({
            #     'create_vals': payment_vals,
            #     'to_reconcile': batches[0]['lines'],
            #     'batch': batches[0],
            # })
            # payments = self._init_payments(to_process, edit_mode=edit_mode)
            # self._post_payments(to_process, edit_mode=edit_mode)
            # self._reconcile_payments(to_process, edit_mode=edit_mode)
            self.ca_ho_id.write({'state':'done'})
        else:
            self.partner_id = self.settelment_ho_id.ca_ho_id.request_by.id
            myline = self.create_settelment_jurnal()
            prec = self.company_id.currency_id.decimal_places
            move_vals = {
                'ref': self.settelment_ho_id.ca_ho_id.name,
                'date': self.payment_date,
                'journal_id': self.journal_id.id,
                'settelment_ho_id': self.settelment_ho_id.id,
                'line_ids': myline,
                'name': '/',
                'is_noi_ho': False,
                'is_sundry': False,
                'move_type': 'entry',
                'partner_id': self.settelment_ho_id.request_by.id,
                'invoice_date': self.payment_date,
                'currency_id': self.settelment_ho_id.currency_id.id,
            }
            mybill = self.env['account.move'].with_context(default_is_noi_ho=False,default_is_sundry_site=False).create(move_vals)
            mybill.action_post()
            self.settelment_ho_id.write({'state': 'done'})
        return


    def create_ca_jurnal(self,ca_ids):
        line_ids = []
        amount = 0.0
        amount_currency = 0.0
        for allrec in ca_ids:
            for alldata in allrec.ca_ids:
                amount += alldata.amount
                company_currency = allrec.company_id.currency_id
                current_currency = allrec.currency_id
                prec = company_currency.decimal_places
                balance = allrec.currency_id._convert(alldata.amount, company_currency, allrec.company_id,
                                                       allrec.request_date)
                amount_currency += alldata.amount
                alldata_currency_id = alldata.currency_id.id

            move_line_src = {
                'name': allrec.name,
                'account_id':  allrec.request_by.coa_tujuan.id,
                'credit': 0.0,
                'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'amount_currency': amount_currency,
                'currency_id': alldata_currency_id,
                'partner_id': allrec.request_by.id,
            }
            move_line_dst = {
                'name': allrec.name,
                'debit': 0.0,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'account_id':  self.journal_id.payment_credit_account_id.id,
                'date_maturity': self.payment_date,
                'amount_currency': amount_currency,
                'currency_id':  alldata_currency_id,
                'partner_id': allrec.request_by.id,
            }
            line_ids.append((0, 0, move_line_dst))
            line_ids.append((0,0,move_line_src))
        return line_ids


    def create_settelment_jurnal(self):
        line_ids = []
        prec = False
        for allrec in self.settelment_ho_id:
            if self.payment_difference == 0:
                for alldata in allrec.settelment_ids.filtered(lambda l:l.state=='approved'):
                    amount = alldata.amount
                    company_currency = allrec.company_id.currency_id
                    current_currency = allrec.currency_id
                    prec = company_currency.decimal_places
                    balance = allrec.currency_id._convert(alldata.amount, company_currency, allrec.company_id,
                                                           self.payment_date)
                    amount_currency = alldata.amount
                    move_line_src = {
                        'product_id': alldata.product_id.id,
                        'account_id': alldata.product_id.property_account_expense_id.id,
                        'quantity': 1,
                        'credit': 0.0,
                        'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                        'amount_currency': amount_currency,
                        'currency_id': alldata.currency_id.id,
                        'partner_id': allrec.request_by.id,
                    }
                    line_ids.append((0, 0, move_line_src))
                move_line_dst = {
                    'debit':  0.0,
                    'credit': allrec.ca_ho_id.amount_ca if float_compare(allrec.ca_ho_id.amount_ca, 0.0, precision_digits=prec) > 0 else 0.0,
                    'account_id':  allrec.ca_ho_id.request_by.coa_tujuan.id,
                    'date_maturity': self.payment_date,
                    'amount_currency': allrec.ca_ho_id.amount_ca,
                    'currency_id':  allrec.currency_id.id,
                    'partner_id': allrec.request_by.id,
                }

                line_ids.append((0, 0, move_line_dst))
            elif self.payment_difference < 0:
                for alldata in allrec.settelment_ids.filtered(lambda l:l.state=='approved'):
                    amount = alldata.amount
                    company_currency = allrec.company_id.currency_id
                    current_currency = allrec.currency_id
                    prec = company_currency.decimal_places
                    balance = allrec.currency_id._convert(alldata.amount, company_currency, allrec.company_id,
                                                           self.payment_date)
                    amount_currency = alldata.amount
                    move_line_src = {
                        'product_id': alldata.product_id.id,
                        'account_id': alldata.product_id.property_account_expense_id.id,
                        'quantity': 1,
                        'credit': 0.0,
                        'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                        'amount_currency': amount_currency,
                        'currency_id': alldata.currency_id.id,
                        'partner_id': allrec.request_by.id,
                    }
                    line_ids.append((0, 0, move_line_src))
                move_line_dst = {
                    'debit':  0.0,
                    'credit': allrec.ca_ho_id.amount_ca if float_compare(allrec.ca_ho_id.amount_ca, 0.0, precision_digits=prec) > 0 else 0.0,
                    'account_id':  allrec.ca_ho_id.request_by.coa_tujuan.id,
                    'date_maturity': self.payment_date,
                    'amount_currency': allrec.ca_ho_id.amount_ca,
                    'currency_id':  alldata.currency_id.id,
                    'partner_id': allrec.request_by.id,
                }

                line_ids.append((0, 0, move_line_dst))
                move_line_bank = {
                    'debit':  0.0,
                    'credit': abs(self.payment_difference),
                    'account_id':  self.journal_id.payment_credit_account_id.id,
                    'date_maturity': self.payment_date,
                    'amount_currency': allrec.ca_ho_id.amount_ca,
                    'currency_id':  alldata.currency_id.id,
                    'partner_id': allrec.request_by.id,
                }
                line_ids.append((0, 0, move_line_bank))
            else:
                for alldata in allrec.settelment_ids.filtered(lambda l:l.state=='approved'):
                    amount = alldata.amount
                    company_currency = allrec.company_id.currency_id
                    current_currency = allrec.currency_id
                    prec = company_currency.decimal_places
                    balance = allrec.currency_id._convert(alldata.amount, company_currency, allrec.company_id,
                                                           self.payment_date)
                    amount_currency = alldata.amount
                    move_line_src = {
                        'product_id': alldata.product_id.id,
                        'account_id': alldata.product_id.property_account_expense_id.id,
                        'quantity': 1,
                        'credit': 0.0,
                        'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                        'amount_currency': amount_currency,
                        'currency_id': alldata.currency_id.id,
                        'partner_id': allrec.request_by.id,
                    }
                    line_ids.append((0, 0, move_line_src))
                move_line_dst = {
                    'debit':  0.0,
                    'credit': allrec.ca_ho_id.amount_ca if float_compare(allrec.ca_ho_id.amount_ca, 0.0, precision_digits=prec) > 0 else 0.0,
                    'account_id':  allrec.ca_ho_id.request_by.coa_tujuan.id,
                    'date_maturity': self.payment_date,
                    'amount_currency': allrec.ca_ho_id.amount_ca,
                    'currency_id':  alldata.currency_id.id,
                    'partner_id': allrec.request_by.id,
                }

                line_ids.append((0, 0, move_line_dst))
                move_line_bank = {
                    'debit':  abs(self.payment_difference),
                    'credit': 0.0,
                    'account_id':  self.journal_id.payment_credit_account_id.id,
                    'date_maturity': self.payment_date,
                    'amount_currency': allrec.ca_ho_id.amount_ca,
                    'currency_id':  alldata.currency_id.id,
                    'partner_id': allrec.request_by.id,
                }
                line_ids.append((0, 0, move_line_bank))
        return line_ids

