# coding: utf-8
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import datetime
from datetime import date
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
import calendar
from math import floor
import base64  # file encode
from urllib.request import urlopen


class LeasingManagement(models.Model):
    _name = "leasing.management"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name       = fields.Char('Name', default="New",copy=False)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    total_leasing     = fields.Float('Total Leasing')
    total_principal_amount     = fields.Float('Total Principal Amount')
    total_interest_amount     = fields.Float('Total Interest Amount')
    total_paid     = fields.Float('Total Paid')
    remaining_amount     = fields.Float('Remaining Amount')
    processing_date       = fields.Date('Processing Date',copy=False)
    state      = fields.Selection([
        ("draft", "Draft"),
        ('approved', 'Approved'),
        # ("done", "Done"),
        ("rejected",'Rejected')],default='draft',string='State',readonly=True,copy=False)
    lessor_id  = fields.Many2one('lessor.leasing.management','Lessor Name')
    contract_number = fields.Char('Contract Number')
    asset_class_id  = fields.Many2one('asset.class','Asset Class')
    asset_name      = fields.Char('Asset Name')
    tennor_id        = fields.Many2one('tennor.leasing.management','Tennor')
    project_code_id = fields.Many2one('project.code.leasing.management','Project Code')
    asset_qty     = fields.Float('Asset Qty')
    loan_account_id     = fields.Many2one('account.account','Loan Account')
    interest_account_id     = fields.Many2one('account.account','Interest Account')
    journal_id     = fields.Many2one('account.journal','Journal')
    analytic_account_id     = fields.Many2one('account.analytic.account','Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tag')
    rate_amount = fields.Float(string='Rate')
    leasing_management_ids  = fields.One2many('leasing.management.line','leasing_management_id', string='Leasing Management Line')
    detail_asset_leasing_management_ids  = fields.One2many('leasing.management.detail.asset','leasing_management_id', string='Detail Asset Leasing Management Line')
    is_insert_plant = fields.Boolean(default=False,copy=False)
    activity = fields.Selection(
        [('Stockpile', 'Stockpile'),
         ('Hauling Internal', 'Hauling Internal'),
         ('Hauling Subcon', 'Hauling Subcon'),
         ('Rental', 'Rental'),
         ('Overburden', 'Overburden')],
        string='Activity',
        )

    def create_move_id_1(self,rec,journal_id,move_pool,line_mv_ids):
        """
            create move id in journal entries
        :return: move ID
        """
        move = {
            'name': '/',
            'journal_id': journal_id,
            'lm_journal_voucher_ids' : line_mv_ids,
            "leasing_management_id": rec.leasing_management_id.id,
            "leasing_management_line_id": rec.id,
            "request_date": rec.journal_date,
            "activity": rec.activity,
            "state": "draft",
        }
        move_id = move_pool.create(move)
        return move_id

    def create_journal_rev_1(self,rec,journal_id,move_line_pool):
        list_ap_mv = []
        for item in self:
            move_line_credit = {
                        'description': 'Interest Amount',
                        'amount':  rec.interest_amount,
                        "account_id": item.interest_account_id.id, 
                    }
            list_ap_mv.append((0, 0, move_line_credit))
            return list_ap_mv
    
    def create_journal_rev_2(self,rec,journal_id,move_line_pool):
        list_ap_mv = []
        for item in self:
            move_line_credit = {
                    'description': 'Principal Amount',
                    'amount': rec.principal_amount,
                    "account_id": item.loan_account_id.id,                   
                }
            list_ap_mv.append((0, 0, move_line_credit))
            return list_ap_mv

    def generate_journal_voucher(self):
        move_pool = self.env['lm.journal.voucher']
        move_line_pool = self.env['lm.journal.voucher.line']
        for item in self:
            for line in item.leasing_management_ids:
                if not line.journal_voucher_id and line.is_journal_voucher == True:
                    journal_id = item.journal_id.id
                    line_mv_ids_1 = item.create_journal_rev_1(line, journal_id, move_line_pool)
                    line_mv_ids_2 = item.create_journal_rev_2(line, journal_id, move_line_pool)
                    line_mv_ids_4 = line_mv_ids_1 + line_mv_ids_2
                    move = item.create_move_id_1(line, journal_id, move_pool,line_mv_ids_4)
                    line.journal_voucher_id = move.id 

    def register_payment(self):
        return {
            'name': _('Register Payment'),
            'res_model': 'leasing.management.payment',
            'view_mode': 'form',
            'context': {
                'active_model': 'leasing.management',
                'active_ids': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def write(self, vals):
        result = super(LeasingManagement, self).write(vals)
        self.calculate_os_principal()
        return result

    def calculate_os_principal(self):
        for i in self:
            for item in i.leasing_management_ids:
                item.installment_amount = item.principal_amount + item.interest_amount
                if item.name =='Installment - 1':
                    item.os_principal_amount = item.leasing_management_id.total_leasing - item.principal_amount - item.interest_amount
                else:
                    id_lml = int(item.lml_id) - 1                
                    lml = self.env['leasing.management.line'].search([('id','=',int(id_lml))])
                    # item.interest_amount = item.installment_amount - item.principal_amount
                    item.os_principal_amount = lml.os_principal_amount - item.principal_amount - item.interest_amount

    def button_approved(self):
        for item in self:
            if not item.leasing_management_ids:
                raise UserError(
                _("Please Klik Button Generate Installment"))
            if item.name == 'New':
                item.name = self.env["ir.sequence"].next_by_code("leasing.management")
            item.write({'state':'approved'})

    def get_id_leasing_management_line(self):
        for item in self:
            for i in item.leasing_management_ids:
                i.lml_id = i.id

          

    def calculate(self):
        for o in self:
            installment_amount = o.total_leasing / o.tennor_id.tennor
            rate = o.rate_amount/100
            start_installment_date = o.processing_date
            o.leasing_management_ids.unlink()
            prev_installment_date = start_installment_date

            count = 0
            curbalance = 0
            interest_amount = installment_amount * rate
            principal_amount = installment_amount - interest_amount
            os_principal_amount = o.total_principal_amount

            for l in range(0, o.tennor_id.tennor):
                count += 1
                next_installment_date = (
                    datetime.strptime(str(prev_installment_date), '%Y-%m-%d') + relativedelta(months=count)).strftime('%Y-%m-%d')
                vals = {
                    'leasing_management_id': o.id,
                    'due_date': next_installment_date,
                    'journal_date': next_installment_date,
                    'name': 'Installment - %s' % count,
                    'tennor': 'Installment - %s' % count,
                    'installment_amount' : installment_amount
                }
                self.env['leasing.management.line'].sudo().create(vals)
        self.get_id_leasing_management_line()
        self.button_force_rounding()

    def button_force_rounding(self):
        for rec in self:
            installment_amount = rec.leasing_management_ids.filtered( lambda line: line.installment_amount)
            debit_decimal_value = round(sum([round(debit_line.installment_amount % 1, 2) for debit_line in installment_amount]))

            for line_id in rec.leasing_management_ids:
                if line_id.installment_amount:
                    if line_id.installment_amount % 1 >= 0.5 and debit_decimal_value > 0:
                        line_id.with_context(check_move_validity=False).write({
                            'installment_amount': line_id.currency_id.with_context(custom_rounding=1.000).round(line_id.installment_amount)
                        })
                        debit_decimal_value -= 1
                    else:
                        line_id.with_context(check_move_validity=False).write({
                            'installment_amount':floor(line_id.installment_amount)
                        })
        return

class LeasingManagementLine(models.Model):
    _name = "leasing.management.line"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    leasing_management_id       = fields.Many2one('leasing.management','Leasing Management')
    lml_id     =fields.Integer('ID LML')
    name       = fields.Char('Name')
    tennor       = fields.Char('Tennor')
    due_date       = fields.Date('Due Date')
    journal_date       = fields.Date('Journal Date')
    installment_amount     = fields.Float('Installment Amount',compute="_compute_principal_interest_amount",store=True)
    principal_amount     = fields.Float('principal Amount')
    interest_amount     = fields.Float('Interest Amount')
    os_principal_amount    = fields.Float('OS principal Amount',compute="_compute_principal_interest_amount",store=True)
    journal_voucher_id     = fields.Many2one('lm.journal.voucher','Journal Voucher')
    is_journal_voucher  = fields.Boolean('Make Journal',default=True)  
    state_transaction = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("to_approve_matrix", "Tobe Approved Matrix"),
            ('approved', 'Approved'),
            ("waiting_on_payment", "Waiting On Payment"),
            ("done", "Done"),
            ("rejected",'Rejected')
        ],
        string='Status Transaction', related="journal_voucher_id.state", store=True
    )

    @api.depends('principal_amount')
    def _compute_principal_interest_amount(self):
        for item in self:
            item.installment_amount = item.principal_amount + item.interest_amount
            if item.name =='Installment - 1':
                item.os_principal_amount = item.leasing_management_id.total_leasing - item.principal_amount - item.interest_amount
            else:
                id_lml = int(item.lml_id) - 1                
                lml = self.env['leasing.management.line'].search([('id','=',int(id_lml))])
                
                item.os_principal_amount = lml.os_principal_amount - item.principal_amount - item.interest_amount

