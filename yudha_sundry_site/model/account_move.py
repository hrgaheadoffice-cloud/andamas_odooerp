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
    def _amount_sundry(self):
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
    def _default_sundry_warehouse(self):
        warehouse = self.env["stock.warehouse"]
        company_id = self.env.context.get("company_id") or self.env.company.id
        warehouse_id = warehouse.search(
            [("company_id", "=", company_id)]
        )
        return warehouse_id[:1]

    is_sundry_site = fields.Boolean()
    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money'),
    ], string='Payment Type', default='inbound', required=True)
    amount = fields.Float(compute=_amount_sundry)
    show_amount = fields.Float('Amount')

    sundrychecked_by  = fields.Many2one('res.users',string='Checked By',tracking=3,ondelete="cascade",)
    sundryrequest_by = fields.Many2one('res.partner',string='Request By',tracking=3,ondelete="cascade",domain="[('type', '=', 'contact')]")
    sundryprepaid_by = fields.Many2one('res.users',string='Prepared By',tracking=3,ondelete="cascade",default=lambda self: self.env.user)
    sundryprepare_bydate = fields.Datetime(default=fields.Date.today())
    sundryverify_by = fields.Many2one('res.users',string='Verify By',tracking=3,ondelete="cascade",)
    sundryverify_by = fields.Many2one('res.users',string='Verify By',tracking=3,ondelete="cascade",)
    sundrychecked_by = fields.Many2one('res.users', 'Checked by')
    sundry_user_id = fields.Many2one(
        'res.users', string='Purchase Representative', index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)
    sundryappr1 = fields.Many2one('res.users', 'approved by', compute='_default_sundryapproval', store=False)
    sundry_state_new = fields.Selection([
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
        ("posted", "Posted"),
        ('cancel', 'Cancelled'),
        ("rejected", 'Rejected')], default='draft', string='sundry_state_new', readonly=True)

    sundry_state_new_a = fields.Selection(related='sundry_state_new')
    sundry_state_new_b = fields.Selection(related='sundry_state_new')
    sundry_state_new_c = fields.Selection(related='sundry_state_new')
    sundry_state_new_d = fields.Selection(related='sundry_state_new')
    sundry_state_new_e = fields.Selection(related='sundry_state_new')
    sundry_state_new_f = fields.Selection(related='sundry_state_new')
    sundry_state_new_g = fields.Selection(related='sundry_state_new')
    sundry_state_new_h = fields.Selection(related='sundry_state_new')
    READONLY_sundry_state_newS = {

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
    sundryappr1_dt = fields.Datetime('sundryappr1 dt', readonly=True)
    sundryappr1_view = fields.Boolean('sundryappr1 view', readonly=True)
    sundryappr2 = fields.Many2one('res.users', 'approved by', compute='_default_sundryapproval', store=False)
    sundryappr2_dt = fields.Datetime('sundryappr1 dt', readonly=True)
    sundryappr2_view = fields.Boolean('sundryappr1 view', readonly=True)
    sundryappr3 = fields.Many2one('res.users', 'approved by', compute='_default_sundryapproval', store=False)
    sundryappr3_dt = fields.Datetime('sundryappr1 dt', readonly=True)
    sundryappr3_view = fields.Boolean('sundryappr1 view', readonly=True)
    sundryappr4 = fields.Many2one('res.users', 'approved by', compute='_default_sundryapproval', store=False)
    sundryappr4_dt = fields.Datetime('sundryappr1 dt', readonly=True)
    sundryappr4_view = fields.Boolean('sundryappr1 view', readonly=True)
    sundryappr5 = fields.Many2one('res.users', 'approved by', compute='_default_sundryapproval', store=False)
    sundryappr5_dt = fields.Datetime('sundryappr1 dt', readonly=True)
    sundryappr5_view = fields.Boolean('sundryappr1 view', readonly=True)
    sundryappr6 = fields.Many2one('res.users', 'approved by', compute='_default_sundryapproval', store=False)
    sundryappr6_dt = fields.Datetime('sundryappr1 dt', readonly=True)
    sundryappr6_view = fields.Boolean('sundryappr1 view', readonly=True)
    sundryappr7 = fields.Many2one('res.users', 'approved by', compute='_default_sundryapproval', store=False)
    sundryappr7_dt = fields.Datetime('sundryappr1 dt', readonly=True)
    sundryappr7_view = fields.Boolean('sundryappr1 view', readonly=True)
    sundryappr8 = fields.Many2one('res.users', 'approved by', compute='_default_sundryapproval', store=False)
    sundryappr8_dt = fields.Datetime('sundryappr1 dt', readonly=True)
    sundryappr8_view = fields.Boolean('sundryappr1 view', readonly=True)
    sundry_approval_stage = fields.Integer()
    modul = fields.Char(
        string="sundry Modul",
        readonly=True,
        default="Sundry Site",
    )
    sundry_alasan_reject = fields.Text(
        string="Reason for Cancellation",
        track_visibility="onchange"
    )
    next_sundryapprover = fields.Many2one('res.users', 'Next sundryapproval User', compute="_compute_next_sundryapprover", readonly=True,
                                    track_visibility="onchange", store=True)
    next_sundryapprover_ids = fields.Many2many('res.users', compute='_compute_next_sundryapprover_ids')
    submit_sundrydt = fields.Datetime('submit dt', readonly=True)
    sundry_warehouse_id = fields.Many2one('stock.warehouse',string='Location',default=_default_sundry_warehouse)
    
    @api.model
    def create(self, vals):
        myctx = self._context.get('default_is_sundry_site')
        if myctx !=None:
            if myctx != False :
                vals['is_sundry_site'] = True
                if 'reversed_entry_id' not in vals:
                    line_vals = {}
                    journal_id = vals.get('journal_id')
                    account_id = self.env['account.journal'].browse(journal_id).default_account_id.id
                    line_vals['account_id'] = account_id
                    if vals.get('payment_type') == 'outbound':
                        line_vals['credit'] = vals.get('amount')
                    else:
                        line_vals['debit'] = vals.get('amount')
                    if vals.get('line_ids') !=None:
                        vals.get('line_ids').append([0, 0, line_vals])
                    vals['show_amount'] = vals.get('amount')

        res = super(AccountMove, self).create(vals)
        return res

    @api.depends('sundry_state_new')
    def _default_sundryapproval(self):
        for allrec in self:
            allrec.sundry_approval_stage = 0
            allsundryapproval = self.env['tbl_matrix_auth'].search(
                [('modul', '=', 'Sundry Site'),('company_id','=',allrec.company_id.id),('tag_warehouse', 'in', allrec.sundry_warehouse_id.id), ('value_awal', '<=', allrec.show_amount)])
            if not allsundryapproval:
                raise UserError("Please Setting Matrix Approval For Sundry Site first ")
            else:
                allrec.sundry_approval_stage = len(allsundryapproval)
                allrec.sundryappr1 = allsundryapproval.filtered(lambda e: e.level == '1').approval_user.id if allsundryapproval.filtered(lambda e: e.level == '1') else False
                allrec.sundryappr2 = allsundryapproval.filtered(lambda e: e.level == '2').approval_user.id if allsundryapproval.filtered(lambda e: e.level == '2') else False
                allrec.sundryappr3 = allsundryapproval.filtered(lambda e: e.level == '3').approval_user.id if allsundryapproval.filtered(lambda e: e.level == '3') else False
                allrec.sundryappr4 = allsundryapproval.filtered(lambda e: e.level == '4').approval_user.id if allsundryapproval.filtered(lambda e: e.level == '4') else False
                allrec.sundryappr5 = allsundryapproval.filtered(lambda e: e.level == '5').approval_user.id if allsundryapproval.filtered(lambda e: e.level == '5') else False
                allrec.sundryappr6 = allsundryapproval.filtered(lambda e: e.level == '6').approval_user.id if allsundryapproval.filtered(lambda e: e.level == '6') else False
                allrec.sundryappr7 = allsundryapproval.filtered(lambda e: e.level == '7').approval_user.id if allsundryapproval.filtered(lambda e: e.level == '7') else False
                allrec.sundryappr8 = allsundryapproval.filtered(lambda e: e.level == '8').approval_user.id if allsundryapproval.filtered(lambda e: e.level == '8') else False

    @api.depends('sundry_state_new')
    def _compute_next_sundryapprover_ids(self):
        for rec in self:
            if rec.sundry_state_new == 'approved1':
                next_sundryapprover = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Sundry Site'), ('level', '=', '1')]).approval_user
                rec.next_sundryapprover_ids = next_sundryapprover
            elif rec.sundry_state_new == 'approved2':
                next_sundryapprover = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Sundry Site'), ('level', '=', '2')]).approval_user
                rec.next_sundryapprover_ids = next_sundryapprover
            elif rec.sundry_state_new == 'approved3':
                next_sundryapprover = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Sundry Site'), ('level', '=', '3')]).approval_user
                rec.next_sundryapprover_ids = next_sundryapprover
            elif rec.sundry_state_new == 'approved4':
                next_sundryapprover = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Sundry Site'), ('level', '=', '4')]).approval_user
                rec.next_sundryapprover_ids = next_sundryapprover
            elif rec.sundry_state_new == 'approved5':
                next_sundryapprover = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Sundry Site'), ('level', '=', '5')]).approval_user
                rec.next_sundryapprover_ids = next_sundryapprover
            elif rec.sundry_state_new == 'approved6':
                next_sundryapprover = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Sundry Site'), ('level', '=', '6')]).approval_user
                rec.next_sundryapprover_ids = next_sundryapprover
            elif rec.sundry_state_new == 'approved7':
                next_sundryapprover = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Sundry Site'), ('level', '=', '7')]).approval_user
                rec.next_sundryapprover_ids = next_sundryapprover
            elif rec.sundry_state_new == 'approved8':
                next_sundryapprover = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Sundry Site'), ('level', '=', '8')]).approval_user
                rec.next_sundryapprover_ids = next_sundryapprover
            else:
                rec.next_sundryapprover_ids = False


    @api.depends('sundry_state_new',)
    def _compute_sundry_approval_stage(self):
        for rec in self:
            rec.sundry_approval_stage = 0
            emp_id = rec.env['tbl_matrix_auth'].search([('modul', '=', 'Sundry Site')])
            print('total aoproval ', len(emp_id))
            rec.sundry_approval_stage = len(emp_id)
        return



    @api.depends("sundry_state_new", "sundry_user_id", "sundrychecked_by", "sundryverify_by", "sundryappr1", "sundryappr2", "sundryappr3", "sundryappr4", "sundryappr5","sundryappr6", "sundryappr7", "sundryappr8")
    def _compute_next_sundryapprover(self):
        for rec in self:
            if rec.sundry_state_new == 'draft' and rec.sundry_user_id:
                rec.next_sundryapprover = rec.sundry_user_id.id
            elif rec.sundry_state_new == 'to_check' and rec.checked_by:
                rec.next_sundryapprover = rec.checked_by.id
            elif rec.sundry_state_new == 'to_verify' and rec.verify_by:
                rec.next_sundryapprover = rec.verify_by.id
            elif rec.sundry_state_new == 'approved1' and rec.sundryappr1:
                rec.next_sundryapprover = rec.sundryappr1.id
            elif rec.sundry_state_new == 'approved2' and rec.sundryappr2:
                rec.next_sundryapprover = rec.sundryappr2.id
            elif rec.sundry_state_new == 'approved3' and rec.sundryappr3:
                rec.next_sundryapprover = rec.sundryappr3.id
            elif rec.sundry_state_new in ('approved4',) and rec.sundryappr4:
                rec.next_sundryapprover = rec.sundryappr4.id
            elif rec.sundry_state_new in ('approved5',) and rec.sundryappr5:
                rec.next_sundryapprover = rec.sundryappr5.id
            elif rec.sundry_state_new == 'approved6' and rec.sundryappr6:
                rec.next_sundryapprover = rec.sundryappr6.id
            elif rec.sundry_state_new in ('approved7',) and rec.sundryappr7:
                rec.next_sundryapprover = rec.sundryappr7.id
            elif rec.sundry_state_new in ('approved8',) and rec.sundryappr8:
                rec.next_sundryapprover = rec.sundryappr8.id
            else:
                rec.next_sundryapprover = False


    def button_check(self):
        if self.checked_by.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))

        # if self.checked_by:
        #         self.sundry_state_new = 'to_check'
        self.checked_dt = fields.Datetime.now()
        if self.verify_by:
            self.sundry_state_new = 'to_verify'
        elif self.sundryappr1:
            self.sundry_state_new = 'approved1'
        elif self.sundryappr2:
            self.sundry_state_new = 'approved2'
        elif self.sundryappr3:
            self.sundry_state_new = 'approved3'
        elif self.sundryappr4:
            self.sundry_state_new = 'approved4'
        elif self.sundryappr5:
            self.sundry_state_new = 'approved5'
        elif self.sundryappr6:
            self.sundry_state_new = 'approved6'
        elif self.sundryappr7:
            self.sundry_state_new = 'approved7'
        elif self.sundryappr8:
            self.sundry_state_new = 'approved8'
        else:
            self.sundry_state_new = 'approved'
            # self.button_done_pr()
            super(Reimbursementho, self).button_sundryapprove()

    def button_verify(self):
        if self.verify_by.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.verified_dt = fields.Datetime.now()

        if self.sundryappr1:
            self.sundry_state_new = 'approved1'
        elif self.sundryappr2:
            self.sundry_state_new = 'approved2'
        elif self.sundryappr3:
            self.sundry_state_new = 'approved3'
        elif self.sundryappr4:
            self.sundry_state_new = 'approved4'
        elif self.sundryappr5:
            self.sundry_state_new = 'approved5'
        elif self.sundryappr6:
            self.sundry_state_new = 'approved6'
        elif self.sundryappr7:
            self.sundry_state_new = 'approved7'
        elif self.sundryappr8:
            self.sundry_state_new = 'approved8'
        else:
            self.sundry_state_new = 'approved'
            # self.button_done_pr()
            super(CashAdvance, self).button_sundryapprove()

    def button_sundry_to_approve(self):
        for order in self:
            if order.sundry_state_new not in ['draft', 'sent', 'approved']:
                continue
            order.write({'sundry_state_new': 'approved1'})
        return True

    def button_sundryappr1(self):
        if self.env.user not in self.next_sundryapprover_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.sundryappr1 = self.env.user
        self.sundryappr1_dt = fields.Datetime.now()
        if self.sundry_approval_stage > 1:
            self.sundry_state_new = 'approved2'
        else:
            self.sundry_state_new = 'approved'

    def button_sundryappr2(self):
        if self.env.user not in self.next_sundryapprover_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.sundryappr2 = self.env.user
        self.sundryappr2_dt = fields.Datetime.now()
        if self.sundry_approval_stage > 2:
            self.sundry_state_new = 'approved3'
        else:
            self.sundry_state_new = 'approved'

    def button_sundryappr3(self):
        if self.env.user not in self.next_sundryapprover_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.sundryappr3 = self.env.user
        self.sundryappr3_dt = fields.Datetime.now()
        if self.sundry_approval_stage > 3:
            self.sundry_state_new = 'approved4'
        else:
            self.sundry_state_new = 'approved'

    def button_sundryappr4(self):
        if self.env.user not in self.next_sundryapprover_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.sundryappr4 = self.env.user
        self.sundryappr4_dt = fields.Datetime.now()
        if self.sundry_approval_stage > 4:
            self.sundry_state_new = 'approved5'
        else:
            self.sundry_state_new = 'approved'

    def button_sundryappr5(self):
        if self.env.user not in self.next_sundryapprover_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.sundryappr5 = self.env.user
        self.sundryappr5_dt = fields.Datetime.now()
        if self.sundry_approval_stage > 5:
            self.sundry_state_new = 'approved6'
        else:
            self.sundry_state_new = 'approved'


    def button_sundryappr6(self):
        if self.env.user not in self.next_sundryapprover_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.sundryappr6 = self.env.user
        self.sundryappr6_dt = fields.Datetime.now()
        if self.sundry_approval_stage > 6:
            self.sundry_state_new = 'approved7'
        else:
            self.sundry_state_new = 'approved'

    def button_sundryappr7(self):
        if self.env.user not in self.next_sundryapprover_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.sundryappr7 = self.env.user
        self.sundryappr7_dt = fields.Datetime.now()
        if self.sundry_approval_stage > 7:
            self.sundry_state_new = 'approved8'
        else:
            self.sundry_state_new = 'approved'
    def button_sundryappr8(self):
        if self.env.user not in self.next_sundryapprover_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.sundryappr8 = self.env.user
        self.sundryappr8_dt = fields.Datetime.now()
        self.sundry_state_new = 'approved'
    def button_to_sundryapprove(self):
        emp_id = self.env['tbl_matrix_auth'].search(
            [('modul', '=', self.modul), ('level', '=', '1')],
            limit=1)
        if emp_id and not self.sundryappr1:
            self.sundryappr1 = self.env.user.id # emp_id.approval_user.id
        if emp_id:
            if self.sundryappr1 not in emp_id.approval_user:
                raise UserError(
                    _("Invalid sundryapproval User"))
        self.sundry_state_new = 'approved1'


    def button_sundryapprove(self):
        if not self.ca_ids:
            raise UserError(
                 _("The product line must be filled in."))

        if self.sundry_user_id.id != self.env.uid:
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

        # two_steps_purchase_sundryapproval.write({"sundry_state_new": status})
        # one_step_purchase_sundryapproval = self - two_steps_purchase_sundryapproval
        self.submit_dt = fields.Datetime.now()
        emp_id = self.env['tbl_matrix_auth'].search([('modul', '=', self.modul),('level', '=', '1')], limit=1)
        if emp_id:
            if not self.sundryappr1:
                self.sundryappr1 = emp_id.approval_user.id
                self.todo_user = emp_id.approval_user.id
            else:
                self.todo_user = self.sundryappr1.id
        else:
            # raise UserError(
            #         _('Tidak ditemukan pada Matrix Auth')
            #     )
            if not self.sundryappr1:
                raise UserError(
                        _('approved by 1 Harus di isi')
                    )
            self.todo_user = self.sundryappr1.id
        return super(AccountMove,self).button_sundryapprove()


    def action_sundry_draft(self):
        return self.write({'sundry_state_new': 'draft'})

    def button_sundryreject(self):
        self.sundryappr1_dt = ''
        self.sundryappr2_dt = ''
        self.sundryappr3_dt = ''
        self.sundryappr4_dt = ''
        self.sundryappr5_dt = ''
        self.sundryappr1 = False
        self.sundryappr2 = False
        self.sundryappr3 = False
        self.sundryappr4 = False
        self.sundryappr5 = False
        self.sundryappr6 = False
        self.sundryappr7 = False
        self.sundryappr8 = False
        return self.write({'sundry_state_new': 'rejected'})

    def action_post(self):
        res = super(AccountMove,self).action_post()
        if self._context.get('is_sundry_site'):
            self.noi_state_new = 'posted'
            self.state='posted'
            self.show_reset_to_draft_button = False
        return res

class tbl_matrix_auth(models.Model):
    _inherit = "tbl_matrix_auth"

    modul = fields.Selection(selection_add=[('Sundry Site', 'Sundry Site')])