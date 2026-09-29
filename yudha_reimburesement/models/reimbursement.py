# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, ValidationError

class Reimbursement(models.Model):
    _name = 'reimbursement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "create_date desc, id desc"
    _description = "Reimbursement"
    _rec_name = 'name'
    _check_company_auto = True

    def _get_default_currency_id(self):
        return self.env.company.currency_id.id

    @api.depends('reimbursement_ids.amount','reimbursement_ids.state')
    def hitung_total(self):
        for order in self:
            amount_total = 0.0
            # order.update({"over_due": order.ca_id.amount_ca})
            if order.reimbursement_ids:
                for line in order.reimbursement_ids.filtered(lambda x: x.state=='approved'):
                    amount_total += line.final_amount
                order.update({
                    'request_amount': amount_total,
                })
            else:
                order.update({
                    'request_amount': 0.0,
                })
    # @api.depends('journal_id')
    # def _compute_available_partner_bank_ids(self):
    #     for alldata in self:
    #         allbank = self.env['res.partner.bank'].sudo().search([])
    #         databank = []
    #         for mybank in allbank:
    #             myjournal = mybank.journal_id.filtered(lambda x: x.id == alldata.journal_id.id)
    #             if myjournal:
    #                 for alljurnal in myjournal:
    #                     databank.append(alljurnal.bank_account_id.id)
    #         if databank != []:
    #             caribank = self.env['res.partner.bank'].sudo().search([('id','in',databank)])
    #             alldata.available_partner_bank_ids = [(6,0,caribank.ids)]
    #         else:
    #             alldata.available_partner_bank_ids = False


    name = fields.Char('Document Number',index=True,default='New')
    # journal_id = fields.Many2one('account.journal',string='Journal', store=True, readonly=False,
    #     compute='_compute_journal_id',
    #     domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")
    request_date = fields.Date('Request Date')
    # available_partner_bank_ids = fields.Many2many(
    #     comodel_name='res.partner.bank',
    #     compute='_compute_available_partner_bank_ids',
    #     store=False
    # )
    # request_bank = fields.Many2one('res.partner.bank',
    #                                string="Bank Reciveing",
    #                                domain="[('id', 'in', available_partner_bank_ids)]",
    #                                ondelete='restrict')

    request_amount = fields.Monetary('Amount Requested', readonly=False,compute='hitung_total',store=False,tracking=5)
    currency_id = fields.Many2one('res.currency', 'Currency', default=_get_default_currency_id, required=True)
    company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.company)
    cost_center = fields.Many2one('account.cost.center', string='Cost Center', ondelete="restrict", index=True)
    checked_by  = fields.Many2one('res.users',string='Checked By',tracking=3,ondelete="cascade",)
    request_by = fields.Many2one('res.partner',string='Request By',tracking=3,ondelete="cascade",domain="[('type', '=', 'contact')]")
    prepaid_by = fields.Many2one('res.users',string='Prepared By',tracking=3,ondelete="cascade",default=lambda self: self.env.user)
    prepare_bydate = fields.Date(default=fields.Date.today())
    verify_by = fields.Many2one('res.users',string='Verify By',tracking=3,ondelete="cascade",)
    verify_by = fields.Many2one('res.users',string='Verify By',tracking=3,ondelete="cascade",)
    checked_by = fields.Many2one('res.users', 'Checked by')
    user_id = fields.Many2one(
        'res.users', string='Purchase Representative', index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)
    appr1 = fields.Many2one('res.users', 'Approved by')
    state = fields.Selection([
        ("draft", "Draft"),
        ("approved1", "Tobe Approved"),
        ("approved2", "Tobe Approved 2"),
        ("approved3", "Tobe Approved 3"),
        ("approved4", "Tobe Approved 4"),
        ("approved5", "Tobe Approved 5"),
        ("approved", "Approved"),
        ("waiting_on_payment", "Waiting On Payment"),
        ("done", "Done"),
        ("rejected", 'Rejected')], default='draft', string='State', readonly=True)

    state_a = fields.Selection(related='state')
    state_b = fields.Selection(related='state')
    state_c = fields.Selection(related='state')
    state_d = fields.Selection(related='state')
    state_e = fields.Selection(related='state')

    READONLY_STATES = {

        "done": [("readonly", True)],
        "rejected": [("readonly", True)],
        "waiting_on_payment": [("readonly", True)],
        "approved1": [("readonly", True)],
        "approved2": [("readonly", True)],
        "approved3": [("readonly", True)],
        "approved4": [("readonly", True)],
        "approved5": [("readonly", True)],
        "approved6": [("readonly", True)],
        "approved7": [("readonly", True)],
        "approved8": [("readonly", True)],
        "approved": [("readonly", True)],
        "to_check": [("readonly", True)],
        "to_verify": [("readonly", True)],
    }
    appr1_dt = fields.Datetime('appr1 dt', readonly=True)
    appr1_view = fields.Boolean('appr1 view', readonly=True)
    appr2 = fields.Many2one('res.users', 'Approved by', compute='_default_approval', store=False)
    appr2_dt = fields.Datetime('appr1 dt', readonly=True)
    appr2_view = fields.Boolean('appr1 view', readonly=True)
    appr3 = fields.Many2one('res.users', 'Approved by', compute='_default_approval', store=False)
    appr3_dt = fields.Datetime('appr1 dt', readonly=True)
    appr3_view = fields.Boolean('appr1 view', readonly=True)
    appr4 = fields.Many2one('res.users', 'Approved by', compute='_default_approval', store=False)
    appr4_dt = fields.Datetime('appr1 dt', readonly=True)
    appr4_view = fields.Boolean('appr1 view', readonly=True)
    appr5 = fields.Many2one('res.users', 'Approved by', compute='_default_approval', store=False)
    appr5_dt = fields.Datetime('appr1 dt', readonly=True)
    appr5_view = fields.Boolean('appr1 view', readonly=True)
    appr6 = fields.Many2one('res.users', 'Approved by', compute='_default_approval', store=False)
    appr6_dt = fields.Datetime('appr1 dt', readonly=True)
    appr6_view = fields.Boolean('appr1 view', readonly=True)
    appr7 = fields.Many2one('res.users', 'Approved by', compute='_default_approval', store=False)
    appr7_dt = fields.Datetime('appr1 dt', readonly=True)
    appr7_view = fields.Boolean('appr1 view', readonly=True)
    appr8 = fields.Many2one('res.users', 'Approved by', compute='_default_approval', store=False)
    appr8_dt = fields.Datetime('appr1 dt', readonly=True)
    appr8_view = fields.Boolean('appr1 view', readonly=True)
    approval_stage = fields.Integer(compute='_compute_approval_stage')
    modul = fields.Char(
        string="Modul",
        readonly=True,
        default="Reimbursement",
    )
    alasan_reject = fields.Text(
        string="Reason for Cancellation",
        track_visibility="onchange"
    )
    next_approver = fields.Many2one('res.users', 'Next Approval User', compute="_compute_next_approver", readonly=True,
                                    track_visibility="onchange", store=True)
    next_approver_ids = fields.Many2many('res.users', compute='_compute_next_approver_ids')
    submit_dt = fields.Datetime('submit dt', readonly=True)
    payment_date = fields.Date('Payment Date')
    payment_bank = fields.Many2one('res.partner.bank', string="Payment Bank")
    reimbursement_ids = fields.One2many('reimbursement.line','reimbursement_id',string='Reimbursement Details',auto_join=True)
    acmove_ids = fields.One2many("account.move", 'reimbursement_id',string='Journal', copy=False,auto_join=True)
    jurnal_ids =  fields.One2many("account.move.line", related='acmove_ids.line_ids',string='Journal Items', copy=False,auto_join=True)
    user_pembuat = fields.Many2one('res.users', default=lambda self: self.env.user.id)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'reimbursement') or _('New')
        res = super(Reimbursement, self).create(vals)
        return res

    # @api.depends('company_id')
    # def _compute_journal_id(self):
    #     for wizard in self:
    #             wizard.journal_id = self.env['account.journal'].search([
    #                 ('type', 'in', ('bank', 'cash')),
    #                 ('company_id', '=', wizard.company_id.id),
    #             ], limit=1)

    @api.depends('state')
    def _compute_next_approver_ids(self):
        for rec in self:
            if rec.state == 'approved1':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Reimbursement'), ('level', '=', '1')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved2':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Reimbursement'), ('level', '=', '2')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved3':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Reimbursement'), ('level', '=', '3')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved4':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Reimbursement'), ('level', '=', '4')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved5':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Reimbursement'), ('level', '=', '5')]).approval_user
                rec.next_approver_ids = next_approver
            else:
                rec.next_approver_ids = False

    def _compute_approval_stage(self):
        for rec in self:
            approval_stage = 0
            emp_id = rec.env['tbl_matrix_auth'].search([('modul', '=', 'Reimbursement')])
            rec.approval_stage = len(emp_id)
        return


    @api.depends("state", "user_id", "checked_by", "verify_by", "appr1", "appr2", "appr3", "appr4", "appr5")
    def _compute_next_approver(self):
        for rec in self:
            if rec.state == 'draft' and rec.user_id:
                rec.next_approver = rec.user_id.id
            elif rec.state == 'to_check' and rec.checked_by:
                rec.next_approver = rec.checked_by.id
            elif rec.state == 'to_verify' and rec.verify_by:
                rec.next_approver = rec.verify_by.id
            elif rec.state == 'approved1' and rec.appr1:
                rec.next_approver = rec.appr1.id
            elif rec.state == 'approved2' and rec.appr2:
                rec.next_approver = rec.appr2.id
            elif rec.state == 'approved3' and rec.appr3:
                rec.next_approver = rec.appr3.id
            elif rec.state in ('approved4',) and rec.appr4:
                rec.next_approver = rec.appr4.id
            elif rec.state in ('approved5',) and rec.appr5:
                rec.next_approver = rec.appr5.id
            else:
                rec.next_approver = False


    def button_check(self):
        if self.checked_by.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))

        # if self.checked_by:
        #         self.state = 'to_check'
        self.checked_dt = fields.Datetime.now()
        if self.verify_by:
            self.state = 'to_verify'
        elif self.appr1:
            self.state = 'approved1'
        elif self.appr2:
            self.state = 'approved2'
        elif self.appr3:
            self.state = 'approved3'
        elif self.appr4:
            self.state = 'approved4'
        elif self.appr5:
            self.state = 'approved5'
        else:
            self.state = 'approved'
            # self.button_done_pr()
            super(Reimbursement, self).button_approve()

    def button_verify(self):
        if self.verify_by.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.verified_dt = fields.Datetime.now()

        if self.appr1:
            self.state = 'approved1'
        elif self.appr2:
            self.state = 'approved2'
        elif self.appr3:
            self.state = 'approved3'
        elif self.appr4:
            self.state = 'approved4'
        elif self.appr5:
            self.state = 'approved5'
        else:
            self.state = 'approved'
            # self.button_done_pr()
            super(Reimbursement, self).button_approve()

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'approved']:
                continue
            order.write({'state': 'to approve'})
        return True

    def button_appr1(self):
        if self.env.user not in self.next_approver_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr1 = self.env.user
        self.appr1_dt = fields.Datetime.now()
        if self.approval_stage > 1:
            self.state = 'approved2'
        else:
            self.state = 'approved'

    def button_appr2(self):
        if self.env.user not in self.next_approver_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr2 = self.env.user
        self.appr2_dt = fields.Datetime.now()
        if self.approval_stage > 2:
            self.state = 'approved3'
        else:
            self.state = 'approved'

    def button_appr3(self):
        if self.env.user not in self.next_approver_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr3 = self.env.user
        self.appr3_dt = fields.Datetime.now()
        if self.approval_stage > 3:
            self.state = 'approved4'
        else:
            self.state = 'approved'

    def button_appr4(self):
        if self.env.user not in self.next_approver_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr4 = self.env.user
        self.appr4_dt = fields.Datetime.now()
        if self.approval_stage > 4:
            self.state = 'approved5'
        else:
            self.state = 'approved'

    def button_appr5(self):
        if self.env.user not in self.next_approver_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr5 = self.env.user
        self.appr5_dt = fields.Datetime.now()
        self.state = 'approved'

    def button_to_approve(self):
        emp_id = self.env['tbl_matrix_auth'].search(
            [('modul', '=', self.modul), ('level', '=', '1')],
            limit=1)
        if emp_id and not self.appr1:
            self.appr1 = emp_id.approval_user.id
        if emp_id:
            if self.appr1 not in emp_id.approval_user:
                raise UserError(
                    _("Invalid Approval User"))
        self.state = 'approved1'

    def button_approve(self):
        if not self.ca_ids:
            raise UserError(
                 _("The product line must be filled in."))

        if self.user_id.id != self.env.uid:
            raise UserError(
                 _("Anda tidak berhak melakukan proses ini"))
        status = 'approved1'
        if self.checked_by:
            # if self.checked_by.id == self.env.uid:
            #     if self.verify_by.id != self.env.uid:
            #         self.checked_dt = fields.Datetime.now()
            #         status = 'to_verify'
            # else:
                status = 'to_check'
                self.todo_user = self.checked_by.id
        else:
            if self.verify_by:
                status = 'to_verify'
                self.todo_user = self.verify_by.id

        # two_steps_purchase_approval.write({"state": status})
        # one_step_purchase_approval = self - two_steps_purchase_approval
        self.submit_dt = fields.Datetime.now()
        emp_id = self.env['tbl_matrix_auth'].search([('modul', '=', self.modul),('level', '=', '1')], limit=1)
        if emp_id:
            if not self.appr1:
                self.appr1 = emp_id.approval_user.id
                self.todo_user = emp_id.approval_user.id
            else:
                self.todo_user = self.appr1.id
        else:
            # raise UserError(
            #         _('Tidak ditemukan pada Matrix Auth')
            #     )
            if not self.appr1:
                raise UserError(
                        _('Approved by 1 Harus di isi')
                    )
            self.todo_user = self.appr1.id
        return super(Reimbursement,self).button_approve()


    def register_payment(self):
        return {
            'name': _('Register Payment'),
            'res_model': 'reimbursement.payment',
            'view_mode': 'form',
            'context': {
                'active_model': 'reimbursement',
                'active_ids': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


    def action_draft(self):
        return self.write({'state': 'draft'})

    def button_reject(self):
        self.appr1_dt = ''
        self.appr2_dt = ''
        self.appr3_dt = ''
        self.appr4_dt = ''
        self.appr5_dt = ''
        self.appr1 = False
        self.appr2 = False
        self.appr3 = False
        self.appr4 = False
        self.appr5 = False
        return self.write({'state': 'rejected'})


class ReimbursementLine(models.Model):
    _name = "reimbursement.line"
    _description = "Reimbursement Line"

    reimbursement_id = fields.Many2one(
        string="# Employee Reimbursement",
        comodel_name="reimbursement",
        required=True,
        ondelete="cascade",
    )
    state_id = fields.Selection(related='reimbursement_id.state',readonly=True, copy=False, index=True, tracking=3)
    state = fields.Selection([
        ('approved', 'Approved'),
        ('rejected','Rejected'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='approved')
    currency_id = fields.Many2one('res.currency', 'Currency',related='reimbursement_id.currency_id', required=True)
    company_id = fields.Many2one('res.company', 'Company',related='reimbursement_id.company_id')
    domain_product = fields.Many2many('product.product','reimbursement_line_rel',string='Domain Product',compute='category_expense',store=False)
    # product_id = fields.Many2one('product.product','Product Name',index=True,domain="[('can_be_expensed', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", ondelete='restrict')
    product_id = fields.Many2one('product.product','Product Name',index=True,domain="[('id','in',domain_product)]", ondelete='restrict')

    amount = fields.Float(digits='Product Price',string='Estimated Amount')
    is_approved = fields.Boolean('Is Approved',default=False)
    is_rejected = fields.Boolean('Is Rejected',default=False)
    alasan = fields.Text('Reason',index=True)
    description = fields.Text('Description')
    cost_center = fields.Many2one('account.cost.center',string='Cost Center',ondelete="restrict",index=True)

    percentage = fields.Integer('Percentage (%)',default=100)
    final_amount = fields.Float(digits='Product Price',string='Amount',compute='_hitung_final')


    @api.onchange('percentage')
    def cek_max(self):
        for alldata in self:
            if not alldata.percentage:
                return
            if alldata.percentage > 100:
                alldata.percentage = 100

    @api.depends('amount','percentage')
    def _hitung_final(self):
        for alldata in self:
            if not alldata.percentage:
                alldata.final_amount =0.0
            else:
                alldata.final_amount = alldata.percentage / 100 * alldata.amount
    @api.depends('reimbursement_id','state')
    def category_expense(self):
        for alldata in self:
            allprod =self.env['product.product'].sudo().search([])
            myprod = allprod.filtered(lambda p:p.can_be_expensed==True)
            alldata.domain_product =[(6,0,myprod.ids)]

    def action_approved(self):
        return {
            'name': _('Approve Reason'),
            'res_model': 'reimbursement.reason.wiz',
            'view_mode': 'form',
            'context': {
                'active_model': 'cash.advance',
                'active_ids': self.id,
                'tindakan': 'approved',
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

        # for allrec in self:
        #     if not allrec.product_id:
        #         raise UserWarning("Please Insert Product First")
        # return self.write({'is_approved': True ,'is_rejected': False,'state':'approved'})

    def action_rejected(self):
        return {
            'name': _('Rejected Reason'),
            'res_model': 'reimbursement.reason.wiz',
            'view_mode': 'form',
            'context': {
                'active_model': 'cash.advance',
                'active_ids': self.id,
                'tindakan': 'rejected',
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_type = fields.Selection(string='Company Type',
        selection=[('person', 'Individual'), ('company', 'Company')],
        compute='_compute_company_type', inverse='_write_company_type',store=True)


class tbl_matrix_auth(models.Model):
    _inherit = "tbl_matrix_auth"

    modul = fields.Selection(selection_add=[('Reimbursement', 'Reimbursement')])