class LeasingManagementDetailAsset(models.Model):
    _name = "leasing.management.detail.asset"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name       = fields.Char('Name')
    leasing_management_id       = fields.Many2one('leasing.management','Leasing Management')
    

class LessorLeasingManagement(models.Model):
    _name = "lessor.leasing.management"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name       = fields.Char('Name')

class AssetLeasingManagement(models.Model):
    _name = "asset.class"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name       = fields.Char('Name')

class TennorLeasingManagement(models.Model):
    _name = "tennor.leasing.management"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name       = fields.Char('Name')
    tennor      = fields.Integer('Tennor')

class ProjectCodeLeasingManagement(models.Model):
    _name = "project.code.leasing.management"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name       = fields.Char('Name')

class AccountMoveLeasingManagement(models.Model):
    _inherit = "account.move"

    leasing_management_id       = fields.Many2one('leasing.management','Leasing Management')
    leasing_management_line_id       = fields.Many2one('leasing.management.line','Leasing Management Line')

class InheritPaymentPlan(models.Model):
    _inherit = 'payment.plan'

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

                            if data.vendor_bill_id:
                                data.vendor_bill_id.action_post()

                            if data.leasing_management_voucher_id:
                                data.leasing_management_voucher_id.state = 'waiting_on_payment'
                            
                            data.is_show_button = False
                else:
                    self.todo_user_ids = [(6, 0, emp_id.config_approval_matrix_id.approval_user_ids.ids)]
            else:
                raise UserError(
                    _("Anda tidak berhak melakukan proses ini"))


