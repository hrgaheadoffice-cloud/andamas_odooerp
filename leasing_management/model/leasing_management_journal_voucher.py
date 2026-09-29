# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, ValidationError

class LeasingManagementJournalVoucher(models.Model):
    _name = 'lm.journal.voucher'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "create_date desc, id desc"
    _description = "Leasing Management Journal Voucher"
    _rec_name = 'name'
    _check_company_auto = True

    def _get_default_currency_id(self):
        return self.env.company.currency_id.id

    @api.depends('lm_journal_voucher_ids.amount')
    def hitung_total(self):
        for order in self:
            amount_total = 0.0
            for line in order.lm_journal_voucher_ids:
                amount_total += line.amount
            order.update({
                'request_amount': amount_total,
            })

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

    @api.model
    def _default_warehouse(self):
        warehouse = self.env["stock.warehouse"]
        company_id = self.env.context.get("company_id") or self.env.company.id
        warehouse_id = warehouse.search(
            [("company_id", "=", company_id)]
        )
        return warehouse_id[:1]
 

    name = fields.Char('Document Number',index=True,default='New')
    journal_id = fields.Many2one('account.journal',string='Journal', store=True, readonly=False,
        compute='_compute_journal_id',
        domain="[('company_id', '=', company_id), ('type', 'in', ('bank', 'cash'))]")
    request_date = fields.Date('Request Date')
    available_partner_bank_ids = fields.Many2many(
        comodel_name='res.partner.bank',
        compute='_compute_available_partner_bank_ids',
        store=False
    )
    request_bank = fields.Many2one('res.partner.bank',
                                   string="Bank Reciveing",
                                   domain="[('id', 'in', available_partner_bank_ids)]",
                                   ondelete='restrict')
    request_amount = fields.Monetary('Amount Requested', readonly=False,compute='hitung_total',tracking=5)
    currency_id = fields.Many2one('res.currency', 'Currency', default=_get_default_currency_id, required=True)
    company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.company)
    # cost_center = fields.Many2one('account.cost.center', string='Cost Center', ondelete="restrict", index=True)
    checked_by  = fields.Many2one('res.users',string='Checked By',tracking=3,ondelete="cascade",)
    request_by = fields.Many2one('res.partner',string='Request By',tracking=3,ondelete="cascade",domain="[('type', '=', 'contact')]")
    prepaid_by = fields.Many2one('res.users',string='Prepared By',tracking=3,ondelete="cascade",default=lambda self: self.env.user)
    prepare_bydate = fields.Date(default=fields.Date.today())
    verify_by = fields.Many2one('res.users',string='Verify By',tracking=3,ondelete="cascade",)
    checked_by = fields.Many2one('res.users', 'Checked by')
    user_id = fields.Many2one(
        'res.users', string='Purchase Representative', index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("to_approve_matrix", "Tobe Approved Matrix"),
        ('approved', 'Approved'),
        ("waiting_on_payment", "Waiting On Payment"),
        ("done", "Done"),
        ("rejected",'Rejected')],default='draft',string='State',readonly=True,tracking=True)
    modul = fields.Char(
        string="Modul",
        readonly=True,
        default="Leasing Management Journal Voucher",
    )
    alasan_reject = fields.Text(
        string="Reason for Cancellation",
        track_visibility="onchange"
    )
    next_approver = fields.Many2one('res.users', 'Next Approval User', compute="_compute_next_approver", readonly=True,
                                    track_visibility="onchange", store=True)
    submit_dt = fields.Datetime('submit dt', readonly=True)
    payment_date = fields.Date('Payment Date')
    payment_bank = fields.Many2one('res.partner.bank', string="Payment Bank")
    lm_journal_voucher_ids = fields.One2many('lm.journal.voucher.line','lm_journal_voucher_id',string='Leasing Management Journal Voucher line',auto_join=True)
    acmove_ids = fields.One2many("account.move", 'lm_journal_voucher_id',string='Journal', copy=False,auto_join=True)
    jurnal_ids =  fields.One2many("account.move.line", related='acmove_ids.line_ids',string='Journal Items', copy=False,auto_join=True)
    user_pembuat = fields.Many2one('res.users', default=lambda self: self.env.user.id)
    warehouse_id = fields.Many2one('stock.warehouse',string='Location',default=_default_warehouse)
    is_insert_plant = fields.Boolean(default=False,copy=False)
    todo_user_ids = fields.Many2many(comodel_name="res.users",string="Next Approval",readonly=True,copy=False)
    leasing_management_id       = fields.Many2one('leasing.management','Leasing Management')
    leasing_management_line_id       = fields.Many2one('leasing.management.line','Leasing Management Line')
    activity = fields.Selection(
        [('Stockpile', 'Stockpile'),
         ('Hauling Internal', 'Hauling Internal'),
         ('Hauling Subcon', 'Hauling Subcon'),
         ('Rental', 'Rental'),
         ('Overburden', 'Overburden')],
        string='Activity',
        )
    # approval_matrix_ids = fields.One2many(
    #         comodel_name="approval.matrix",
    #         inverse_name="lm_journal_voucher_id",
    #         string="Approval Matrix",
    #         readonly=True,
    #         copy=False,
    #         track_visibility="onchange",
    #     )

    def button_approved_matrix(self):
        emp_id = self.env['approval.matrix'].search([('lm_journal_voucher_id','=',self.id),('realization_user_id','=',False)],limit=1,order="state asc")
        if emp_id:
            if self.env.uid in (emp_id.config_approval_matrix_id.approval_user_ids.ids) or emp_id.config_approval_matrix_id.delegate_user.id == self.env.uid:
                emp_id.write({'realization_user_id':self.env.uid,"date": fields.Datetime.now()})
                emp_id = self.env['approval.matrix'].search([('lm_journal_voucher_id','=',self.id),('realization_user_id','=',False)],limit=1,order="state asc")
                if not emp_id:
                    self.todo_user_ids = False
                    self.state = 'approved'
                else:
                    self.todo_user_ids = [(6, 0, emp_id.config_approval_matrix_id.approval_user_ids.ids)]
            else:
                raise UserError(
                    _("Anda tidak berhak melakukan proses ini"))

    def create_approval_matrix(self):
        obj_app = self.env['config.approval.matrix'].search([('modul','=',self.modul),('company_id','=',self.company_id.id),('tag_warehouse', 'in', self.warehouse_id.id),('expected_amount', '<=', self.request_amount)],order="matrix_level_name asc")  
        for item in obj_app:
            vals = {
                "lm_journal_voucher_id":self.id,
                "user_ids": [(6, 0, item.approval_user_ids.ids)],
                "matrix_level_id":item.matrix_level_id.id,
                "config_approval_matrix_id":item.id,
                "state":"Tobe Approved Mtrx "+ item.matrix_level_name,
                "name":"Tobe Approved Mtrx "+ item.matrix_level_name,
            }
            obj_create = self.env['approval.matrix'].create(vals)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'leasing.anagement.journal.voucher') or _('New')
        res = super(LeasingManagementJournalVoucher, self).create(vals)
        return res

    @api.depends('company_id')
    def _compute_journal_id(self):
        for wizard in self:
                wizard.journal_id = self.env['account.journal'].search([
                    ('type', 'in', ('bank', 'cash')),
                    ('company_id', '=', wizard.company_id.id),
                ], limit=1)

    def button_request_approval(self):
        if self.user_id.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.submit_dt = fields.Datetime.now()
        if self.name == '/':
            self.name = self.env["ir.sequence"].next_by_code("leasing.anagement.journal.voucher")
        self.state = 'approved'
        # self.approval_matrix_ids.unlink()
        # self.create_approval_matrix()
        # if not self.approval_matrix_ids:
        #     raise UserError(
        #         _("Approval Matrix not found, Please Check Config Approval Matrix"))
        # emp_id = self.env['approval.matrix'].search([('lm_journal_voucher_id','=',self.id),('realization_user_id','=',False)],limit=1,order="state asc")
        # if emp_id:
        #     self.todo_user_ids = [(6, 0, emp_id.config_approval_matrix_id.approval_user_ids.ids)]
        # self.state = 'to_approve_matrix'

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
        elif self.appr6:
            self.state = 'approved6'
        elif self.appr7:
            self.state = 'approved7'
        elif self.appr8:
            self.state = 'approved8'
        else:
            self.state = 'approved'
            # self.button_done_pr()
            super(LeasingManagementJournalVoucher, self).button_approve()

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
        elif self.appr6:
            self.state = 'approved6'
        elif self.appr7:
            self.state = 'approved7'
        elif self.appr8:
            self.state = 'approved8'
        else:
            self.state = 'approved'
            # self.button_done_pr()
            super(LeasingManagementJournalVoucher, self).button_approve()

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'approved']:
                continue
            order.write({'state': 'to approve'})
        return True

    
    def button_to_approve(self):
        emp_id = self.env['tbl_matrix_auth'].search(
            [('modul', '=', self.modul), ('level', '=', '1')],
            limit=1)
        if emp_id and not self.appr1:
            self.appr1 = self.env.user.id # emp_id.approval_user.id
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
        return super(LeasingManagementJournalVoucher,self).button_approve()


    def action_draft(self):
        return self.write({'state': 'draft'})

    def button_reject(self):
        return self.write({'state': 'rejected'})

    def register_payment(self):
        return {
            'name': _('Register Payment'),
            'res_model': 'leasing.management.payment',
            'view_mode': 'form',
            'context': {
                'active_model': 'lm.journal.voucher',
                'active_ids': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

class LeasingManagementJournalVoucherLi(models.Model):
    _name = "lm.journal.voucher.line"
    _description = "Leasing Management Journal Voucher Line"

    lm_journal_voucher_id = fields.Many2one(
        string="# Journal Voucher",
        comodel_name="lm.journal.voucher",
        required=True,
        ondelete="cascade",
    )
    currency_id = fields.Many2one('res.currency', 'Currency',related='lm_journal_voucher_id.currency_id', required=True)
    company_id = fields.Many2one('res.company', 'Company',related='lm_journal_voucher_id.company_id')
    
    amount = fields.Float(digits='Product Price',string='Estimated Amount')
    description = fields.Text('Description')
    account_id     = fields.Many2one('account.account','Account')

# class InheritApprovalMatrixJV(models.Model):
#     _inherit = "approval.matrix"

#     lm_journal_voucher_id = fields.Many2one('lm.journal.voucher','Journal voucher')