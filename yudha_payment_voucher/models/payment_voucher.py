#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, ValidationError

class PaymentPlan(models.Model):
    _name = 'payment.plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "create_date desc, id desc"
    _description = "Payment Plan"
    _rec_name = 'name'
    _check_company_auto = True

    @api.depends('ca_payment_ids.amount')
    def _amount_all(self):
        for me in self:
            amount_total = 0
            for line in me.ca_payment_ids:
                amount_total += line.amount
            me.update({
                'amount_total': amount_total,
            })

    @api.depends('journal_id', 'amount_total')
    def compute_journal_balance(self):
        for me in self:
            me.journal_balance = me.estimated_balance = 0
            if me.journal_id:
                bank_account_balance, nb_lines_bank_account_balance = me.journal_id._get_journal_bank_account_balance(
                    domain=[('parent_state', '=', 'posted')])
                me.journal_balance = bank_account_balance
                me.estimated_balance = me.journal_balance - me.amount_total

    name = fields.Char('Document Name',index=True,required=True,default='New')
    journal_id = fields.Many2one('account.journal',string='Journal', store=True, readonly=False,
        compute='_compute_journal_id',
        domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")
    company_id  = fields.Many2one('res.company', string='Company',default=lambda self:self.env.company)
    payment_date = fields.Date(string="Payment Date", required=True,
        default=fields.Date.context_today)

    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        compute='_compute_currency_id',
        help="The payment's currency.")

    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method',
        readonly=False, store=True,
        compute='_compute_payment_method_id',
        domain="[('id', 'in', available_payment_method_ids)]",
        help="Manual: Get paid by cash, check or any other method outside of Odoo.\n"\
        "Electronic: Get paid automatically through a payment acquirer by requesting a transaction on a card saved by the customer when buying or subscribing online (payment token).\n"\
        "Check: Pay bill by check and print it from Odoo.\n"\
        "Batch Deposit: Encase several customer checks at once by generating a batch deposit to submit to your bank. When encoding the bank statement in Odoo, you are suggested to reconcile the transaction with the batch deposit.To enable batch deposit, module account_batch_payment must be installed.\n"\
        "SEPA Credit Transfer: Pay bill from a SEPA Credit Transfer file you submit to your bank. To enable sepa credit transfer, module account_sepa must be installed ")
    available_payment_method_ids = fields.Many2many('account.payment.method',
        compute='_compute_payment_method_fields')
    hide_payment_method = fields.Boolean(
        compute='_compute_payment_method_fields',
        help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")
    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money'),
    ], string='Payment Type',index=True)
    state = fields.Selection([('draft','Draft'),
                              ('to_approved', 'Request For Approval'),
                              ("to_approve_matrix", "Tobe Approved Matrix"),
                              ('approved','Approved'),
                              ('rejected', 'Rejected'),
                              ],default='draft',string='Status',readonly=True)

    payment_plan_ids = fields.One2many('payment.plan.details','plan_id',domain="[('dibuang','=',False)]",string='Payment Plan Details')
    ca_payment_ids = fields.One2many('ca.payment.detail','plant_id')
    journal_balance = fields.Float(compute='compute_journal_balance')
    estimated_balance = fields.Float(compute='compute_journal_balance')
    amount_total = fields.Float('Total', store=True, readonly=True, compute='_amount_all')
    todo_user_ids = fields.Many2many(comodel_name="res.users",string="Next Approval",readonly=True,copy=False)
    approval_matrix_ids = fields.One2many(
            comodel_name="approval.matrix",
            inverse_name="plan_id",
            string="Approval Matrix",
            readonly=True,
            copy=False,
            track_visibility="onchange",
        )

    def create_approval_matrix(self):
        obj_app = self.env['config.approval.matrix'].search([('modul','=','PAYMENT'),('company_id','=',self.company_id.id)],order="matrix_level_name asc")  
        for item in obj_app:
            vals = {
                "plan_id":self.id,
                "user_ids": [(6, 0, item.approval_user_ids.ids)],
                "matrix_level_id":item.matrix_level_id.id,
                "config_approval_matrix_id":item.id,
                "state":"Tobe Approved Mtrx "+ item.matrix_level_name,
                "name":"Tobe Approved Mtrx "+ item.matrix_level_name,
            }
            obj_create = self.env['approval.matrix'].create(vals)



    def insert_ca(self):
        return {
            'type': 'ir.actions.act_window',
            # 'name':"Insert Cash Advance",
            'res_model': 'insert.ca.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'name': "Insert Document",
            'target': 'new',
            'context':{'default_payment_plant_id':self.id},
        }
        

    @api.depends('journal_id')
    def _compute_currency_id(self):
        for wizard in self:
            wizard.currency_id = wizard.journal_id.currency_id or wizard.currency_id or wizard.company_id.currency_id



    @api.depends('payment_type',
                 'journal_id.inbound_payment_method_ids',
                 'journal_id.outbound_payment_method_ids')
    def _compute_payment_method_fields(self):
        for wizard in self:
            wizard.available_payment_method_ids = wizard._get_batch_available_payment_methods(wizard.journal_id, wizard.payment_type)
            wizard.hide_payment_method = len(wizard.available_payment_method_ids) == 1 and wizard.available_payment_method_ids.code == 'manual'

    @api.model
    def _get_batch_available_payment_methods(self, journal, payment_type):
        if payment_type == 'inbound':
            return journal.inbound_payment_method_ids._origin
        else:
            return journal.outbound_payment_method_ids._origin

    def button_approved_matrix(self):
        emp_id = self.env['approval.matrix'].search([('plan_id','=',self.id),('realization_user_id','=',False)],limit=1,order="state asc")
        if emp_id:
            if self.env.uid in (emp_id.config_approval_matrix_id.approval_user_ids.ids) or emp_id.config_approval_matrix_id.delegate_user.id == self.env.uid:
                emp_id.write({'realization_user_id':self.env.uid,"date": fields.Datetime.now()})
                emp_id = self.env['approval.matrix'].search([('plan_id','=',self.id),('realization_user_id','=',False)],limit=1,order="state asc")
                if not emp_id:
                    self.todo_user_ids = False
                    self.state = 'approved'
                    if self.ca_payment_ids:
                        for data in self.ca_payment_ids:
                            if data.ca_id:
                                data.ca_id.state = 'waiting_on_payment'
                            if data.noi_id:
                                data.noi_id.state = 'waiting_on_payment'
                            if data.settlement_id:
                                data.settlement_id.state = 'waiting_on_payment'
                            if data.cash_request_id:
                                data.cash_request_id.state = 'waiting_on_payment'
                            
                            if data.reimbursement_id:
                                data.reimbursement_id.state = 'waiting_on_payment'
                            
                            data.is_show_button = False
                else:
                    self.todo_user_ids = [(6, 0, emp_id.config_approval_matrix_id.approval_user_ids.ids)]
            else:
                raise UserError(
                    _("Anda tidak berhak melakukan proses ini"))

    def button_approved(self):
        appr_id = self.env['tbl_matrix_auth'].search([('modul', '=', 'PAYMENT'), ('company_id', '=', self.company_id.id)]).approval_user
        if appr_id.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        if self.ca_payment_ids:
            for data in self.ca_payment_ids:
                if data.ca_id:
                    data.ca_id.state = 'waiting_on_payment'
                if data.noi_id:
                    data.noi_id.state = 'waiting_on_payment'
                if data.settlement_id:
                    data.settlement_id.state = 'waiting_on_payment'
                if data.cash_request_id:
                    data.cash_request_id.state = 'waiting_on_payment'
                
                if data.reimbursement_id:
                    data.reimbursement_id.state = 'waiting_on_payment'
                
                data.is_show_button = False
        return self.write({'state':'approved'})
        
    def button_to_approve(self):
        self.approval_matrix_ids.unlink()
        self.create_approval_matrix()
        if not self.approval_matrix_ids:
            raise UserError(
                _("Approval Matrix not found, Please Check Config Approval Matrix"))
        emp_id = self.env['approval.matrix'].search([('plan_id','=',self.id),('realization_user_id','=',False)],limit=1,order="state asc")
        if emp_id:
            self.todo_user_ids = [(6, 0, emp_id.config_approval_matrix_id.approval_user_ids.ids)]
        for data in self.ca_payment_ids:
            if data.ca_id:
                data.ca_id.is_insert_plant = True
            if data.noi_id:
                data.noi_id.is_insert_plant = True
            if data.settlement_id:
                data.settlement_id.is_insert_plant = True
            if data.cash_request_id:
                data.cash_request_id.is_insert_plant = True
            if data.reimbursement_id:
                data.reimbursement_id.is_insert_plant = True
            if data.vendor_bill_id:
                data.vendor_bill_id.is_insert_plant = True
                
        return self.write({'state':'to_approve_matrix'})

    def action_draft(self):
        return self.write({'state':'draft'})

    def button_reject(self):
        if self.ca_payment_ids:
            for data in self.ca_payment_ids:
                data.action_rejected()

        return self.write({'state':'rejected'})

    def unlink(self):
        for alldata in self:
            if alldata.state == 'paid':
                raise UserError('You Cannot Delete Data That Already Paid!')
            for allrec in alldata.payment_plan_ids:
                allrec.action_rejected()

            for allrec in alldata.payment_plan_ids:
                allrec.action_rejected()
                
        return super(PaymentPlan,self).unlink()

    def button_register_payment(self):
        for allrec in self:
            for allids in allrec.payment_plan_ids:
                mylines =[]
                for allines in allids.moves_id.invoice_line_ids:
                    mylines.append(allines.id)
                self.env['account.payment.register'].with_context(active_model='account.move', active_ids=allids.moves_id.ids).create({
                    'payment_date': allids.moves_id.invoice_date,
                    'journal_id': allrec.journal_id.id,
                    'payment_type': allrec.payment_type,
                    'payment_difference_handling': 'open',
                    'payment_method_id': allrec.payment_method_id.id,
                    'amount': allids.amount_currency,
                    'line_ids':[(6, 0, mylines)],
                })._create_payments()
                if allids.contx =="CA HO":
                     myca = self.env['cash.advance.ho'].sudo().search([('name','=',allids.source_doc)],limit=1)
                     myca.write({'state': 'done'})
                elif allids.contx =="NOI":
                     myca = self.env['noi'].sudo().search([('name','=',allids.source_doc)],limit=1)
                elif allids.contx =="Settlement HO":
                     myca = self.env['settelment.ho'].sudo().search([('name','=',allids.source_doc)],limit=1)
                     myca.write({'state': 'done'})
                elif allids.contx =="Cash Request":
                     myca = self.env['cash.request'].sudo().search([('name','=',allids.source_doc)],limit=1)
                     myca.write({'state': 'done'})
                elif allids.contx =="Reimbursement HO":
                     myca = self.env['reimbursement.ho'].sudo().search([('name','=',allids.source_doc)],limit=1)
                     myca.write({'state': 'done'})
            allrec.state='paid'


