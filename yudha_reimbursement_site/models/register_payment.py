# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero, float_round

class ReimbursementPaymentSite(models.TransientModel):
    _name = 'reimbursement.payment.site'
    _description = 'Reimbursement Payment Site'

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
        domain="[('id', 'in', available_partner_bank_ids)]",
    )
    amount = fields.Float(digits='Account',string='Amount', tracking=5)
    currency_id = fields.Many2one('res.currency', 'Currency', default=_get_default_currency_id, required=True)
    company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.company)
    payment_date = fields.Date('Payment Date')
    communication = fields.Text('Memo')
    reimbursement_site_id = fields.Many2one('reimbursement.site',string='Cash Request')
    line_ids = fields.Many2many('account.move.line', 'reimbursement_payment_site_move_line_rel', 'wizard_id',
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

    @api.depends('amount','reimbursement_site_id')
    def _compute_payment_difference(self):
        for wizard in self:
            wizard.payment_difference = 0


    @api.depends('company_id')
    def _compute_journal_id(self):
        for wizard in self:
                wizard.journal_id = self.env['account.journal'].search([
                    ('type', 'in', ('bank', 'cash')),
                    ('company_id', '=', wizard.company_id.id),
                ], limit=1)

    @api.model
    def default_get(self, default_fields):
        res = super(ReimbursementPaymentSite, self).default_get(default_fields)
        mymodel =  self._context.get('active_model')
        activeid =  self._context.get('active_ids')
        if mymodel == 'reimbursement.site':
            myca = self.env['reimbursement.site'].sudo().browse(activeid)
            res['reimbursement_site_id'] = activeid
            res['amount'] = myca.request_amount
            res['payment_type'] = 'outbound'
            res['partner_type'] = 'customer'
            res['payment_difference_handling'] = 'open'
            res['communication'] = myca.name
        return res

    def action_create_payments(self):
        self.ensure_one()
        if self.reimbursement_site_id:
            setdet = []
            self.partner_id = self.reimbursement_site_id.request_by.id
            myline = self.create_ca_jurnal(self.reimbursement_site_id)
            move_vals = {
                'ref': self.reimbursement_site_id.name,
                'date': self.payment_date,
                'journal_id': self.journal_id.id,
                'reimbursement_site_id': self.reimbursement_site_id.id,
                'line_ids': myline,
                'is_noi_ho': False,
                'is_sundry': False,
                'name': '/',
                'move_type': 'entry',
                'partner_id': self.reimbursement_site_id.request_by.id,
                'invoice_date': self.payment_date,
                'currency_id': self.reimbursement_site_id.currency_id.id,
            }
            mybill = self.env['account.move'].with_context(default_is_noi_ho=False,default_is_sundry_site=False).create(move_vals)
            mybill.action_post()
            self.reimbursement_site_id.write({'state':'done'})
        return

    def create_ca_jurnal(self,ca_ids):
        line_ids = []
        for alldata in ca_ids.reimbursement_ids.filtered(lambda p: p.state=='approved'):
            amount = alldata.final_amount
            company_currency = alldata.company_id.currency_id
            current_currency = alldata.currency_id
            prec = company_currency.decimal_places
            move_line_src = {
                'name': alldata.description,
                'account_id': alldata.product_id.property_account_expense_id.id,
                'product_id': alldata.product_id.id,
                'credit': 0.0,
                'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'currency_id': alldata.currency_id.id,
                'partner_id': alldata.reimbursement_site_id.request_by.id,
            }

            line_ids.append((0,0,move_line_src))

        move_line_dst = {
            'name': '/',
            'debit': 0.0,
            'credit': self.amount if float_compare(self.amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'account_id': self.journal_id.payment_credit_account_id.id,
            'date_maturity': self.payment_date,
            'amount_currency': self.amount,
            'currency_id':self.reimbursement_site_id.currency_id.id,
            'partner_id': self.reimbursement_site_id.request_by.id,
        }
        line_ids.append((0, 0, move_line_dst))
        return line_ids
