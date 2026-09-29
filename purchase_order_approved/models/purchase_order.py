# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _default_warehouse(self):
        warehouse = self.env["stock.warehouse"]
        company_id = self.env.context.get("company_id") or self.env.company.id
        warehouse_id = warehouse.search(
            [("company_id", "=", company_id)]
        )
        return warehouse_id[:1]

    @api.model
    def _department_get(self):
        department = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]).department_id
        if department:
            return department
        else:
            return False

    state = fields.Selection(selection_add=[
        # ("po_draft", "PO Draft"),
        # ("to_check", "Tobe Check"),
        # ("to_verify", "Tobe Verify"),
        ("approved1", "Tobe Approved"),
        ("approved2", "Tobe Approved 2"),
        ("approved3", "Tobe Approved 3"),
        ("approved4", "Tobe Approved 4"),
        ("approved5", "Tobe Approved 5"),
        ("approved6", "Tobe Approved 6"),
        ("approved7", "Tobe Approved 7"),
        ("approved8", "Tobe Approved 8"),
        ("to_approve_matrix", "Tobe Approved Matrix"),
        ("approved", "Approved"),
        ("purchase", "Purchase Order"),
        ("done", "Done"),
        ("rejected", "Rejected"),
        ("cancel",)])

    state_a = fields.Selection(related='state')
    state_b = fields.Selection(related='state')
    state_c = fields.Selection(related='state')
    state_d = fields.Selection(related='state')
    state_e = fields.Selection(related='state')
    state_f = fields.Selection(related='state')
    state_g = fields.Selection(related='state')
    state_h = fields.Selection(related='state')

    READONLY_STATES = {
        "purchase": [("readonly", True)],
        "done": [("readonly", True)],
        "cancel": [("readonly", True)],
        "approved": [("readonly", True)],
        "approved1": [("readonly", True)],
        "approved2": [("readonly", True)],
        "approved3": [("readonly", True)],
        "approved4": [("readonly", True)],
        "approved5": [("readonly", True)],
        "approved6": [("readonly", True)],
        "approved7": [("readonly", True)],
        "approved8": [("readonly", True)],
        "to_check": [("readonly", True)],
        "to_verify": [("readonly", True)],
    }

    # Update the readonly states:
    # origin = fields.Char(states=READONLY_STATES)
    # date_order = fields.Datetime(states=READONLY_STATES)
    # partner_id = fields.Many2one(states=READONLY_STATES)
    # dest_address_id = fields.Many2one(states=READONLY_STATES)
    # currency_id = fields.Many2one(states=READONLY_STATES)
    # order_line = fields.One2many(states=READONLY_STATES)
    # company_id = fields.Many2one(states=READONLY_STATES)
    # picking_type_id = fields.Many2one(states=READONLY_STATES)

    submit_dt = fields.Datetime('submit dt', readonly=True)
    checked_by = fields.Many2one('res.users', 'Checked by')
    verified_by = fields.Many2one('res.users', 'Verified by')
    appr1 = fields.Many2one('res.users', 'Approved by')
    todo_user = fields.Many2one('res.users', 'Todo User', readonly=True)
    checked_dt = fields.Datetime('checked dt', readonly=True)
    checked_view = fields.Boolean('checked view', readonly=True)
    verified_dt = fields.Datetime('verified dt', readonly=True)
    verified_view = fields.Boolean('verified view', readonly=True)
    appr1_dt = fields.Datetime('appr1 dt', readonly=True)
    appr1_view = fields.Boolean('appr1 view', readonly=True)
    appr2 = fields.Many2one('res.users', 'Approved by')
    appr2_dt = fields.Datetime('appr1 dt', readonly=True)
    appr2_view = fields.Boolean('appr1 view', readonly=True)
    appr3 = fields.Many2one('res.users', 'Approved by')
    appr3_dt = fields.Datetime('appr1 dt', readonly=True)
    appr3_view = fields.Boolean('appr1 view', readonly=True)
    appr4 = fields.Many2one('res.users', 'Approved by')
    appr4_dt = fields.Datetime('appr1 dt', readonly=True)
    appr4_view = fields.Boolean('appr1 view', readonly=True)
    appr5 = fields.Many2one('res.users', 'Approved by')
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
    approval_stage = fields.Integer()
    modul = fields.Char(
        string="Modul",
        readonly=True,
        default="PO",
    )
    # alasan_reject = fields.Text(
    #     string="Reason for Cancellation",
    #     track_visibility="onchange"
    # )
    # langsung_po = fields.Boolean(
    #     string="Langsung PO",
    #     default=False
    # )
    # status_rfq = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('done', 'Done'),
    #     ('cancel', 'Cancel'),
    # ], string='Status RFQ', copy=False, index=True, default='draft')
    #
    # no_rfq = fields.Char(string='RFQ', store=True, readonly=True, compute='_compute_no_rfq', copy=False)
    # no_seq = fields.Char(string='Seq', store=True, readonly=True, compute='_compute_no_seq', copy=False)
    # name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New',
    #                    store=True, readonly=True, compute='_compute_name_new')

    next_approver = fields.Many2one('res.users', 'Next Approval User', compute="_compute_next_approver", readonly=True,
                                    track_visibility="onchange", store=True)
    next_approver_ids = fields.Many2many('res.users', compute='_compute_next_approver_ids')
    todo_user_ids = fields.Many2many(comodel_name="res.users",string="Next Approval",readonly=True,copy=False)
    warehouse_id = fields.Many2one('stock.warehouse',string='Location',default=_default_warehouse)
    approval_matrix_ids = fields.One2many(
        comodel_name="approval.matrix",
        inverse_name="purchase_order_id",
        string="Approval Matrix",
        readonly=True,
        copy=False,
        track_visibility="onchange",
    )
    prepared_by = fields.Many2one('res_users', default=lambda self: self.env.uid)
    department_id = fields.Many2one('hr.department', default=_department_get)
    reason_reject = fields.Text(
        string="Reason for Rejection",
        track_visibility="onchange"
    )

    def button_rejected(self):
        self.todo_user_ids = False
        self.state = 'rejected'

    def create_approval_matrix(self):
        obj_app = self.env['config.approval.matrix'].search([('modul','=',self.modul),('proc_group_id','=',self.proc_group_id.id),('company_id','=',self.company_id.id),('tag_warehouse', 'in', self.picking_type_id.warehouse_id.id),('expected_amount', '<=', self.amount_total)],order="matrix_level_name asc")  
        for item in obj_app:
            vals = {
                "purchase_order_id":self.id,
                "user_ids": [(6, 0, item.approval_user_ids.ids)],
                "matrix_level_id":item.matrix_level_id.id,
                "config_approval_matrix_id":item.id,
                "state":"Tobe Approved Mtrx "+ item.matrix_level_name,
                "name":"Tobe Approved Mtrx "+ item.matrix_level_name,
            }
            obj_create = self.env['approval.matrix'].create(vals)


    def action_preview_reject(self):
        if self.env.uid not in (self.todo_user_ids.ids) and self.state in ('to_approve_matrix','approved'):
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
            
        view = self.env.ref('purchase_order_approved.purchase_order_wizard')
        # picking_type_id = self.picking_type_id or self.picking_id.picking_type_id
        return {
            'name': _('Reason for Rejection'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
        }


    @api.depends('state')
    def _default_approval(self):
        for allrec in self:
            allrec.approval_stage = 0
            allapproval = self.env['tbl_matrix_auth'].search(
                [('modul', '=', 'PO'),  ('company_id', '=', allrec.company_id.id), ('tag_warehouse', 'in', allrec.picking_type_id.warehouse_id.id), ('value_awal', '<=', allrec.amount_total)])
            if not allapproval and allrec.state == 'approved1':
                raise UserError("Please Setting Matrix Approval For PO first ")
            else:
                allrec.approval_stage = len(allapproval)
                allrec.appr1 = allapproval.filtered(lambda e: e.level == '1').approval_user.id if allapproval.filtered(lambda e: e.level == '1') else False
                allrec.appr2 = allapproval.filtered(lambda e: e.level == '2').approval_user.id if allapproval.filtered(lambda e: e.level == '2') else False
                allrec.appr3 = allapproval.filtered(lambda e: e.level == '3').approval_user.id if allapproval.filtered(lambda e: e.level == '3') else False
                allrec.appr4 = allapproval.filtered(lambda e: e.level == '4').approval_user.id if allapproval.filtered(lambda e: e.level == '4') else False
                allrec.appr5 = allapproval.filtered(lambda e: e.level == '5').approval_user.id if allapproval.filtered(lambda e: e.level == '5') else False
                allrec.appr6 = allapproval.filtered(lambda e: e.level == '6').approval_user.id if allapproval.filtered(lambda e: e.level == '6') else False
                allrec.appr7 = allapproval.filtered(lambda e: e.level == '7').approval_user.id if allapproval.filtered(lambda e: e.level == '7') else False
                allrec.appr8 = allapproval.filtered(lambda e: e.level == '8').approval_user.id if allapproval.filtered(lambda e: e.level == '8') else False

    @api.depends('state')
    def _compute_next_approver_ids(self):
        for rec in self:
            if rec.state == 'approved1':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'PO'),('proc_group_id', '=', rec.proc_group_id.id
                                           ), ('level', '=', '1')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved2':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'PO'),('proc_group_id', '=', rec.proc_group_id.id
                                           ), ('level', '=', '2')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved3':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'PO'), ('proc_group_id', '=', rec.proc_group_id.id
                                           ), ('level', '=', '3')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved4':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'PO'), ('proc_group_id', '=', rec.proc_group_id.id
                                           ), ('level', '=', '4')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved5':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'PO'), ('proc_group_id', '=', rec.proc_group_id.id
                                           ), ('level', '=', '5')]).approval_user
                rec.next_approver_ids = next_approver
            else:
                rec.next_approver_ids = False

    def _compute_approval_stage(self):
        for rec in self:
            approval_stage = 0
            emp_id = rec.env['tbl_matrix_auth'].search([('modul', '=', 'PO'),('proc_group_id', '=', rec.proc_group_id.id)])
            for me in emp_id:
                if rec.amount_total > me.value_awal:
                    approval_stage += 1
            rec.approval_stage = approval_stage
        return

    @api.depends("state", "user_id", "checked_by", "verified_by", "appr1", "appr2", "appr3", "appr4", "appr5")
    def _compute_next_approver(self):
        for rec in self:
            if rec.state == 'po_draft' and rec.user_id:
                rec.next_approver = rec.user_id.id
            elif rec.state == 'to_check' and rec.checked_by:
                rec.next_approver = rec.checked_by.id
            elif rec.state == 'to_verify' and rec.verified_by:
                rec.next_approver = rec.verified_by.id
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
            elif rec.state == 'to_approve6' and rec.appr6:
                rec.next_approver = rec.appr6.id
            elif rec.state == 'to_approve7' and rec.appr7:
                rec.next_approver = rec.appr7.id
            elif rec.state in ('to_approve8',) and rec.appr8:
                rec.next_approver = rec.appr8.id
            else:
                rec.next_approver = False

    def button_release(self):
        super(PurchaseOrder, self).button_approve()

    def button_approve1(self):
        super(PurchaseOrder, self).button_approve()

    def button_check(self):
        if self.checked_by.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))

        self.checked_dt = fields.Datetime.now()
        if self.verified_by:
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
            super(PurchaseOrder, self).button_approve()

    def button_verify(self):
        if self.verified_by.id != self.env.uid:
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
            super(PurchaseOrder, self).button_approve()

    def button_appr1(self):
        if self.env.user != self.appr1:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr1 = self.env.user
        self.appr1_dt = fields.Datetime.now()
        if self.approval_stage > 1:
            self.state = 'approved2'
        else:
            self.state = 'approved'

    def button_appr2(self):
        if self.env.user != self.appr2:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr2 = self.env.user
        self.appr2_dt = fields.Datetime.now()
        if self.approval_stage > 2:
            self.state = 'approved3'
        else:
            self.state = 'approved'

    def button_appr3(self):
        if self.env.user != self.appr3:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr3 = self.env.user
        self.appr3_dt = fields.Datetime.now()
        if self.approval_stage > 3:
            self.state = 'approved4'
        else:
            self.state = 'approved'

    def button_appr4(self):
        if self.env.user != self.appr4:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr4 = self.env.user
        self.appr4_dt = fields.Datetime.now()
        if self.approval_stage > 4:
            self.state = 'approved5'
        else:
            self.state = 'approved'

    def button_appr5(self):
        if self.env.user != self.appr5:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr5 = self.env.user
        self.appr5_dt = fields.Datetime.now()
        if self.approval_stage > 5:
            self.state = 'approved6'
        else:
            self.state = 'approved'

    def button_appr6(self):
        if self.env.user != self.appr6:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr6 = self.env.user
        self.appr6_dt = fields.Datetime.now()
        if self.approval_stage > 6:
            self.state = 'approved7'
        else:
            self.state = 'approved'

    def button_appr7(self):
        if self.env.user != self.appr7:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr7 = self.env.user
        self.appr7_dt = fields.Datetime.now()
        if self.approval_stage > 7:
            self.state = 'approved8'
        else:
            self.state = 'approved'

    def button_appr8(self):
        if self.env.user != self.appr8:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr8 = self.env.user
        self.appr8_dt = fields.Datetime.now()
        self.state = 'approved'

    def button_approved_matrix(self):
        emp_id = self.env['approval.matrix'].search([('purchase_order_id','=',self.id),('realization_user_id','=',False)],limit=1,order="state asc")
        if emp_id:
            if self.env.uid in (emp_id.config_approval_matrix_id.approval_user_ids.ids) or emp_id.config_approval_matrix_id.delegate_user.id == self.env.uid:
                emp_id.write({'realization_user_id':self.env.uid,"date": fields.Datetime.now()})
                emp_id = self.env['approval.matrix'].search([('purchase_order_id','=',self.id),('realization_user_id','=',False)],limit=1,order="state asc")
                if not emp_id:
                    self.todo_user_ids = False
                    self.state = 'approved'
                else:
                    self.todo_user_ids = [(6, 0, emp_id.config_approval_matrix_id.approval_user_ids.ids)]
            else:
                raise UserError(
                    _("Anda tidak berhak melakukan proses ini"))

    def button_to_approve(self):
        self.approval_matrix_ids.unlink()
        self.create_approval_matrix()
        if not self.approval_matrix_ids:
            raise UserError(
                _("Approval Matrix not found, Please Check Config Approval Matrix"))
        emp_id = self.env['approval.matrix'].search([('purchase_order_id','=',self.id),('realization_user_id','=',False)],limit=1,order="state asc")
        if emp_id:
            self.todo_user_ids = [(6, 0, emp_id.config_approval_matrix_id.approval_user_ids.ids)]
        self.state = 'to_approve_matrix'

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'approved']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

class InheritApprovalMatrixPO(models.Model):
    _inherit = "approval.matrix"

    purchase_order_id = fields.Many2one('purchase.order','Purchase Order')


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_product_purchase_description(self, product_lang):
        self.ensure_one()
        name = product_lang.name
        if product_lang.description_purchase:
            name += '\n' + product_lang.description_purchase

        return name
