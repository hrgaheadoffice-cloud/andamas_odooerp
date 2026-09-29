from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from collections import defaultdict


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _default_warehouse(self):
        warehouse = self.env["stock.warehouse"]
        company_id = self.env.context.get("company_id") or self.env.company.id
        warehouse_id = warehouse.search(
            [("company_id", "=", company_id)]
        )
        return warehouse_id[:1]

    modul = fields.Char(
        string="Modul",
        readonly=True,
        default="Vendor Bill",
    )
    state_new = fields.Selection([
        ('draft', 'Draft'),
        ('approved1', 'Tobe approved'),
        ('approved2', 'Tobe approved 2'),
        ('approved3', 'Tobe approved 3'),
        ('approved4', 'Tobe approved 4'),
        ('approved5', 'Tobe approved 5'),
        ('approved6', 'Tobe approved 6'),
        ('approved7', 'Tobe approved 7'),
        ('approved8', 'Tobe approved 8'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
        ('rejected', 'Rejected'),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')

    state_new_a = fields.Selection(related='state')
    state_new_b = fields.Selection(related='state')
    state_new_c = fields.Selection(related='state')
    state_new_d = fields.Selection(related='state')
    state_new_e = fields.Selection(related='state')
    state_new_f = fields.Selection(related='state')
    state_new_g = fields.Selection(related='state')
    state_new_h = fields.Selection(related='state')

    appr1 = fields.Many2one('res.users', 'Approved by', store=1)
    appr1_dt = fields.Datetime('appr1 dt', readonly=True)
    appr2 = fields.Many2one('res.users', 'Approved by', store=1)
    appr2_dt = fields.Datetime('appr1 dt', readonly=True)
    appr3 = fields.Many2one('res.users', 'Approved by', store=1)
    appr3_dt = fields.Datetime('appr1 dt', readonly=True)
    appr4 = fields.Many2one('res.users', 'Approved by', store=1)
    appr4_dt = fields.Datetime('appr1 dt', readonly=True)
    appr5 = fields.Many2one('res.users', 'Approved by', store=1)
    appr5_dt = fields.Datetime('appr1 dt', readonly=True)
    appr6 = fields.Many2one('res.users', 'Approved by', store=1)
    appr6_dt = fields.Datetime('appr1 dt', readonly=True)
    appr7 = fields.Many2one('res.users', 'Approved by', store=1)
    appr7_dt = fields.Datetime('appr1 dt', readonly=True)
    appr8 = fields.Many2one('res.users', 'Approved by', store=1)
    appr8_dt = fields.Datetime('appr1 dt', readonly=True)
    approval_stage = fields.Integer(compute='_default_approval', store=False)
    next_approver = fields.Many2one('res.users', 'Next Approval User', compute="_compute_next_approver", readonly=True,
                                    track_visibility="onchange", store=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Location', default=_default_warehouse)

    def button_request_approval(self):
        self.state = 'approved1'

    # @api.depends('state')
    def _default_approval(self):
        for allrec in self:
            allapproval = self.env['tbl_matrix_auth'].search(
                [('modul', '=', 'Vendor Bill'), ('company_id', '=', allrec.company_id.id), ('tag_warehouse', 'in', allrec.warehouse_id.id)])
            allrec.approval_stage = len(allapproval) or 0
            if allrec.state == 'approved1':
                if not allapproval and allrec.state != 'draft':
                    raise UserError("Please Setting Matrix Approval For Vendor Bill first ")
                else:
                    allrec.appr1 = allapproval.filtered(lambda e: e.level == '1').approval_user.id if allapproval.filtered(lambda e: e.level == '1') else False
                    allrec.appr2 = allapproval.filtered(lambda e: e.level == '2').approval_user.id if allapproval.filtered(lambda e: e.level == '2') else False
                    allrec.appr3 = allapproval.filtered(lambda e: e.level == '3').approval_user.id if allapproval.filtered(lambda e: e.level == '3') else False
                    allrec.appr4 = allapproval.filtered(lambda e: e.level == '4').approval_user.id if allapproval.filtered(lambda e: e.level == '4') else False
                    allrec.appr5 = allapproval.filtered(lambda e: e.level == '5').approval_user.id if allapproval.filtered(lambda e: e.level == '5') else False
                    allrec.appr6 = allapproval.filtered(lambda e: e.level == '6').approval_user.id if allapproval.filtered(lambda e: e.level == '6') else False
                    allrec.appr7 = allapproval.filtered(lambda e: e.level == '7').approval_user.id if allapproval.filtered(lambda e: e.level == '7') else False
                    allrec.appr8 = allapproval.filtered(lambda e: e.level == '8').approval_user.id if allapproval.filtered(lambda e: e.level == '8') else False

    @api.depends("state")
    def _compute_next_approver(self):
        for rec in self:
            if rec.state == 'approved1' and rec.appr1:
                rec.next_approver = rec.appr1.id
            elif rec.state == 'approved2' and rec.appr2:
                rec.next_approver = rec.appr2.id
            elif rec.state == 'approved3' and rec.appr3:
                rec.next_approver = rec.appr3.id
            elif rec.state == 'approved4' and rec.appr4:
                rec.next_approver = rec.appr4.id
            elif rec.state == 'approved5' and rec.appr5:
                rec.next_approver = rec.appr5.id
            elif rec.state == 'approved6' and rec.appr6:
                rec.next_approver = rec.appr6.id
            elif rec.state == 'approved7' and rec.appr7:
                rec.next_approver = rec.appr7.id
            elif rec.state == 'approved8' and rec.appr8:
                rec.next_approver = rec.appr8.id
            else:
                rec.next_approver = False
                
    def button_appr1(self):
        if self.env.user != self.next_approver:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr1 = self.env.user
        self.appr1_dt = fields.Datetime.now()
        if self.approval_stage > 1:
            self.state = 'approved2'
        else:
            self.state = 'approved'

    def button_appr2(self):
        if self.env.user != self.next_approver:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr2 = self.env.user
        self.appr2_dt = fields.Datetime.now()
        if self.approval_stage > 2:
            self.state = 'approved3'
        else:
            self.state = 'approved'

    def button_appr3(self):
        if self.env.user != self.next_approver:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr3 = self.env.user
        self.appr3_dt = fields.Datetime.now()
        if self.approval_stage > 3:
            self.state = 'approved4'
        else:
            self.state = 'approved'

    def button_appr4(self):
        if self.env.user != self.next_approver:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr4 = self.env.user
        self.appr4_dt = fields.Datetime.now()
        if self.approval_stage > 4:
            self.state = 'approved5'
        else:
            self.state = 'approved'

    def button_appr5(self):
        if self.env.user != self.next_approver:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr5 = self.env.user
        self.appr5_dt = fields.Datetime.now()
        if self.approval_stage > 5:
            self.state = 'approved6'
        else:
            self.state = 'approved'

    def button_appr6(self):
        if self.env.user != self.next_approver:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr6 = self.env.user
        self.appr6_dt = fields.Datetime.now()
        if self.approval_stage > 6:
            self.state = 'approved7'
        else:
            self.state = 'approved'

    def button_appr7(self):
        if self.env.user != self.next_approver:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr7 = self.env.user
        self.appr7_dt = fields.Datetime.now()
        if self.approval_stage > 7:
            self.state = 'approved8'
        else:
            self.state = 'approved'
            
    def button_appr8(self):
        if self.env.user != self.next_approver:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr8 = self.env.user
        self.appr8_dt = fields.Datetime.now()
        self.state = 'approved'


class tbl_matrix_auth(models.Model):
    _inherit = "tbl_matrix_auth"

    modul = fields.Selection(selection_add=[('Vendor Bill', 'Vendor Bill')])