class InheritcaPaymentdetail(models.Model):
    _inherit = 'ca.payment.detail'

    leasing_management_voucher_id = fields.Many2one('lm.journal.voucher')
    document_type = fields.Selection(selection_add=[
                                      ('leasing_management_voucher','Leasing Management')
                                      ])

    def action_rejected(self):
        res = super(InheritcaPaymentdetail, self).action_rejected()
        for rec in self:
            rec.action_rejected_lm_voucher()

    def action_rejected_lm_voucher(self):
        if self.leasing_management_voucher_id:
            self.leasing_management_voucher_id.is_insert_plant = False
            self.is_show_button = False
            self.leasing_management_voucher_id.state = 'approved'

class InheritinsertCaWizard(models.TransientModel):
    _inherit = 'insert.ca.wizard'

    leasing_management_voucher_ids = fields.Many2many('lm.journal.voucher')

    def insert_ca(self):
        res = super(InheritinsertCaWizard, self).insert_ca()
        for rec in self:
            rec.insert_ca_leasing_management()

    def insert_ca_leasing_management(self):
        for data in self:
            document_to_insert = []            
            if data.leasing_management_voucher_ids:
                for lm in data.leasing_management_voucher_ids:
                    document_to_insert.append((0,0,{'leasing_management_voucher_id':lm.id,
                                                    'document_number':lm.name,
                                                    'document_type':'leasing_management_voucher',
                                                    'amount':lm.request_amount,
                                                      'create_document_date':lm.create_date
                                                    
                                                    }))
                    lm.is_insert_plant = True
            
                

            data.payment_plant_id.ca_payment_ids = document_to_insert



