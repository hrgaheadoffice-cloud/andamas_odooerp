from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero, float_round


class LeasingManagementPayment(models.TransientModel):
    _name = 'leasing.management.payment'
    _description = 'Leasing Management Payment'

    def _get_default_currency_id(self):
        return self.env.company.currency_id.id

    @api.depends('journal_id')
    def compute_journal_balance(self):
        for me in self:
            me.journal_balance = 0.0
            if me.journal_id:
                bank_account_balance, nb_lines_bank_account_balance = me.journal_id._get_journal_bank_account_balance(
                    domain=[('parent_state', '=', 'posted')])
                me.journal_balance = bank_account_balance

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
                caribank = self.env['res.partner.bank'].sudo().search([('id', 'in', databank)])
                alldata.available_partner_bank_ids = [(6, 0, caribank.ids)]
            else:
                alldata.available_partner_bank_ids = False

    journal_id = fields.Many2one('account.journal',string='Journal', store=True, readonly=False,
                                 compute='_compute_journal_id',
                                 domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")
    available_partner_bank_ids = fields.Many2many(
        comodel_name='res.partner.bank',
        compute='_compute_available_partner_bank_ids',
        store=False
    )

    partner_bank_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string="Recipient Bank Account",
        readonly=False,
        store=True,
        domain="[('id', 'in', available_partner_bank_ids)]",
        ondelete='restrict')
    amount = fields.Float(digits='Account', string='Amount', tracking=5)
    currency_id = fields.Many2one('res.currency', 'Currency', default=_get_default_currency_id, required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    payment_date = fields.Date('Payment Date')
    communication = fields.Text('Memo')
    leasing_management_voucher_id = fields.Many2one('lm.journal.voucher', string='Leasing Management')
    line_ids = fields.Many2many('account.move.line', 'leasing_management_voucher_payment_move_line_rel', 'wizard_id',
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
    journal_balance = fields.Float(compute='compute_journal_balance',string='Journal Balance')

    

    @api.depends('amount','leasing_management_voucher_id')
    def _compute_payment_difference(self):
        for wizard in self:
            if wizard.leasing_management_voucher_id:
                wizard.payment_difference = 0
            else:
                wizard.payment_difference = 0
                # wizard.payment_difference = wizard.leasing_management_voucher_id.over_due

    @api.depends('company_id')
    def _compute_journal_id(self):
        for wizard in self:
            wizard.journal_id = self.env['account.journal'].search([
                    ('type', 'in', ('bank', 'cash')),
                    ('company_id', '=', wizard.company_id.id),
                ], limit=1)

    @api.model
    def default_get(self, default_fields):
        res = super(LeasingManagementPayment, self).default_get(default_fields)
        mymodel = self._context.get('active_model')
        activeid = self._context.get('active_ids')
        if mymodel == 'lm.journal.voucher':
            mylm = self.env['lm.journal.voucher'].sudo().browse(activeid)
            res['leasing_management_voucher_id'] = activeid
            res['amount'] = mylm.request_amount
            res['payment_type'] = 'outbound'
            res['partner_type'] = 'customer'
            res['payment_difference_handling'] = 'open'
            res['communication'] = mylm.name
        return res

    def action_create_payments(self):
        self.ensure_one()
        if self.leasing_management_voucher_id:
            print('===????',self.leasing_management_voucher_id.name)
            setdet = []
            myline_credit = self.create_lm_jurnal_credit(self.leasing_management_voucher_id)
            myline_debit  = self.create_lm_jurnal_debit(self.leasing_management_voucher_id)
            total_myline = myline_credit + myline_debit
            print('=====>>>>>total_myline',total_myline)
            prec = self.company_id.currency_id.decimal_places
            move_vals = {
                'ref': self.leasing_management_voucher_id.name,
                'date': fields.Datetime.now(),
                'journal_id': self.journal_id.id,
                'lm_journal_voucher_id': self.leasing_management_voucher_id.id,
                'line_ids': total_myline,
                'is_noi_ho': False,
                'is_sundry': False,
                'name': '/',
                'move_type': 'entry',
                'invoice_date': self.payment_date,
                'currency_id': self.leasing_management_voucher_id.currency_id.id,
            }
            mybill = self.env['account.move'].with_context(default_is_noi_ho=False, default_is_sundry_site=False).create(move_vals)
            mybill.action_post()
            self.leasing_management_voucher_id.write({'state': 'done'})
        return

    def create_lm_jurnal_credit(self,lm_ids):
        line_ids = []
        amount = 0.0
        amount_currency = 0.0
        for allrec in lm_ids:
            for alldata in allrec.lm_journal_voucher_ids:
                alldatadescription = alldata.description
                amount += alldata.amount
                company_currency = allrec.company_id.currency_id
                current_currency = allrec.currency_id
                prec = company_currency.decimal_places
                balance = allrec.currency_id._convert(alldata.amount, company_currency, allrec.company_id,
                                                       allrec.request_date)
                amount_currency += alldata.amount
                alldata_currency_id = alldata.currency_id.id
                allrec_request_by = allrec.request_by.id
            move_line_dst = {
                'name': "Bank",
                'debit': 0.0,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'account_id':  self.journal_id.payment_credit_account_id.id,
                'date_maturity': self.payment_date,
                'amount_currency': amount_currency,
                'currency_id':  alldata_currency_id,
                'partner_id': allrec_request_by,
                'activity': allrec.activity,
            }
            line_ids.append((0, 0, move_line_dst))
        return line_ids

    def create_lm_jurnal_debit(self,lm_ids):
        line_ids = []
        for allrec in lm_ids:
            for alldata in allrec.lm_journal_voucher_ids:
                amount = alldata.amount
                company_currency = allrec.company_id.currency_id
                current_currency = allrec.currency_id
                prec = company_currency.decimal_places
                balance = allrec.currency_id._convert(alldata.amount, company_currency, allrec.company_id,
                                                       allrec.request_date)
                amount_currency = alldata.amount
                move_line_src = {
                    'name': alldata.description,
                    'account_id':   alldata.account_id.id,
                    'credit': 0.0,
                    'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                    'amount_currency': amount_currency,
                    'currency_id': alldata.currency_id.id,
                    'partner_id': allrec.request_by.id,
                    'activity': allrec.activity,
                }
                line_ids.append((0,0,move_line_src))
        return line_ids
