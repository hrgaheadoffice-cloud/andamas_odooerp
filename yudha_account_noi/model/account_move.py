# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from collections import defaultdict


class AccountMove(models.Model):
    _inherit = 'account.move'


    @api.depends('line_ids.debit', 'line_ids.credit')
    def _amount_noi(self):
        for rec in self:
            total_debit = 0.0
            total_credit = 0.0
            for line in rec.line_ids:
                total_debit += line.debit
                total_credit += line.credit
            amount = abs(total_debit-total_credit)
            rec.update({
                'amount': amount
            })

    @api.model
    def _default_noi_warehouse(self):
        warehouse = self.env["stock.warehouse"]
        company_id = self.env.context.get("company_id") or self.env.company.id
        warehouse_id = warehouse.search(
            [("company_id", "=", company_id)]
        )
        return warehouse_id[:1]

    is_noi_ho = fields.Boolean()
    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money'),
    ], string='Payment Type', default='inbound', required=True)
    amount = fields.Float(compute=_amount_noi)
    show_amount = fields.Float('Amount')

    noichecked_by = fields.Many2one('res.users', string='Checked By', tracking=3, ondelete="cascade", )
    noirequest_by = fields.Many2one('res.partner', string='Request By', tracking=3, ondelete="cascade", domain="[('type', '=', 'contact')]")
    noiprepaid_by = fields.Many2one('res.users', string='Prepared By', tracking=3, ondelete="cascade",
                                       default=lambda self: self.env.user)
    noiprepare_bydate = fields.Datetime(default=fields.Date.today())
    noiverify_by = fields.Many2one('res.users', string='Verify By', tracking=3, ondelete="cascade", )
    noiverify_by = fields.Many2one('res.users', string='Verify By', tracking=3, ondelete="cascade", )
    noichecked_by = fields.Many2one('res.users', 'Checked by')
    noi_user_id = fields.Many2one(
        'res.users', string='Purchase Representative', index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)
    noiappr1 = fields.Many2one('res.users', 'Approved by', compute='_default_noiapproval', store=False)
    noi_state_new = fields.Selection([
        ("draft", "Draft"),
        ("approved1", "Tobe approved"),
        ("approved2", "Tobe approved 2"),
        ("approved3", "Tobe approved 3"),
        ("approved4", "Tobe approved 4"),
        ("approved5", "Tobe approved 5"),
        ("approved6", "Tobe approved 6"),
        ("approved7", "Tobe approved 7"),
        ("approved8", "Tobe approved 8"),
        ("approved", "approved"),
        ("waiting_on_payment", "Waiting On Payment"),
        ("posted", "Posted"),
        ('cancel', 'Cancelled'),
        ("rejected", 'Rejected')], default='draft', string='noi_state_new', readonly=True)

    noi_state_new_a = fields.Selection(related='noi_state_new')
    noi_state_new_b = fields.Selection(related='noi_state_new')
    noi_state_new_c = fields.Selection(related='noi_state_new')
    noi_state_new_d = fields.Selection(related='noi_state_new')
    noi_state_new_e = fields.Selection(related='noi_state_new')
    noi_state_new_f = fields.Selection(related='noi_state_new')
    noi_state_new_g = fields.Selection(related='noi_state_new')
    noi_state_new_h = fields.Selection(related='noi_state_new')
    READONLY_noi_state_newS = {
        "done": [("readonly", True)],
        "rejected": [("readonly", True)],
        "approved1": [("readonly", True)],
        "approved2": [("readonly", True)],
        "approved3": [("readonly", True)],
        "approved4": [("readonly", True)],
        "approved5": [("readonly", True)],
        "approved6": [("readonly", True)],
        "approved7": [("readonly", True)],
        "approved8": [("readonly", True)],
        "approved": [("readonly", True)],
    }
    noiappr1_dt = fields.Datetime('noiappr1 dt', readonly=True)
    noiappr1_view = fields.Boolean('noiappr1 view', readonly=True)
    noiappr2 = fields.Many2one('res.users', 'Approved by', compute='_default_noiapproval', store=False)
    noiappr2_dt = fields.Datetime('noiappr1 dt', readonly=True)
    noiappr2_view = fields.Boolean('noiappr1 view', readonly=True)
    noiappr3 = fields.Many2one('res.users', 'Approved by', compute='_default_noiapproval', store=False)
    noiappr3_dt = fields.Datetime('noiappr1 dt', readonly=True)
    noiappr3_view = fields.Boolean('noiappr1 view', readonly=True)
    noiappr4 = fields.Many2one('res.users', 'Approved by', compute='_default_noiapproval', store=False)
    noiappr4_dt = fields.Datetime('noiappr1 dt', readonly=True)
    noiappr4_view = fields.Boolean('noiappr1 view', readonly=True)
    noiappr5 = fields.Many2one('res.users', 'Approved by', compute='_default_noiapproval', store=False)
    noiappr5_dt = fields.Datetime('noiappr1 dt', readonly=True)
    noiappr5_view = fields.Boolean('noiappr1 view', readonly=True)
    noiappr6 = fields.Many2one('res.users', 'Approved by', compute='_default_noiapproval', store=False)
    noiappr6_dt = fields.Datetime('noiappr1 dt', readonly=True)
    noiappr6_view = fields.Boolean('noiappr1 view', readonly=True)
    noiappr7 = fields.Many2one('res.users', 'Approved by', compute='_default_noiapproval', store=False)
    noiappr7_dt = fields.Datetime('noiappr1 dt', readonly=True)
    noiappr7_view = fields.Boolean('noiappr1 view', readonly=True)
    noiappr8 = fields.Many2one('res.users', 'Approved by', compute='_default_noiapproval', store=False)
    noiappr8_dt = fields.Datetime('noiappr1 dt', readonly=True)
    noiappr8_view = fields.Boolean('noiappr1 view', readonly=True)
    noi_approval_stage = fields.Integer()
    modul = fields.Char(
        string="NOI Modul",
        readonly=True,
        default="NOI HO",
    )
    noi_alasan_reject = fields.Text(
        string="Reason for Cancellation",
        track_visibility="onchange"
    )
    next_noiapprover = fields.Many2one('res.users', 'Next noiapproval User',
                                          compute="_compute_next_noiapprover", readonly=True,
                                          track_visibility="onchange", store=True)
    next_noiapprover_ids = fields.Many2many('res.users', compute='_compute_next_noiapprover_ids')
    submit_noidt = fields.Datetime('submit dt', readonly=True)
    noi_warehouse_id = fields.Many2one('stock.warehouse',string='Location',default=_default_noi_warehouse)
    is_insert_plant = fields.Boolean(default=False,copy=False)

    @api.model
    def create(self, vals):
        myctx = self._context.get('default_is_noi_ho')
        if myctx != None:
            if myctx != False:
                print('ini kq kemari terus ', myctx)
                vals['is_noi_ho'] = True
                if 'reversed_entry_id' not in vals:
                    line_vals = {}
                    journal_id = vals.get('journal_id')
                    account_id = self.env['account.journal'].browse(journal_id).default_account_id.id
                    line_vals['account_id'] = account_id
                    if vals.get('payment_type') == 'outbound':
                        line_vals['credit'] = vals.get('amount')
                    else:
                        line_vals['debit'] = vals.get('amount')
                    if vals.get('line_ids') != None:
                        vals.get('line_ids').append([0, 0, line_vals])
                    vals['show_amount'] = vals.get('show_amount_noi')
                # if 'company_id' in vals:
                #     self = self.with_company(vals['company_id'])
                # vals['name'] = self.env['ir.sequence'].next_by_code('account.noi.number') or '/'
        res = super(AccountMove, self).create(vals)
        return res

    @api.depends('noi_state_new')
    def _default_noiapproval(self):
        for allrec in self:
            allrec.noi_approval_stage = 0
            allnoiapproval = self.env['tbl_matrix_auth'].search(
                [('modul', '=', 'NOI HO'), ('company_id', '=', self.company_id.id),('tag_warehouse', 'in', allrec.noi_warehouse_id.id), ('value_awal', '<=', allrec.show_amount)])
            if not allnoiapproval and allrec.noi_state_new != 'draft':
                raise UserError("Please Setting Matrix Approval For NOI HO first ")
            else:
                allrec.noi_approval_stage = len(allnoiapproval)
                allrec.noiappr1 = allnoiapproval.filtered(lambda e: e.level == '1').approval_user.id if allnoiapproval.filtered(lambda e: e.level == '1') else False
                allrec.noiappr2 = allnoiapproval.filtered(lambda e: e.level == '2').approval_user.id if allnoiapproval.filtered(lambda e: e.level == '2') else False
                allrec.noiappr3 = allnoiapproval.filtered(lambda e: e.level == '3').approval_user.id if allnoiapproval.filtered(lambda e: e.level == '3') else False
                allrec.noiappr4 = allnoiapproval.filtered(lambda e: e.level == '4').approval_user.id if allnoiapproval.filtered(lambda e: e.level == '4') else False
                allrec.noiappr5 = allnoiapproval.filtered(lambda e: e.level == '5').approval_user.id if allnoiapproval.filtered(lambda e: e.level == '5') else False
                allrec.noiappr6 = allnoiapproval.filtered(lambda e: e.level == '6').approval_user.id if allnoiapproval.filtered(lambda e: e.level == '6') else False
                allrec.noiappr7 = allnoiapproval.filtered(lambda e: e.level == '7').approval_user.id if allnoiapproval.filtered(lambda e: e.level == '7') else False
                allrec.noiappr8 = allnoiapproval.filtered(lambda e: e.level == '8').approval_user.id if allnoiapproval.filtered(lambda e: e.level == '8') else False

    @api.depends('noi_state_new')
    def _compute_next_noiapprover_ids(self):
        for rec in self:
            if rec.noi_state_new == 'approved1':
                next_noiapprover = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'NOI HO'), ('level', '=', '1')]).approval_user
                rec.next_noiapprover_ids = next_noiapprover
            elif rec.noi_state_new == 'approved2':
                next_noiapprover = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'NOI HO'), ('level', '=', '2')]).approval_user
                rec.next_noiapprover_ids = next_noiapprover
            elif rec.noi_state_new == 'approved3':
                next_noiapprover = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'NOI HO'), ('level', '=', '3')]).approval_user
                rec.next_noiapprover_ids = next_noiapprover
            elif rec.noi_state_new == 'approved4':
                next_noiapprover = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'NOI HO'), ('level', '=', '4')]).approval_user
                rec.next_noiapprover_ids = next_noiapprover
            elif rec.noi_state_new == 'approved5':
                next_noiapprover = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'NOI HO'), ('level', '=', '5')]).approval_user
                rec.next_noiapprover_ids = next_noiapprover
            elif rec.noi_state_new == 'approved6':
                next_noiapprover = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'NOI HO'), ('level', '=', '6')]).approval_user
                rec.next_noiapprover_ids = next_noiapprover
            elif rec.noi_state_new == 'approved7':
                next_noiapprover = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'NOI HO'), ('level', '=', '7')]).approval_user
                rec.next_noiapprover_ids = next_noiapprover
            elif rec.noi_state_new == 'approved8':
                next_noiapprover = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'NOI HO'), ('level', '=', '8')]).approval_user
                rec.next_noiapprover_ids = next_noiapprover
            else:
                rec.next_noiapprover_ids = False


    @api.depends('noi_state_new',)
    def _compute_noi_approval_stage (self):
        for rec in self:
            rec.noi_approval_stage = 0
            emp_id = rec.env['tbl_matrix_auth'].search([('modul', '=', 'NOI HO')])
            print('total aoproval ', len(emp_id))
            rec.noi_approval_stage = len(emp_id)
        return



    @api.depends("noi_state_new", "noi_user_id", "noichecked_by", "noiverify_by", "noiappr1", "noiappr2", "noiappr3", "noiappr4", "noiappr5","noiappr6", "noiappr7", "noiappr8")
    def _compute_next_noiapprover(self):
        for rec in self:
            if rec.noi_state_new == 'draft' and rec.noi_user_id:
                rec.next_noiapprover = rec.noi_user_id.id
            elif rec.noi_state_new == 'to_check' and rec.checked_by:
                rec.next_noiapprover = rec.checked_by.id
            elif rec.noi_state_new == 'to_verify' and rec.verify_by:
                rec.next_noiapprover = rec.verify_by.id
            elif rec.noi_state_new == 'approved1' and rec.noiappr1:
                rec.next_noiapprover = rec.noiappr1.id
            elif rec.noi_state_new == 'approved2' and rec.noiappr2:
                rec.next_noiapprover = rec.noiappr2.id
            elif rec.noi_state_new == 'approved3' and rec.noiappr3:
                rec.next_noiapprover = rec.noiappr3.id
            elif rec.noi_state_new in ('approved4',) and rec.noiappr4:
                rec.next_noiapprover = rec.noiappr4.id
            elif rec.noi_state_new in ('approved5',) and rec.noiappr5:
                rec.next_noiapprover = rec.noiappr5.id
            elif rec.noi_state_new == 'approved6' and rec.noiappr6:
                rec.next_noiapprover = rec.noiappr6.id
            elif rec.noi_state_new in ('approved7',) and rec.noiappr7:
                rec.next_noiapprover = rec.noiappr7.id
            elif rec.noi_state_new in ('approved8',) and rec.noiappr8:
                rec.next_noiapprover = rec.noiappr8.id
            else:
                rec.next_noiapprover = False


    def button_check(self):
        if self.checked_by.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))

        # if self.checked_by:
        #         self.noi_state_new = 'to_check'
        self.checked_dt = fields.Datetime.now()
        if self.verify_by:
            self.noi_state_new = 'to_verify'
        elif self.noiappr1:
            self.noi_state_new = 'approved1'
        elif self.noiappr2:
            self.noi_state_new = 'approved2'
        elif self.noiappr3:
            self.noi_state_new = 'approved3'
        elif self.noiappr4:
            self.noi_state_new = 'approved4'
        elif self.noiappr5:
            self.noi_state_new = 'approved5'
        elif self.noiappr6:
            self.noi_state_new = 'approved6'
        elif self.noiappr7:
            self.noi_state_new = 'approved7'
        elif self.noiappr8:
            self.noi_state_new = 'approved8'
        else:
            self.noi_state_new = 'approved'
            # self.button_done_pr()
            super(Reimbursementho, self).button_noiapprove()

    def button_verify(self):
        if self.verify_by.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.verified_dt = fields.Datetime.now()

        if self.noiappr1:
            self.noi_state_new = 'approved1'
        elif self.noiappr2:
            self.noi_state_new = 'approved2'
        elif self.noiappr3:
            self.noi_state_new = 'approved3'
        elif self.noiappr4:
            self.noi_state_new = 'approved4'
        elif self.noiappr5:
            self.noi_state_new = 'approved5'
        elif self.noiappr6:
            self.noi_state_new = 'approved6'
        elif self.noiappr7:
            self.noi_state_new = 'approved7'
        elif self.noiappr8:
            self.noi_state_new = 'approved8'
        else:
            self.noi_state_new = 'approved'
            # self.button_done_pr()
            super(CashAdvance, self).button_noiapprove()

    def button_noi_to_approve(self):
        for order in self:
            if order.noi_state_new not in ['draft', 'sent', 'approved']:
                continue
            order.write({'noi_state_new': 'approved1'})
        return True

    def button_noiappr1(self):
        if self.env.user not in self.next_noiapprover_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.noiappr1 = self.env.user
        self.noiappr1_dt = fields.Datetime.now()
        if self.noi_approval_stage > 1:
            self.noi_state_new = 'approved2'
        else:
            self.noi_state_new = 'approved'

    def button_noiappr2(self):
        if self.env.user not in self.next_noiapprover_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.noiappr2 = self.env.user
        self.noiappr2_dt = fields.Datetime.now()
        if self.noi_approval_stage > 2:
            self.noi_state_new = 'approved3'
        else:
            self.noi_state_new = 'approved'

    def button_noiappr3(self):
        if self.env.user not in self.next_noiapprover_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.noiappr3 = self.env.user
        self.noiappr3_dt = fields.Datetime.now()
        if self.noi_approval_stage > 3:
            self.noi_state_new = 'approved4'
        else:
            self.noi_state_new = 'approved'

    def button_noiappr4(self):
        if self.env.user not in self.next_noiapprover_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.noiappr4 = self.env.user
        self.noiappr4_dt = fields.Datetime.now()
        if self.noi_approval_stage > 4:
            self.noi_state_new = 'approved5'
        else:
            self.noi_state_new = 'approved'

    def button_noiappr5(self):
        if self.env.user not in self.next_noiapprover_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.noiappr5 = self.env.user
        self.noiappr5_dt = fields.Datetime.now()
        if self.noi_approval_stage > 5:
            self.noi_state_new = 'approved6'
        else:
            self.noi_state_new = 'approved'


    def button_noiappr6(self):
        if self.env.user not in self.next_noiapprover_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.noiappr6 = self.env.user
        self.noiappr6_dt = fields.Datetime.now()
        if self.noi_approval_stage > 6:
            self.noi_state_new = 'approved7'
        else:
            self.noi_state_new = 'approved'

    def button_noiappr7(self):
        if self.env.user not in self.next_noiapprover_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.noiappr7 = self.env.user
        self.noiappr7_dt = fields.Datetime.now()
        if self.noi_approval_stage > 7:
            self.noi_state_new = 'approved8'
        else:
            self.noi_state_new = 'approved'
    def button_noiappr8(self):
        if self.env.user not in self.next_noiapprover_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.noiappr8 = self.env.user
        self.noiappr8_dt = fields.Datetime.now()
        self.noi_state_new = 'approved'
    def button_to_noiapprove(self):
        emp_id = self.env['tbl_matrix_auth'].search(
            [('modul', '=', self.modul), ('level', '=', '1')],
            limit=1)
        if emp_id and not self.noiappr1:
            self.noiappr1 = self.env.user.id # emp_id.approval_user.id
        if emp_id:
            if self.noiappr1 not in emp_id.approval_user:
                raise UserError(
                    _("Invalid noiapproval User"))
        self.noi_state_new = 'approved1'


    def button_noiapprove(self):
        if not self.ca_ids:
            raise UserError(
                 _("The product line must be filled in."))

        if self.noi_user_id.id != self.env.uid:
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

        # two_steps_purchase_noiapproval.write({"noi_state_new": status})
        # one_step_purchase_noiapproval = self - two_steps_purchase_noiapproval
        self.submit_dt = fields.Datetime.now()
        emp_id = self.env['tbl_matrix_auth'].search([('modul', '=', self.modul),('level', '=', '1')], limit=1)
        if emp_id:
            if not self.noiappr1:
                self.noiappr1 = emp_id.approval_user.id
                self.todo_user = emp_id.approval_user.id
            else:
                self.todo_user = self.noiappr1.id
        else:
            # raise UserError(
            #         _('Tidak ditemukan pada Matrix Auth')
            #     )
            if not self.noiappr1:
                raise UserError(
                        _('approved by 1 Harus di isi')
                    )
            self.todo_user = self.noiappr1.id
        return super(AccountMove,self).button_noiapprove()


    def action_noi_draft(self):
        return self.write({'noi_state_new': 'draft'})

    def button_noireject(self):
        self.noiappr1_dt = ''
        self.noiappr2_dt = ''
        self.noiappr3_dt = ''
        self.noiappr4_dt = ''
        self.noiappr5_dt = ''
        self.noiappr1 = False
        self.noiappr2 = False
        self.noiappr3 = False
        self.noiappr4 = False
        self.noiappr5 = False
        self.noiappr6 = False
        self.noiappr7 = False
        self.noiappr8 = False
        return self.write({'noi_state_new': 'rejected'})

    @api.model
    def action_post(self):
        res = super(AccountMove,self).action_post()
        if self._context.get('default_is_noi_ho'):
            self.noi_state_new = 'posted'
            self.state='posted'
            self.show_reset_to_draft_button = False
        return res

class tbl_matrix_auth(models.Model):
    _inherit = "tbl_matrix_auth"

    modul = fields.Selection(selection_add=[('NOI HO', 'NOI HO')])

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    domain_product = fields.Many2many('product.product', 'account_move_line_rel', string='Domain Product',
                                  compute='category_expense', store=False)

    @api.depends('move_id')
    def category_expense(self):
        for alldata in self:
            allprod =self.env['product.product'].sudo().search([('company_id', '=', self.env.company.id)])
            myctx = self._context.get('default_is_noi_ho')
            if myctx != None:
                if myctx != False:
                    myprod = allprod.filtered(lambda p:p.categ_id.name=='EXPENSES EMPLOYEE')
                    alldata.domain_product =[(6,0,myprod.ids)]
            else:
                alldata.domain_product = [(6, 0, allprod.ids)]