class caPaymentdetail(models.Model):
    _name = 'ca.payment.detail'

    def _get_default_currency_id(self):
        return self.env.company.currency_id.id

    plant_id = fields.Many2one('payment.plan')
    ca_id = fields.Many2one('cash.advance.ho')
    document_number = fields.Char()
    request_date = fields.Date(related='ca_id.request_date',store=True)
    create_document_date = fields.Date()
    amount = fields.Monetary()
    currency_id = fields.Many2one('res.currency', 'Currency')
    is_show_button = fields.Boolean(default=True)
    vendor_bill_id = fields.Many2one('account.move')
    noi_id = fields.Many2one('noi')
    cash_request_id = fields.Many2one('cash.request')
    settlement_id = fields.Many2one('settelment.ho')
    reimbursement_id = fields.Many2one('reimbursement.ho')
    document_type = fields.Selection([('vendor_bill','Vendor Bils'),('ca_ho','Cash Advance HO'),('noi_ho','NOI HO'),('settlement_ho','Settlement HO'),
                                      ('cash_request','Cash Request'),
                                      ('reimbursement_ho','Reimbursement HO')
                                      ])

    def action_approved(self):
        if self.ca_id:
            # self.ca_id.state = 'waiting_on_payment'
            self.is_show_button = False

    def action_rejected(self):
        if self.vendor_bill_id:
            self.is_show_button = False

        if self.ca_id:
            self.ca_id.is_insert_plant = False
            self.is_show_button = False
            self.ca_id.state = 'approved'

        if self.noi_id:
            self.noi_id.is_insert_plant = False
            self.is_show_button = False
            self.noi_id.state = 'approved'

        if self.settlement_id:
            self.settlement_id.is_insert_plant = False
            self.is_show_button = False
            self.settlement_id.state = 'approved'

        if self.cash_request_id:
            self.cash_request_id.is_insert_plant = False
            self.is_show_button = False
            self.cash_request_id.state = 'approved'

        if self.reimbursement_id:
            self.reimbursement_id.is_insert_plant = False
            self.is_show_button = False
            self.reimbursement_id.state = 'approved'


