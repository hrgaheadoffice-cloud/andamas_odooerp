# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, ValidationError
from odoo.tools import float_compare, float_is_zero, float_round
class CashAdvance(models.Model):
    _name = "cash.advance"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "create_date desc, id desc"
    _description = "Cash Advance"
    _rec_name = 'name'
    _check_company_auto = True

    def _get_default_currency_id(self):
        return self.env.company.currency_id.id

    @api.depends('settelment_ids','state')
    def _get_settelment(self):
        for order in self:
            mysettel = self.env['settelment'].sudo().search([('ca_id','=',order.id)])
            print('mysettel ', mysettel)
            if mysettel:
                order.settelment_ids = mysettel.ids
                order.settelment_count = len(mysettel)
            else:
                order.settelment_ids = False
                order.settelment_count = 0


    @api.depends('ca_ids.amount','state')
    def hitung_total(self):
        for order in self:
            amount_total = 0.0
            for line in order.ca_ids:
                amount_total += line.amount
            order.update({
                'amount_ca': amount_total,
            })


    name = fields.Char('Document Number',index=True,default='New')
    request_date = fields.Date('Request Date')
    amount_ca = fields.Monetary('Amount Advance', store=True, readonly=True,compute='hitung_total',tracking=5)
    currency_id = fields.Many2one('res.currency', 'Currency', default=_get_default_currency_id, required=True)
    company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.company)
    cost_center = fields.Many2one('account.cost.center', string='Cost Center', ondelete="restrict", index=True)
    request_by = fields.Many2one('res.partner',string='Request By',tracking=3,ondelete="cascade",domain="[('type', '=', 'contact')]")
    prepaid_by = fields.Many2one('res.users',string='Prepared By',tracking=3,ondelete="cascade",default=lambda self: self.env.user)
    prepare_bydate = fields.Date(default=fields.Date.today())
    verify_by = fields.Many2one('res.users',string='Verify By',tracking=3,ondelete="cascade",)
    checked_by = fields.Many2one('res.users', 'Checked by')
    user_id = fields.Many2one(
        'res.users', string='Purchase Representative', index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)
    appr1 = fields.Many2one('res.users', 'Approved by',compute='_default_approval',store=False)
    state = fields.Selection([
        ("draft", "Draft"),
        ("approved1", "Tobe Approved"),
        ("approved2", "Tobe Approved 2"),
        ("approved3", "Tobe Approved 3"),
        ("approved4", "Tobe Approved 4"),
        ("approved5", "Tobe Approved 5"),
        ("approved5", "Tobe Approved 6"),
        ("approved7", "Tobe Approved 7"),
        ("approved8", "Tobe Approved 8"),
        ('approved', 'Approved'),
        ("waiting_on_payment", "Waiting On Payment"),
        ("done", "Done"),
        ("rejected",'Rejected')],default='draft',string='State',readonly=True)

    state_a = fields.Selection(related='state')
    state_b = fields.Selection(related='state')
    state_c = fields.Selection(related='state')
    state_d = fields.Selection(related='state')
    state_e = fields.Selection(related='state')
    state_f = fields.Selection(related='state')
    state_g = fields.Selection(related='state')
    state_h = fields.Selection(related='state')


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
        "approved":  [("readonly",True,)],
        "to_check": [("readonly", True)],
        "to_verify": [("readonly", True)],
    }
    appr1_dt = fields.Datetime('appr1 dt', readonly=True)
    appr1_view = fields.Boolean('appr1 view', readonly=True)
    appr2 = fields.Many2one('res.users', 'Approved by',compute='_default_approval',store=False)
    appr2_dt = fields.Datetime('appr1 dt', readonly=True)
    appr2_view = fields.Boolean('appr1 view', readonly=True)
    appr3 = fields.Many2one('res.users', 'Approved by',compute='_default_approval',store=False)
    appr3_dt = fields.Datetime('appr1 dt', readonly=True)
    appr3_view = fields.Boolean('appr1 view', readonly=True)
    appr4 = fields.Many2one('res.users', 'Approved by',compute='_default_approval',store=False)
    appr4_dt = fields.Datetime('appr1 dt', readonly=True)
    appr4_view = fields.Boolean('appr1 view', readonly=True)
    appr5 = fields.Many2one('res.users', 'Approved by',compute='_default_approval',store=False)
    appr5_dt = fields.Datetime('appr1 dt', readonly=True)
    appr5_view = fields.Boolean('appr1 view', readonly=True)
    appr6 = fields.Many2one('res.users', 'Approved by',compute='_default_approval',store=False)
    appr6_dt = fields.Datetime('appr1 dt', readonly=True)
    appr6_view = fields.Boolean('appr1 view', readonly=True)
    appr7 = fields.Many2one('res.users', 'Approved by',compute='_default_approval',store=False)
    appr7_dt = fields.Datetime('appr1 dt', readonly=True)
    appr7_view = fields.Boolean('appr1 view', readonly=True)
    appr8 = fields.Many2one('res.users', 'Approved by',compute='_default_approval',store=False)
    appr8_dt = fields.Datetime('appr1 dt', readonly=True)
    appr8_view = fields.Boolean('appr1 view', readonly=True)
    approval_stage = fields.Integer(compute='_compute_approval_stage')
    modul = fields.Char(
        string="Modul",
        readonly=True,
        default="Cash Advance Site",
    )
    alasan_reject = fields.Text(
        string="Reason for Cancellation",
        track_visibility="onchange"
    )
    next_approver = fields.Many2one('res.users', 'Next Approval User', compute="_compute_next_approver", readonly=True,
                                    track_visibility="onchange", store=True)
    next_approver_ids = fields.Many2many('res.users', compute='_compute_next_approver_ids')
    submit_dt = fields.Datetime('submit dt', readonly=True)
    ca_ids = fields.One2many('cash.advance.line','ca_id',string='Cash Advance Details',auto_join=True)
    settelment_ids = fields.One2many('settelment', 'ca_id', string='Cash Advance Details', auto_join=True,compute='_get_settelment')
    user_pembuat = fields.Many2one('res.users',default=lambda self:self.env.user.id)
    settelment_count = fields.Integer(string='Settelment Count', compute='_get_settelment', readonly=True)
    acmove_ids = fields.One2many("account.move", 'ca_id',string='Journal', copy=False,auto_join=True)
    jurnal_ids =  fields.One2many("account.move.line", related='acmove_ids.line_ids',string='Journal Items', copy=False,auto_join=True)
    payment_aktif = fields.Boolean('Payment',)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'cash.advance') or _('New')
        res = super(CashAdvance, self).create(vals)
        return res

    def preview_settelment(self):
        settelment = self.mapped('settelment_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("yudha_ca.action_settelment")
        if len(settelment) >= 1:
            action['domain'] = [('id', 'in', settelment.ids)]
        elif len(settelment) == 0:
            form_view = [(self.env.ref('yudha_ca.view_settelment_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = settelment.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action

    @api.depends('state')
    def _default_approval(self):
        for allrec in self:
            allapproval = self.env['tbl_matrix_auth'].search(
                [('modul', '=', 'Cash Advance')])
            if not allapproval:
                allrec.appr1 = False
                allrec.appr2 = False
                allrec.appr3 = False
                allrec.appr4 = False
                allrec.appr5 = False
                allrec.appr6 = False
                allrec.appr7 = False
                allrec.appr8 = False
            for allapp in allapproval:
                if allapp.level == 1:
                    allrec.appr1 = allapp.approval_user.id
                elif allapp.level == 2:
                    allrec.appr2 = allapp.approval_user.id
                elif allapp.level == 3:
                    allrec.appr4 = allapp.approval_user.id
                elif allapp.level == 4:
                    allrec.appr4 = allapp.approval_user.id
                elif allapp.level == 5:
                    allrec.appr5 = allapp.approval_user.id
                elif allapp.level == 6:
                    allrec.appr6 = allapp.approval_user.id
                elif allapp.level == 7:
                    allrec.appr7 = allapp.approval_user.id
                elif allapp.level == 8:
                    allrec.appr8 = allapp.approval_user.id

    @api.depends('state')
    def _compute_next_approver_ids(self):
        for rec in self:
            if rec.state == 'approved1':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Cash Advance'), ('level', '=', '1')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved2':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Cash Advance'), ('level', '=', '2')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved3':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Cash Advance'), ('level', '=', '3')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved4':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Cash Advance'), ('level', '=', '4')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved5':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Cash Advance'), ('level', '=', '5')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved6':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Cash Advance'), ('level', '=', '6')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved7':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Cash Advance'), ('level', '=', '7')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved8':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'Cash Advance'), ('level', '=', '8')]).approval_user
                rec.next_approver_ids = next_approver
            else:
                rec.next_approver_ids = False

    def _compute_approval_stage(self):
        for rec in self:
            approval_stage = 0
            emp_id = rec.env['tbl_matrix_auth'].search([('modul', '=', 'Cash Advance')])
            rec.approval_stage = len(emp_id)
        return


    @api.depends("state", "user_id", "checked_by", "verify_by", "appr1", "appr2", "appr3", "appr4", "appr5","appr6", "appr7", "appr8")
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
            elif rec.state == 'approved6' and rec.appr6:
                rec.next_approver = rec.appr6.id
            elif rec.state in ('approved7',) and rec.appr7:
                rec.next_approver = rec.appr7.id
            elif rec.state in ('approved8',) and rec.appr8:
                rec.next_approver = rec.appr8.id
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
            super(CashAdvance, self).button_approve()

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
            super(CashAdvance, self).button_approve()

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
        return super(CashAdvance,self).button_approve()


    def register_payment(self):
        return {
            'name': _('Register Payment'),
            'res_model': 'register.payment.wiz',
            'view_mode': 'form',
            'context': {
                'active_model': 'cash.advance',
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

class CashAdvanceLine(models.Model):
    _name = "cash.advance.line"
    _description = "Cash Advance Line"

    ca_id = fields.Many2one(
        string="# Employee CA",
        comodel_name="cash.advance",
        required=True,
        ondelete="cascade",
    )
    currency_id = fields.Many2one('res.currency', 'Currency',related='ca_id.currency_id', required=True)
    company_id = fields.Many2one('res.company', 'Company',related='ca_id.company_id')
    # product_id = fields.Many2one('product.product','Product Name',index=True,domain="[('can_be_expensed', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", ondelete='restrict')
    amount = fields.Float(digits='Product Price',string='Estimated Amount')
    description = fields.Text('Description')
    # cost_center = fields.Selection([('ibp_ho','IBP-HEAD OFFICE'),
    #                                 ('ibp_samarinda','IBP-SAMARINDA'),
    #                                 ('ibp_lmj','IBP-LMJ'),
    #                                 ('ibp_site','IBP-SITE'),
    #                                 ('ibp_isp','IBP-ISP')],default='ibp_ho',string='Cost Center',ondelete="restrict",index=True)

class tbl_matrix_auth(models.Model):
    _inherit = "tbl_matrix_auth"

    modul = fields.Selection(selection_add=[('Cash Advance Site', 'Cash Advance Site')])