class PaymentPlanDetails(models.Model):
    _name = 'payment.plan.details'

    plan_id = fields.Many2one('payment.plan',string='Plann ID',index=True)

    date_maturity = fields.Date(string='Due Date', index=True, tracking=True,
        help="This field is used for payable and receivable journal entries. You can put the limit date for the payment of this line.")

    invoice_date = fields.Date(string='Invoice Date', index=True, tracking=True,
        help="This field is used for payable and receivable journal entries. You can put the limit date for the payment of this line.")
    partner_id = fields.Many2one('res.partner',string='Partner')
    moves_id = fields.Many2one('account.move',string='Document Name',index=True)
    source_doc = fields.Char('Source Document',index=True)
    company_id  = fields.Many2one('res.company', string='Company',default=lambda self:self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id', string='Company Currency',
        readonly=True, store=True,
        help='Utility field to express amount currency')
    amount_currency = fields.Monetary(string='Amount in Currency', store=True, copy=True,
        help="The amount expressed in an optional other currency if it is a multi-currency entry.")
    state = fields.Selection([('approved','Approved'),
                              ('rejected','Rejected'),
                              ('paid','Paid')],default='approved',string='Status',readonly=True)

    is_approved = fields.Boolean('Is Approved',default=False)
    is_rejected = fields.Boolean('Is Rejected',default=False)
    dibuang = fields.Boolean('Di buang',default=False)
    alasan = fields.Text('Reason',index=True)
    contx = fields.Text('Context')

    def action_approved(self):
        for alldata in self:
            alldata.is_approved = True
            alldata.is_rejected= False
            alldata.dibuang = False
        # return {
        #     'name': _('Approve Reason'),
        #     'res_model': 'reimbursement.reason.wiz',
        #     'view_mode': 'form',
        #     'context': {
        #         'active_model': 'cash.advance',
        #         'active_ids': self.id,
        #         'tindakan': 'approved',
        #     },
        #     'target': 'new',
        #     'type': 'ir.actions.act_window',
        # }

        # for allrec in self:
        #     if not allrec.product_id:
        #         raise UserWarning("Please Insert Product First")
        # return self.write({'is_approved': True ,'is_rejected': False,'state':'approved'})

    def action_rejected(self):
        for alldata in self:
            alldata.is_approved = False
            alldata.is_rejected= True
            alldata.dibuang = True
            alldata.moves_id.write({'already_process': False})
            alldata.plan_id = False


        # return {
        #     'name': _('Rejected Reason'),
        #     'res_model': 'reimbursement.reason.wiz',
        #     'view_mode': 'form',
        #     'context': {
        #         'active_model': 'cash.advance',
        #         'active_ids': self.id,
        #         'tindakan': 'rejected',
        #     },
        #     'target': 'new',
        #     'type': 'ir.actions.act_window',
        # }

    @api.onchange('moves_id')
    def onchange_moves_id(self):
        for alldata in self:
            if not alldata.moves_id:
                return

class InheritApprovalMatrixPaymentPlan(models.Model):
    _inherit = "approval.matrix"

    plan_id = fields.Many2one('payment.plan','Payment Plant')