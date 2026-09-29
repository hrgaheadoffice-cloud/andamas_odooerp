# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_STATES = [
    ("draft", "Draft"),
    ("to_request_approve", "Tobe Approve Request"),
    ("to_recommend", "Tobe Recommend"),
    ("to_check", "Tobe Check"),
    ("to_verify", "Tobe Verify"),
    ("to_approve", "Tobe Approved"),
    ("to_approve1", "Tobe Apprvd Mtrx1"),
    ("to_approve2", "Tobe Apprvd Mtrx2"),
    ("to_approve3", "Tobe Apprvd Mtrx3"),
    ("to_approve4", "Tobe Apprvd Mtrx4"),
    ("to_approve5", "Tobe Apprvd Mtrx5"),
    ("to_approve6", "Tobe Apprvd Mtrx6"),
    ("to_approve7", "Tobe Apprvd Mtrx7"),
    ("to_approve8", "Tobe Apprvd Mtrx8"),
    ("to_approve_matrix", "Tobe Approved Matrix"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("cancel", "Canceled"),
    ("done", "Done"),
]


class tbl_proc_group(models.Model):
    _name = "tbl_proc_group"
    _description = "tbl_proc_group"

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    name = fields.Char(
        string="Name",
        required=True, )
    active = fields.Boolean(
        'Active', default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=_company_get,
        track_visibility="onchange",
    )


class tbl_procurement_by(models.Model):
    _name = "tbl_procurement_by"

    name = fields.Char(
        string="Name",
        required=True)


class Priority(models.Model):
    _name = "priority"

    name = fields.Char(
        string="Name",
        required=True)


class PurchaseRequest(models.Model):
    _name = "purchase.request"
    _description = "Purchase Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    @api.model
    def _get_default_prepared_by(self):
        return self.env["res.users"].browse(self.env.uid)
    # @api.model
    # def _get_default_approval_svp(self):
    #     return self.env["hr.employee"].search([('user_id', '=', self.env.uid)])
    @api.model
    def _get_default_manager(self):
        emp_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        svp_id = self.env['hr.employee'].browse(emp_id.coach_id.id)
        return self.env["res.users"].browse(svp_id.user_id.id)

    @api.model
    def _get_default_checked_by(self):
        emp_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        svp_id = self.env['hr.employee'].browse(emp_id.parent_id.id)
        return self.env["res.users"].browse(svp_id.user_id.id)

    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("purchase.request")

    @api.model
    def _default_picking_type(self):
        type_obj = self.env["stock.picking.type"]
        company_id = self.env.context.get("company_id") or self.env.company.id
        types = type_obj.search(
            [("code", "=", "incoming"), ("warehouse_id.company_id", "=", company_id)]
        )
        if not types:
            types = type_obj.search(
                [("code", "=", "incoming"), ("warehouse_id", "=", False)]
            )
        return types[:1]

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ("draft"):
                rec.is_editable = True
            else:
                rec.is_editable = False

    @api.model
    def _department_get(self):
        department = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]).department_id
        if department:
            return department
        else:
            raise ValidationError(_("Anda belum terdaftar di department. Hubungi Administrator"))

    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    status_recomend_check = fields.Integer(
        string="Status Recommend",
        track_visibility="onchange",
    )
    status_recomend = fields.Integer(
        string="Status Recommend Check",
        track_visibility="onchange",
    )
    status_check = fields.Integer(
        string="Status Check",
        track_visibility="onchange",
    )
    status_vrecomend = fields.Integer(
        string="Status Recommend Check",
        track_visibility="onchange",
    )
    status_vcheck = fields.Integer(
        string="Status Check",
        track_visibility="onchange",
    )
    name = fields.Char(
        string="Request Reference",
        required=True,
        # default=_get_default_name,
        default='New',
        track_visibility="onchange",
        copy=False
    )
    modul = fields.Char(
        string="Modul",
        readonly=True,
        default="PR",
    )
    origin = fields.Char(string="Source Document",track_visibility="onchange",)
    date_start = fields.Date(
        string="Creation date",
        help="Date when the user initiated the request.",
        default=fields.Date.context_today,
        track_visibility="onchange",
    )
    appr1_dt = fields.Datetime('Appr1 Datetime', copy=False)
    is_appr1 = fields.Boolean('Is Appr1')
    status_tr_appr1 = fields.Selection([
        ('draft', 'Draft'),
        ('todo', 'To Approve'),
        ('done', 'Done'),
    ], string='Status Approval Matrix 1', copy=False, index=True, tracking=True, default='draft')
    appr2 = fields.Many2one(
        comodel_name="res.users",
        string="Approved By",
        copy=False,
        track_visibility="onchange",
        compute='_default_approval',
        store=True
    )
    appr2_dt = fields.Datetime('Appr2 Datetime', copy=False)
    is_appr2 = fields.Boolean('Is Appr2')
    status_tr_appr2 = fields.Selection([
        ('draft', 'Draft'),
        ('todo', 'To Approve'),
        ('done', 'Done'),
    ], string='Status Approval Matrix 2', copy=False, index=True, tracking=True, default='draft')
    appr3 = fields.Many2one(
        comodel_name="res.users",
        string='Approved By',
        copy=False,
        track_visibility="onchange",
        compute='_default_approval',
        store=True
    )
    appr3_dt = fields.Datetime('Appr3 Datetime', copy=False)
    is_appr3 = fields.Boolean('Is Appr3')
    status_tr_appr3 = fields.Selection([
        ('draft', 'Draft'),
        ('todo', 'To Approve'),
        ('done', 'Done'),
    ], string='Status Approval Matrix 3', copy=False, index=True, tracking=True, default='draft')
    appr4 = fields.Many2one(
        comodel_name="res.users",
        string="Approved By",
        copy=False,
        track_visibility="onchange",
        compute='_default_approval',
        store=True
    )
    appr4_dt = fields.Datetime('Appr4 Datetime', copy=False)
    is_appr4 = fields.Boolean('Is Appr4')
    status_tr_appr4 = fields.Selection([
        ('draft', 'Draft'),
        ('todo', 'To Approve'),
        ('done', 'Done'),
    ], string='Status Approval Matrix 4', copy=False, index=True, tracking=True, default='draft')
    appr5 = fields.Many2one(
        comodel_name="res.users",
        string="Approved By",
        copy=False,
        track_visibility="onchange",
        compute='_default_approval',
        store=True
    )
    appr5_dt = fields.Datetime('Appr5 Datetime', copy=False)
    is_appr5 = fields.Boolean('Is Appr5')
    status_appr5 = fields.Selection([
        ('draft', 'Draft'),
        ('todo', 'To Approve'),
        ('done', 'Done'),
    ], string='Status Approval Matrix 5', copy=False, index=True, tracking=True, default='draft')
    appr6 = fields.Many2one(
        comodel_name="res.users",
        string="Approved By",
        copy=False,
        track_visibility="onchange",
        compute='_default_approval',
        store=True
    )
    appr6_dt = fields.Datetime('Appr6 Datetime', copy=False)
    is_appr6 = fields.Boolean('Is Appr6')
    appr7 = fields.Many2one(
        comodel_name="res.users",
        string="Approved By",
        copy=False,
        track_visibility="onchange",
        compute='_default_approval',
        store=True
    )
    appr7_dt = fields.Datetime('Appr7 Datetime', copy=False)
    is_appr7 = fields.Boolean('Is Appr7')
    appr8 = fields.Many2one(
        comodel_name="res.users",
        string="Approved By",
        copy=False,
        track_visibility="onchange",
        compute='_default_approval',
        store=True
    )
    appr8_dt = fields.Datetime('Appr8 Datetime', copy=False)
    is_appr8 = fields.Boolean('Is Appr8')

    requested_by = fields.Many2one(
        comodel_name="res.users",
        string="Requested by",
        required=True,
        copy=False,
        track_visibility="onchange",
        default=_get_default_requested_by,
        index=True,
    )
    requested_dt = fields.Datetime('Request Datetime', copy=False)

    prepared_by = fields.Many2one(
        comodel_name="res.users",
        string="Prepared by",
        required=True,
        copy=False,
        track_visibility="onchange",
        default=_get_default_prepared_by,
        index=True,
    )
    checked_by = fields.Many2one(
        comodel_name="res.users",
        string="Checked By",
        # required=True,
        copy=False,
        default =_get_default_checked_by,
        track_visibility="onchange",
        index=True,
    )
    todo_user = fields.Many2one('res.users', 'Todo user', readonly=True,copy=False)
    todo_user_ids = fields.Many2many(comodel_name="res.users",string="Next Approval",readonly=True,copy=False)
    x_no_po                 =fields.Char('No PO',compute="_compute_no_po")
    prepare_dt = fields.Datetime('Prepare Datetime', copy=False)
    checked_dt = fields.Datetime('Checked Datetime', copy=False)
    status_tr_prepare = fields.Selection([
        ('draft', 'Draft'),
        ('todo', 'To Approve'),
        ('done', 'Done'),
    ], string='Status Prepare', copy=False, index=True, tracking=True, default='draft')
    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department",
        track_visibility="onchange",
        default=_department_get,
        store=True
    )
    work_location = fields.Char(
        string="Location",
        track_visibility="onchange",
        related='prepared_by.work_location'
    )
    location = fields.Many2one(
        'account.analytic.account',
        string="Location",
        track_visibility="onchange",
    )
    # cost_center = fields.Many2one('account.cost.center','Cost Center', required=True)
    procurement_by = fields.Many2one('tbl_procurement_by', 'Procure by')
    recommended_by = fields.Many2one(
        comodel_name="res.users",
        string="Recomended By",
        copy=False,
        track_visibility="onchange",
    )
    recommended_dt = fields.Datetime('Recommended Datetime', copy=False)
    status_tr_recommended = fields.Selection([
        ('draft', 'Draft'),
        ('todo', 'To Approve'),
        ('done', 'Done'),
    ], string='Status Recommended', copy=False, index=True, tracking=True, default='draft')
    checked_dt = fields.Datetime('Checked Datetime', copy=False)
    status_tr_check = fields.Selection([
        ('draft', 'Draft'),
        ('todo', 'To Approve'),
        ('done', 'Done'),
    ], string='Status Check', copy=False, index=True, tracking=True, default='draft')
    verified_by = fields.Many2one(
        comodel_name="res.users",
        string="Verified By",
        track_visibility="onchange")
    verify_dt = fields.Datetime('Verify Datetime', copy=False)
    status_tr_verify = fields.Selection([
        ('draft', 'Draft'),
        ('todo', 'To Approve'),
        ('done', 'Done'),
    ], string='Status Verify', copy=False, index=True, tracking=True, default='draft')

    assigned_to = fields.Many2one(
        comodel_name="res.users",
        string="Approved by",
        track_visibility="onchange",
        # required=True,
        default=_get_default_manager
        # copy=False,
        # track_visibility="onchange",
        # default=_get_default_requested_by,
        # domain=lambda self: [
        #     (
        #         "groups_id",
        #         "in",
        #         self.env.ref("purchase_request.group_purchase_request_manager").id,
        #     )
        # ],
        # index=True,
        # compute="_compute_assign",
        # required=True
    )
    assign_to_dt = fields.Datetime('Approve Datetime', copy=False)
    assign_dt = fields.Datetime('Assign Datetime', copy=False)
    status_tr_assign_to = fields.Selection([
        ('draft', 'Draft'),
        ('todo', 'To Approve'),
        ('done', 'Done'),
    ], string='Status Approved', copy=False, index=True, tracking=True, default='draft')
    site_manager_id = fields.Many2one('hr.employee')
    head_finance_id = fields.Many2one('hr.employee')
    head_scm_id = fields.Many2one('hr.employee')
    deputy_gm_id = fields.Many2one('hr.employee')
    general_manager_id = fields.Many2one('hr.employee')
    checked_by_id = fields.Many2one('hr.employee')
    known_by_id = fields.Many2one('hr.employee')
    request_to = fields.Char()

    @api.depends('x_no_po')
    def _compute_no_po(self):
        for item in self:
            arrNoPO =[]
            po = self.env['purchase.order'].sudo().search([('pr_id','=',item.id)])
            for i in po:
                arrNoPO.append(i.name)
            
            # ================PO====================
            kutip_no_po = str(arrNoPO).replace("'", "")
            kurung_kiri_no_po = str(kutip_no_po).replace("[", "")
            all_result_no_po = str(kurung_kiri_no_po).replace("]", "")
            item.x_no_po    =all_result_no_po

    def update_source_document(self):
        Arrcah_count         =[]
        Arrcas_count         =[]
        Arrsundary_site_count=[]
        Arrnoi_count         =[]
        ArrPO                =[]
        arrNoPR              =[]
        for rec in self:
            cah_count               = self.env['cash.advance.ho'].search([('purchase_request_id','=',rec.id)])
            if cah_count:
                for i in cah_count:
                    Arrcah_count.append(i.name)

            cas_count               = self.env['cash.advance.site'].search([('purchase_request_id','=',rec.id)])
            if cas_count:
                for i in cas_count:
                    Arrcas_count.append(i.name)

            sundary_site_count      = self.env['sundry'].search([('purchase_request_id','=',rec.id)])
            if sundary_site_count:
                for i in sundary_site_count:
                    Arrsundary_site_count.append(i.name)

            noi_count               = self.env['noi'].search([('purchase_request_id','=',rec.id)])
            if noi_count:
                for i in noi_count:
                    Arrnoi_count.append(i.name)

            po_count               = self.env['purchase.order'].search([('pr_id','=',rec.id)])
            if po_count:
                for i in po_count:
                    ArrPO.append(i.origin)

            arrNoPR = Arrcah_count + Arrcas_count + Arrsundary_site_count + Arrnoi_count + ArrPO
            kutip_no_po = str(arrNoPR).replace("'", "")
            kurung_kiri_no_po = str(kutip_no_po).replace("[", "")
            all_result_no_po = str(kurung_kiri_no_po).replace("]", "")
            rec.origin    =all_result_no_po


    @api.onchange('picking_type_id')
    def _onchange_job_position(self):
        tag_id = self.env['hr.employee.category'].search([('name', '=', self.picking_type_id.warehouse_id.name)])
        site_manager_id = self.env['hr.employee'].search([('job_title', '=', 'Site Manager'), ('category_ids', 'in', tag_id.id)], limit=1)
        head_finance_id = self.env['hr.employee'].search([('job_title', '=', 'Head of Finance'), ('category_ids', 'in', tag_id.id)], limit=1)
        head_scm_id = self.env['hr.employee'].search([('job_title', '=', 'Head of SCM'), ('category_ids', 'in', tag_id.id)], limit=1)
        deputy_gm_id = self.env['hr.employee'].search([('job_title', '=', 'Deputy General Manager'), ('category_ids', 'in', tag_id.id)], limit=1)
        general_manager_id = self.env['hr.employee'].search([('job_title', '=', 'General Manager'), ('category_ids', 'in', tag_id.id)], limit=1)
        checked_by_id = self.env['hr.employee'].search([('checked_by', '=', True), ('category_ids', 'in', tag_id.id)], limit=1)
        known_by_id = self.env['hr.employee'].search([('known_by', '=', True), ('category_ids', 'in', tag_id.id)], limit=1)
        if site_manager_id:
            self.site_manager_id = site_manager_id.id
        else:
            self.site_manager_id = False
        if head_finance_id:
            self.head_finance_id = head_finance_id.id
        else:
            self.head_finance_id = False
        if head_scm_id:
            self.head_scm_id = head_scm_id.id
        else:
            self.head_scm_id = False
        if deputy_gm_id:
            self.deputy_gm_id = deputy_gm_id.id
        else:
            self.deputy_gm_id = False
        if general_manager_id:
            self.general_manager_id = general_manager_id.id
        else:
            self.general_manager_id = False
        if checked_by_id:
            self.checked_by_id = checked_by_id.id
        else:
            self.checked_by_id = False
        if known_by_id:
            self.known_by_id = known_by_id.id
        else:
            self.known_by_id = False

    def _compute_assign(self):
        for rec in self:
            emp_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
            if not emp_id:
                raise UserError(
                    _("User Id belum di link dengan employee"))
            else:
                if not emp_id.parent_id:
                    raise UserError(
                        _("Field Manager pada employee belum diisi"))

                else:
                    rec.assigned_to = emp_id.paren_id.id

    appr1 = fields.Many2one(
        comodel_name="res.users",
        string="Approved By",
        copy=False,
        track_visibility="onchange",
        compute='_default_approval',
        store=True
    )
    description = fields.Text(string="Description")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=_company_get,
        track_visibility="onchange",
    )
    line_ids = fields.One2many(
        comodel_name="purchase.request.line",
        inverse_name="request_id",
        string="Products to Purchase",
        readonly=False,
        copy=True,
        track_visibility="onchange",
    )
    approval_matrix_ids = fields.One2many(
        comodel_name="approval.matrix",
        inverse_name="purchase_request_id",
        string="Approval Matrix",
        readonly=True,
        copy=False,
        track_visibility="onchange",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="line_ids.product_id",
        string="Product",
        readonly=True
    )
    harga_total = fields.Monetary(
        string="Total",
        currency_field="currency_id",
        compute="_compute_total",
        track_visibility="onchange",
    )
    tipe_pr = fields.Selection(
        selection=[
            ("Single_RFQ", "Single RFS"),
            ("Multi_RFQ", "Multi RFQ")],
        string="Tipe PR", )
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        track_visibility="onchange",
        required=True,
        copy=False,
        default="draft",
    )
    # priority = fields.Selection(
    #     selection=[
    #         ("normal", "NORMAL"),
    #         ("urgent", "URGENT"),
    #         ("top_urgent", "TOP URGENT"),],
    #     string="Priority",
    #     index=True,
    #     track_visibility="onchange",
    #     required=True,
    #     copy=True,)
    priority = fields.Many2one(
        comodel_name="priority",
        string="Priority")
    priority_allow = fields.Boolean(compute="_compute_priority_allow")
    is_editable = fields.Boolean(
        string="Is editable", compute="_compute_is_editable", readonly=True
    )
    to_approve_allowed = fields.Boolean(compute="_compute_to_approve_allowed")
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Picking Type",
        required=True,
        default=_default_picking_type,
        domain=lambda self: [
            (
                "name",
                "=",
                'Receipts',
            )
        ],
    )
    group_id = fields.Many2one(
        comodel_name="procurement.group",
        string="Procurement Group",
        copy=False,
        index=True,
    )
    proc_group_id = fields.Many2one(
        comodel_name="tbl_proc_group",
        string="Procurement Category",
        copy=True,
        index=True,
    )
    line_count = fields.Integer(
        string="Purchase Request Line count",
        compute="_compute_line_count",
        readonly=True,
    )
    move_count = fields.Integer(
        string="Stock Move count", compute="_compute_move_count", readonly=True
    )
    purchase_count = fields.Integer(
        string="Purchases count", compute="_compute_purchase_count", readonly=True
    )
    rfq_count = fields.Integer(
        string="RFQ Count", compute="_compute_rfq_purchase_count", readonly=True, store=True
    )
    po_count = fields.Integer(
        string="PO Count", compute="_compute_rfq_purchase_count", readonly=True, store=True
    )
    cah_count = fields.Integer(
        string="CAH Count", compute="_compute_cas_sundry_noi_count", readonly=True
    )
    cas_count = fields.Integer(
        string="CAS Count", compute="_compute_cas_sundry_noi_count", readonly=True
    )
    sundary_site_count = fields.Integer(
        string="Sundary Count", compute="_compute_cas_sundry_noi_count", readonly=True
    )
    noi_count = fields.Integer(
        string="Noi Count", compute="_compute_cas_sundry_noi_count", readonly=True
    )
    note = fields.Text(
        string="Notes"
    )
    alasan_reject = fields.Text(
        string="Reason for Rejection",
        track_visibility="onchange"
    )
    alasan_cancel = fields.Text(
        string="Reason for Cancel",
        track_visibility="onchange"
    )
    alasan_done = fields.Text(
        string="Reason for Done",
        track_visibility="onchange"
    )
    next_approver = fields.Many2one('res.users', 'Next Approval User', compute="_compute_next_approver", readonly=True,
                                    track_visibility="onchange", store=True)
    procurement_officer = fields.Many2one('res.users', 'Procurement Officer', track_visibility="onchange")
    last_approve_date = fields.Datetime('Last Approve Date', copy=False, compute="_compute_last_approve_date",
                                        readonly=True, track_visibility="onchange", store=True)

    def _compute_cas_sundry_noi_count(self):
        for rec in self:
            cah_count               = self.env['cash.advance.ho'].search([('purchase_request_id','=',rec.id)])
            cas_count               = self.env['cash.advance.site'].search([('purchase_request_id','=',rec.id)])
            sundary_site_count      = self.env['sundry'].search([('purchase_request_id','=',rec.id)])
            noi_count               = self.env['noi'].search([('purchase_request_id','=',rec.id)])
            rec.cah_count           = len(cah_count)
            rec.cas_count           = len(cas_count)
            rec.sundary_site_count  = len(sundary_site_count)
            rec.noi_count           = len(noi_count)

    @api.depends('state')
    def _default_approval(self):
        for allrec in self:
            allapproval = self.env['tbl_matrix_auth'].search(
                [('modul', '=', allrec.modul),('proc_group_id','=',allrec.proc_group_id.id),('company_id','=',allrec.company_id.id),('tag_warehouse', 'in', allrec.picking_type_id.warehouse_id.id), ('value_awal', '<=', allrec.harga_total)])
            # if allapproval.mapped('department_id'):
            #     allapproval = allapproval.filtered(lambda e: e.department_id == allrec.department_id)
            # if not allapproval and allrec.state != 'draft':
            #     raise UserError("Please Setting Matrix Approval For Purchase Request first ")
            # else:
            allrec.appr1 = allapproval.filtered(lambda e: e.level == '1').filtered(lambda e: e.department_id == allrec.department_id if e.mapped('department_id') else e).approval_user.id if allapproval.filtered(lambda e: e.level == '1') else False
            allrec.appr2 = allapproval.filtered(lambda e: e.level == '2').filtered(lambda e: e.department_id == allrec.department_id if e.mapped('department_id') else e).approval_user.id if allapproval.filtered(lambda e: e.level == '2') else False
            allrec.appr3 = allapproval.filtered(lambda e: e.level == '3').filtered(lambda e: e.department_id == allrec.department_id if e.mapped('department_id') else e).approval_user.id if allapproval.filtered(lambda e: e.level == '3') else False
            allrec.appr4 = allapproval.filtered(lambda e: e.level == '4').filtered(lambda e: e.department_id == allrec.department_id if e.mapped('department_id') else e).approval_user.id if allapproval.filtered(lambda e: e.level == '4') else False
            allrec.appr5 = allapproval.filtered(lambda e: e.level == '5').filtered(lambda e: e.department_id == allrec.department_id if e.mapped('department_id') else e).approval_user.id if allapproval.filtered(lambda e: e.level == '5') else False
            allrec.appr6 = allapproval.filtered(lambda e: e.level == '6').filtered(lambda e: e.department_id == allrec.department_id if e.mapped('department_id') else e).approval_user.id if allapproval.filtered(lambda e: e.level == '6') else False
            allrec.appr7 = allapproval.filtered(lambda e: e.level == '7').filtered(lambda e: e.department_id == allrec.department_id if e.mapped('department_id') else e).approval_user.id if allapproval.filtered(lambda e: e.level == '7') else False
            allrec.appr8 = allapproval.filtered(lambda e: e.level == '8').filtered(lambda e: e.department_id == allrec.department_id if e.mapped('department_id') else e).approval_user.id if allapproval.filtered(lambda e: e.level == '8') else False

    def _compute_priority_allow(self):
        user_id = self.env.user.id
        if self.assigned_to.id != user_id:
            self.priority_allow = False
        else:
            self.priority_allow = True

    def _valid_field_parameter(self, field, name):
        return name == "track_visibility" or super()._valid_field_parameter(field, name)

    @api.depends("line_ids")
    def _compute_purchase_count(self):
        for rec in self:
            rec.purchase_count = len(rec.mapped("line_ids.purchase_lines.order_id"))

    @api.depends("line_ids", "line_ids.purchase_lines", "line_ids.purchase_lines.order_id",
                 "line_ids.purchase_lines.order_id.state")
    def _compute_rfq_purchase_count(self):
        for rec in self:
            rfq_orders = rec.mapped("line_ids.purchase_lines.order_id").filtered(
                lambda order: order.state in ('draft', 'sent','cancel'))
            po_orders = rec.mapped("line_ids.purchase_lines.order_id").filtered(
                lambda order: order.state not in ('draft', 'sent', 'cancel'))

            rec.po_count = len(po_orders)
            rec.rfq_count = len(rfq_orders)

    def action_view_purchase_order(self):
        action = self.env.ref("purchase.purchase_rfq").read()[0]
        lines = self.mapped("line_ids.purchase_lines.order_id")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = lines.id
        return action

    def action_view_po(self):
        action = self.env.ref("purchase.purchase_rfq").read()[0]
        lines = self.mapped("line_ids.purchase_lines.order_id").filtered(
            lambda order: order.state not in ('draft', 'sent', 'cancel'))
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = lines.id
        return action

    def action_view_cah(self):
        action = self.env.ref("yudha_ca_ho.action_cash_advance_ho").read()[0]
        cah_count               = self.env['cash.advance.ho'].search([('purchase_request_id','=',self.id)])
            
        if len(cah_count) > 1:
            action["domain"] = [("id", "in", cah_count.ids)]
        elif cah_count:
            action["views"] = [
                (self.env.ref("yudha_ca_ho.view_ca_ho_form").id, "form")
            ]
            action["res_id"] = cah_count.id
        return action

    def action_view_cas(self):
        action = self.env.ref("yudha_ca_site.action_cash_advance_site").read()[0]
        cas_count               = self.env['cash.advance.site'].search([('purchase_request_id','=',self.id)])
            
        if len(cas_count) > 1:
            action["domain"] = [("id", "in", cas_count.ids)]
        elif cas_count:
            action["views"] = [
                (self.env.ref("yudha_ca_site.view_ca_site_form").id, "form")
            ]
            action["res_id"] = cas_count.id
        return action

    def action_view_sundary_site(self):
        action = self.env.ref("sundry_custom.action_sundry").read()[0]
        sundary_site_count      = self.env['sundry'].search([('purchase_request_id','=',self.id)])
            
        if len(sundary_site_count) > 1:
            action["domain"] = [("id", "in", sundary_site_count.ids)]
        elif sundary_site_count:
            action["views"] = [
                (self.env.ref("sundry_custom.view_sundry_form").id, "form")
            ]
            action["res_id"] = sundary_site_count.id
        return action
    
    def action_view_noi(self):
        action = self.env.ref("noi_custom.action_noi").read()[0]
        noi_count               = self.env['noi'].search([('purchase_request_id','=',self.id)])
        if len(noi_count) > 1:
            action["domain"] = [("id", "in", noi_count.ids)]
        elif noi_count:
            action["views"] = [
                (self.env.ref("noi_custom.view_noi_form").id, "form")
            ]
            action["res_id"] = noi_count.id
        return action

    def action_view_rfq(self):
        action = self.env.ref("purchase.purchase_rfq").read()[0]
        lines = self.mapped("line_ids.purchase_lines.order_id").filtered(lambda order: order.state in ('draft', 'sent','cancel'))
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = lines.id
        return action

    @api.depends("line_ids")
    def _compute_move_count(self):
        for rec in self:
            rec.move_count = len(
                rec.mapped("line_ids.purchase_request_allocation_ids.stock_move_id")
            )

    def action_view_stock_move(self):
        action = self.env.ref("stock.stock_move_action").read()[0]
        # remove default filters
        action["context"] = {}
        lines = self.mapped("line_ids.purchase_request_allocation_ids.stock_move_id")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [(self.env.ref("stock.view_move_form").id, "form")]
            action["res_id"] = lines.id
        return action

    @api.depends("line_ids")
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.mapped("line_ids"))

    @api.depends("line_ids", "line_ids.estimated_cost")
    def _compute_total(self):
        for rec in self:
            rec.harga_total = 0
            for tot in rec.line_ids:
                rec.harga_total += tot.estimated_cost

    def action_view_purchase_request_line(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "purchase_request.purchase_request_line_form_action"
        )
        lines = self.mapped("line_ids")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase_request.purchase_request_line_form").id, "form")
            ]
            action["res_id"] = lines.ids[0]
        return action

    @api.depends("state", "line_ids.product_qty", "line_ids.cancelled")
    def _compute_to_approve_allowed(self):
        for rec in self:
            rec.to_approve_allowed = rec.state == "draft" and any(
                not line.cancelled and line.product_qty for line in rec.line_ids
            )

    @api.depends("state", "prepared_by", "recommended_by", "checked_by", "verified_by", "assigned_to", "appr1", "appr2",
                 "appr3", "appr4")
    def _compute_next_approver(self):
        for rec in self:
            if rec.state == 'to_request_approve' and rec.prepared_by:
                rec.next_approver = rec.prepared_by.id
            elif rec.state == 'to_recommend' and rec.recommended_by:
                rec.next_approver = rec.recommended_by.id
            elif rec.state == 'to_check' and rec.checked_by:
                rec.next_approver = rec.checked_by.id
            elif rec.state == 'to_verify' and rec.verified_by:
                rec.next_approver = rec.verified_by.id
            elif rec.state == 'to_approve' and rec.assigned_to:
                rec.next_approver = rec.assigned_to.id
            elif rec.state == 'to_approve1' and rec.appr1:
                rec.next_approver = rec.appr1.id
            elif rec.state == 'to_approve2' and rec.appr2:
                rec.next_approver = rec.appr2.id
            elif rec.state == 'to_approve3' and rec.appr3:
                rec.next_approver = rec.appr3.id
            elif rec.state in ('to_approve4',) and rec.appr4:
                rec.next_approver = rec.appr4.id
            elif rec.state == 'to_approve5' and rec.appr5:
                rec.next_approver = rec.appr5.id
            elif rec.state == 'to_approve6' and rec.appr6:
                rec.next_approver = rec.appr6.id
            elif rec.state == 'to_approve7' and rec.appr7:
                rec.next_approver = rec.appr7.id
            elif rec.state in ('to_approve8',) and rec.appr8:
                rec.next_approver = rec.appr8.id
            else:
                rec.next_approver = False

    @api.depends("state", "assign_to_dt", "appr1_dt", "appr2_dt", "appr3_dt", "appr4_dt")
    def _compute_last_approve_date(self):
        for rec in self:
            rec.last_approve_date = ''
            if rec.state in ('approved', 'done'):
                if rec.appr4_dt:
                    rec.last_approve_date = rec.appr4_dt
                elif rec.appr3_dt:
                    rec.last_approve_date = rec.appr3_dt
                elif rec.appr2_dt:
                    rec.last_approve_date = rec.appr2_dt
                elif rec.appr1_dt:
                    rec.last_approve_date = rec.appr1_dt
                elif rec.assign_to_dt:
                    rec.last_approve_date = rec.assign_to_dt

    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update({"state": "draft", "name": self._get_default_name()})
        return super(PurchaseRequest, self).copy(default)

    @api.model
    def _get_partner_id(self, request):
        user_id = request.assigned_to or self.env.user
        return user_id.partner_id.id

    @api.model
    def create(self, vals):
        request = super(PurchaseRequest, self).create(vals)
        if vals.get("assigned_to"):
            partner_id = self._get_partner_id(request)
            request.message_subscribe(partner_ids=[partner_id])
        return request

    def write(self, vals):
        res = super(PurchaseRequest, self).write(vals)
        for request in self:
            if vals.get("assigned_to"):
                partner_id = self._get_partner_id(request)
                request.message_subscribe(partner_ids=[partner_id])
        return res

    def _can_be_deleted(self):
        self.ensure_one()
        return self.state == "draft"

    def unlink(self):
        for request in self:
            if not request._can_be_deleted():
                raise UserError(
                    _("You cannot delete a purchase request which is not draft.")
                )
            if request.line_ids:
                request.line_ids.unlink()
        return super(PurchaseRequest, self).unlink()

    # def action_send_email(self):
    #     template_id = self.env.ref("purchase_request.email_template_notif_pr").id
    #     template = self.env['mail.template'].browse(template_id)
    #     template.send_mail(self.id, force_send=True)

    def get_portal_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        action_id = 575  # Gantilah dengan ID aksi yang sesuai
        menu_id = 403  # Gantilah dengan ID menu yang sesuai

        return f"{base_url}/web?#id={self.id}&action={action_id}&model=purchase.request&view_type=form&cids={self.company_id.id}&menu_id={menu_id}"

    def action_print_pr(self):
        return self.env.ref('purchase_request.print_pr_rmb_cek_rekomend_a1').report_action(self)
        # record = self.env['ir.model.data'].search([
        #     ('model', '=', 'ir.actions.report'),
        #     ('name', '=', 'print_po_rmb_a2')
        # ], limit=1)
        # raise UserError(
        #             _(record[0].res_id)
        #         )
        # RMB==============================================================================
    # if self.company_id and self.company_id.name == 'PT NEXIS ENERGY INVESTAMA':
    #         if self.checked_by and not self.recommended_by:
    #             if not self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_cek_a1').report_action(self)
    #             if not self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_cek_a2').report_action(self)
    #             if self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_cek_a3').report_action(self)
    #             if self.appr1 and self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_cek_a4').report_action(self)
    #             if self.appr1 and self.appr2 and self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_cek_a5').report_action(self)
    #
    #         if self.recommended_by and not self.checked_by:
    #             if not self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_recomend_a1').report_action(self)
    #             if self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_recomend_a2').report_action(self)
    #             if self.appr1 and self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_recomend_a3').report_action(self)
    #             if self.appr1 and self.appr2 and self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_recomend_a4').report_action(self)
    #             if self.appr1 and self.appr2 and self.appr3 and self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_recomend_a5').report_action(self)
    #
    #         if self.checked_by and self.recommended_by:
    #             if not self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 # return self.env.ref('__import__.print_pr_rmb_rekomen_a1_qweb').report_action(self)
    #                 return self.env.ref('purchase_request.print_pr_rmb_cek_rekomend_a1').report_action(self)
    #             if self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_cek_rekomend_a2').report_action(self)
    #             if self.appr1 and self.appr2 and not self.appr3 and not self.appr4:
    #                 # raise UserError(
    #                 #     _("appr3")
    #                 # )
    #                 return self.env.ref('__import__.print_pr_rmb_cek_rekomend_a3').report_action(self)
    #             if self.appr1 and self.appr2 and self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_cek_rekomend_a4').report_action(self)
    #             if self.appr1 and self.appr2 and self.appr3 and self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_cek_rekomend_a5').report_action(self)
    #
    #         if not self.checked_by and not self.recommended_by:
    #             if not self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_verify_a1').report_action(self)
    #             if self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_verify_a2').report_action(self)
    #             if self.appr1 and self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_verify_a3').report_action(self)
    #             if self.appr1 and self.appr2 and self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_verify_a4').report_action(self)
    #             if self.appr1 and self.appr2 and self.appr3 and self.appr4:
    #                 return self.env.ref('__import__.print_pr_rmb_verify_a5').report_action(self)
    #     # IBP===========================================================================
    #     if self.company_id and self.company_id.name == 'PT INDO BARA PRATAMA':
    #         if self.checked_by and not self.recommended_by:
    #             if not self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_cek_a1').report_action(self)
    #             if not self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_cek_a2').report_action(self)
    #             if self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_cek_a3').report_action(self)
    #             if self.appr1 and self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_cek_a4').report_action(self)
    #             if self.appr1 and self.appr2 and self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_cek_a5').report_action(self)
    #
    #         if self.recommended_by and not self.checked_by:
    #             if not self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_recomend_a1').report_action(self)
    #             if self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_recomend_a2').report_action(self)
    #             if self.appr1 and self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_recomend_a3').report_action(self)
    #             if self.appr1 and self.appr2 and self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_recomend_a4').report_action(self)
    #             if self.appr1 and self.appr2 and self.appr3 and self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_recomend_a5').report_action(self)
    #
    #         if self.checked_by and self.recommended_by:
    #             if not self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_cek_rekomend_a1').report_action(self)
    #             if self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_cek_rekomend_a2').report_action(self)
    #             if self.appr1 and self.appr2 and not self.appr3 and not self.appr4:
    #                 # raise UserError(
    #                 #     _("appr3")
    #                 # )
    #                 return self.env.ref('__import__.print_pr_ibp_cek_rekomend_a3').report_action(self)
    #             if self.appr1 and self.appr2 and self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_cek_rekomend_a4').report_action(self)
    #             if self.appr1 and self.appr2 and self.appr3 and self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_cek_rekomend_a5').report_action(self)
    #
    #         if not self.checked_by and not self.recommended_by:
    #             if not self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_verify_a1').report_action(self)
    #             if self.appr1 and not self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_verify_a2').report_action(self)
    #             if self.appr1 and self.appr2 and not self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_verify_a3').report_action(self)
    #             if self.appr1 and self.appr2 and self.appr3 and not self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_verify_a4').report_action(self)
    #             if self.appr1 and self.appr2 and self.appr3 and self.appr4:
    #                 return self.env.ref('__import__.print_pr_ibp_verify_a5').report_action(self)
    def button_create_cash_advance_ho(self):
        for item in self:
            vals = {
                "request_date": fields.Datetime.now(),
                "warehouse_id": item.picking_type_id.warehouse_id.id,
                "user_id":item.prepared_by.id,
                "request_by": item.requested_by.partner_id.id,
                "purchase_request_id":item.id,
            }
            cas_id =self.env['cash.advance.ho'].sudo().create(vals)
            for line in item.line_ids:
                vals_line = {
                    "description": line.specifications,
                    "ca_ho_id": cas_id.id,
                }
                casl_id =self.env['cash.advance.holine'].sudo().create(vals_line)
            item.update_source_document()

    def button_create_cash_advance_site(self):
        for item in self:
            vals = {
                "request_date": fields.Datetime.now(),
                "warehouse_id": item.picking_type_id.warehouse_id.id,
                "user_id":item.prepared_by.id,
                "request_by": item.requested_by.partner_id.id,
                "purchase_request_id":item.id,
            }
            cas_id =self.env['cash.advance.site'].sudo().create(vals)
            for line in item.line_ids:
                vals_line = {
                    "description": line.specifications,
                    "ca_site_id": cas_id.id,
                }
                casl_id =self.env['cash.advance.siteline'].sudo().create(vals_line)
            item.update_source_document()

    def button_create_sundry_site(self):
        for item in self:
            vals = {
                "request_date": fields.Datetime.now(),
                "ref": item.name,
                "payment_type": "outbound",
                "warehouse_id": item.picking_type_id.warehouse_id.id,
                "user_id":item.prepared_by.id,
                "request_by": item.requested_by.partner_id.id,
                "purchase_request_id":item.id,
            }
            cas_id =self.env['sundry'].sudo().create(vals)
            item.update_source_document()

    def button_create_noi(self):
        for item in self:
            vals = {
                "request_date": fields.Datetime.now(),
                "ref": item.name,
                "payment_type": "outbound",
                "warehouse_id": item.picking_type_id.warehouse_id.id,
                "user_id":item.prepared_by.id,
                "request_by": item.requested_by.partner_id.id,
                "purchase_request_id":item.id,
            }
            noi_id =self.env['noi'].sudo().create(vals)
            item.update_source_document()

    def button_draft(self):
        self.mapped("line_ids").do_uncancel()
        return self.write({"state": "draft"})
    def button_to_prepare(self):
        self.todo_user_ids = [self.requested_by.id]
        self.prepare_dt = fields.Datetime.now()
        self.state = 'to_request_approve'
        
    def button_to_check(self):
        self.state = 'to_approve'
        self.checked_dt = fields.Datetime.now()
    def button_to_approve(self):

        # self.appr1_dt = fields.Datetime.now()
        if self.line_ids:
            for line in self.line_ids:
                if not line.estimated_price_unit or line.estimated_price_unit == 0 or line.estimated_price_unit == 0.0:
                    raise UserError(_("Price unit must not be 0."))
        if self.requested_by.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        emp_id = self.env['tbl_matrix_auth'].search([('modul', '=', self.modul), ('level', '=', '1')], limit=1)
        if emp_id and not self.assigned_to:
            self.assigned_to = emp_id.approval_user.id
        self.to_approve_allowed_check()
        for ck in self.line_ids:
            if not ck.date_required:
                raise UserError(
                    _("Date Required pada Line ada yg belum diisi (%s)") % ck.name)
        if self.name == 'New':
            self.name = self.env["ir.sequence"].next_by_code("purchase.request")
        if self.requested_by.id == self.prepared_by.id:
            self.prepare_dt = fields.Datetime.now()
            # self.spv_dt = fields.Datetime.now()
            self.state = 'to_approve'
            # if self.checked_by and self.recommended_by:
            #     self.status_vrecomend = 1
            #     self.status_vcheck = 1
            #     self.status_recomend = 1
            #     self.status_check = 1
            #     self.state = 'to_recommend'
            # if self.recommended_by and not self.checked_by:
            #         self.status_vrecomend = 1
            #         self.state = 'to_recommend'
            # if  self.checked_by and not self.recommended_by:
            #             self.status_vcheck = 1
            #             self.state = 'to_check'
            # if not self.checked_by and not self.recommended_by:
            #                 self.state = 'to_verify'
        if self.requested_by.id != self.prepared_by.id:
            self.state = 'to_request_approve'
            self.requested_dt = fields.Datetime.now()

        # return self.action_send_email()

    def button_to_approve_request(self):
        if self.requested_by.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        # self.prepare_dt = fields.Datetime.now()
        self.requested_dt = fields.Datetime.now()
        # self.state = 'to_check'
        self.approval_matrix_ids.unlink()
        self.create_approval_matrix()
        if not self.approval_matrix_ids:
            raise UserError(
                _("Approval Matrix not found, Please Check Config Approval Matrix"))
        emp_id = self.env['approval.matrix'].search([('purchase_request_id','=',self.id),('realization_user_id','=',False)],limit=1,order="state asc")
        if emp_id:
            self.todo_user_ids = [(6, 0, emp_id.config_approval_matrix_id.approval_user_ids.ids)]
        self.state = 'to_approve_matrix'
        
        if self.name == 'New':
            self.name = self.env["ir.sequence"].next_by_code("purchase.request")
        # if self.checked_by and self.recommended_by:
        #         self.status_vrecomend = 1
        #         self.status_vcheck = 1
        #         self.status_recomend = 1
        #         self.status_check = 1
        #         self.state = 'to_recommend'
        # if self.recommended_by and not self.checked_by:
        #             self.status_vrecomend = 1
        #             self.state = 'to_recommend'
        # if  self.checked_by and not self.recommended_by:
        #                 self.status_vcheck = 1
        #                 self.state = 'to_check'
        # if not self.checked_by and not self.recommended_by:
        #                     self.state = 'to_verify'
        # return self.action_send_email()

    def button_recommend(self):
        self.recommended_dt = fields.Datetime.now()
        if self.recommended_by.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))

        if self.recommended_by and not self.checked_by:
            self.state = 'to_verify'
            self.status_vrecomend = 0
        if self.recommended_by and self.checked_by:
            if self.status_check == 1:
                self.status_recomend = 0
                self.state = 'to_check'
                self.status_vrecomend = 0
            else:
                self.status_recomend = 0
                self.state = 'to_verify'
                self.status_vrecomend = 0
        # return self.action_send_email()

    def button_check(self):
        self.checked_dt = fields.Datetime.now()
        if self.checked_by.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        if self.checked_by.id == self.env.uid:
            self.state = 'to_approve'

        # if self.checked_by and not self.recommended_by:
        #     self.state = 'to_verify'
        #     self.status_vcheck = 0
        # if self.recommended_by and self.checked_by:
        #     if self.status_recomend == 1:
        #         self.status_check = 0
        #         self.state = 'to_recommend'
        #         self.status_vcheck = 0
        #     else:
        #         self.status_check = 0
        #         self.state = 'to_verify'
        #         self.status_vcheck = 0
        # return self.action_send_email()

    def button_verify(self):
        if self.verified_by.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.state = 'to_approve'
        self.verify_dt = fields.Datetime.now()
        emp_id = self.env['tbl_matrix_auth'].search(
            [('modul', '=', self.modul),
             ('proc_group_id', '=', self.proc_group_id.id), ('level', '=', '1')], limit=1)
        # if not emp_id:
        #              raise UserError(
        #                  _("Tidak Diditemukan pada authorization matrix"))
        if emp_id and not self.assigned_to:
            self.assigned_to = emp_id.approval_user.id
        # if emp_id and not self.assigned_to:
        self.todo_user = self.assigned_to.id
        # return self.action_send_email()

    def button_approved_matrix(self):
        emp_id = self.env['approval.matrix'].search([('purchase_request_id','=',self.id),('realization_user_id','=',False)],limit=1,order="state asc")
        if emp_id:
            if self.env.uid in (emp_id.config_approval_matrix_id.approval_user_ids.ids) or emp_id.config_approval_matrix_id.delegate_user.id == self.env.uid:
                emp_id.write({'realization_user_id':self.env.uid,"date": fields.Datetime.now()})
                emp_id = self.env['approval.matrix'].search([('purchase_request_id','=',self.id),('realization_user_id','=',False)],limit=1,order="state asc")
                if not emp_id:
                    self.todo_user_ids = False
                    self.state = 'approved'
                else:
                    self.todo_user_ids = [(6, 0, emp_id.config_approval_matrix_id.approval_user_ids.ids)]
            else:
                raise UserError(
                    _("Anda tidak berhak melakukan proses ini"))

    def button_approved(self):
        if self.assigned_to.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        emp_id = self.env['config.approval.matrix'].search([('modul', '=', self.modul),('proc_group_id','=',self.proc_group_id.id),('company_id','=',self.company_id.id),('department_id','=',self.department_id.id)], limit=1, order="matrix_level_name asc")
        if emp_id:
            print('=====>>>>>MASUK')
            self.assign_to_dt = fields.Datetime.now()
            if self.harga_total < emp_id.expected_amount:
                self.state = 'approved'
                if self.name == 'New':
                    self.name = self.env["ir.sequence"].next_by_code("purchase.request")
                # self.assign_to_dt = fields.Datetime.now()
                for item in self.line_ids:
                    if item.estimated_cost == 0:
                        raise UserError(
                            _("Sub Total tidak boleh 0"))

                    if item.product_id:
                        analytic_obj = self.env["crossovered.budget.lines"]
                        # subpo_obj = self.env["tbl_budget_est_practical"]
                        skrg = fields.Date.today()
                        analitik = analytic_obj.search(
                            [("analytic_account_id", "=", item.analytic_account_id.id),
                            ("date_from", "<=", self.date_start), ("date_to", ">=", self.date_start)]
                        )
                        # if analitik:
                        #     subpo_obj.create({
                        #         'details': analitik.id,
                        #         'tipe': 'PR',
                        #         'date': self.date_start,
                        #         'desc': self.name,
                        #         'amount': item.estimated_cost,
                        #     })
                # return self.action_send_email()
            if self.harga_total > emp_id.expected_amount:
                self.state = 'to_approve_matrix'
                # self.appr1 = emp_id.approval_user.id  # emp.approve_user.id
                # self.is_appr1 = True
                self.todo_user = emp_id.approval_user.id
                # return self.action_send_email()

        if not emp_id:
            # raise UserError(
            #         _('Tidak ditemukan pada Matrix Auth')
            #     )
            self.assign_to_dt = fields.Datetime.now()
            self.state = 'approved'
            if self.name == 'New':
                self.name = self.env["ir.sequence"].next_by_code("purchase.request")
            # self.assign_to_dt = fields.Datetime.now()
            for item in self.line_ids:
                if item.estimated_cost == 0:
                    raise UserError(
                        _("Sub Total tidak boleh 0"))

                if item.product_id:
                    analytic_obj = self.env["crossovered.budget.lines"]
                    # subpo_obj = self.env["tbl_budget_est_practical"]
                    skrg = fields.Date.today()
                    analitik = analytic_obj.search(
                        [("analytic_account_id", "=", item.analytic_account_id.id),
                         ("date_from", "<=", self.date_start), ("date_to", ">=", self.date_start)]
                    )
                    # if analitik:
                    #     subpo_obj.create({
                    #         'details': analitik.id,
                    #         'tipe': 'PR',
                    #         'date': self.date_start,
                    #         'desc': self.name,
                    #         'amount': item.estimated_cost,
                    #     })
            # return self.action_send_email()

        # self.write({"state": "to_approve1"})

        # return

    def button_approved1(self):
        emp_id = self.env['tbl_matrix_auth'].search(
            [('modul', '=', self.modul),('proc_group_id','=',self.proc_group_id.id),('company_id','=',self.company_id.id),('level', '=', '2')], limit=1)
        
        self.appr1_dt = fields.Datetime.now()
        if not self.appr1:
            raise UserError(
                _("Field Approved By belum diisi"))
        if self.appr1.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))

        if emp_id:
            if self.harga_total < emp_id.value_awal:
                self.state = 'approved'
                # self.appr1_dt = fields.Datetime.now()
                for item in self.line_ids:
                    if item.product_id:
                        analytic_obj = self.env["crossovered.budget.lines"]
                        # subpo_obj = self.env["tbl_budget_est_practical"]
                        skrg = fields.Date.today()
                        analitik = analytic_obj.search(
                            [("analytic_account_id", "=", item.analytic_account_id.id),
                             ("date_from", "<=", self.date_start), ("date_to", ">=", self.date_start)]
                        )
                        # if analitik:
                        #     subpo_obj.create({
                        #         'details': analitik.id,
                        #         'tipe': 'PR',
                        #         'date': self.date_start,
                        #         'desc': self.name,
                        #         'amount': item.estimated_cost,
                        #     })
                # return self.action_send_email()
            if self.harga_total > emp_id.value_awal:
                self.state = 'to_approve2'
                # self.appr2 = emp_id.approval_user.id  # emp.approve_user.id
                self.is_appr2 = True
                self.todo_user = emp_id.approval_user.id
                # return self.action_send_email()
        
        if not emp_id:
            self.state = 'approved'

    def button_approved2(self):
        emp_id = self.env['tbl_matrix_auth'].search(
            [('modul', '=', self.modul),('proc_group_id','=',self.proc_group_id.id),('company_id','=',self.company_id.id), ('level', '=', '3')], limit=1)
        self.appr2_dt = fields.Datetime.now()
        if not self.appr2:
            raise UserError(
                _("Field Approved By belum diisi"))
        if self.appr2.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        
        if emp_id:
            if self.harga_total < emp_id.value_awal:
                self.state = 'approved'
                # self.appr2_dt = fields.Datetime.now()
                for item in self.line_ids:
                    if item.product_id:
                        analytic_obj = self.env["crossovered.budget.lines"]
                        # subpo_obj = self.env["tbl_budget_est_practical"]
                        skrg = fields.Date.today()
                        analitik = analytic_obj.search(
                            [("analytic_account_id", "=", item.analytic_account_id.id),
                             ("date_from", "<=", self.date_start), ("date_to", ">=", self.date_start)]
                        )
                        # if analitik:
                        #     subpo_obj.create({
                        #         'details': analitik.id,
                        #         'tipe': 'PR',
                        #         'date': self.date_start,
                        #         'desc': self.name,
                        #         'amount': item.estimated_cost,
                        #     })
                # return self.action_send_email()
            if self.harga_total > emp_id.value_awal:
                self.state = 'to_approve3'
                # self.appr3 = emp_id.approval_user.id  # emp.approve_user.id
                self.is_appr3 = True
                self.todo_user = emp_id.approval_user.id
                # return self.action_send_email()
        
        if not emp_id:
            self.state = 'approved'

    def button_approved3(self):
        emp_id = self.env['tbl_matrix_auth'].search(
            [('modul', '=', self.modul),('proc_group_id','=',self.proc_group_id.id),('company_id','=',self.company_id.id),('level', '=', '4')], limit=1)
        self.appr3_dt = fields.Datetime.now()
        if not self.appr3:
            raise UserError(
                _("Field Approved By belum diisi"))
        if self.appr3.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))

        if emp_id:
            if self.harga_total < emp_id.value_awal:
                self.state = 'approved'
                # self.appr3_dt = fields.Datetime.now()
                for item in self.line_ids:
                    if item.product_id:
                        analytic_obj = self.env["crossovered.budget.lines"]
                        # subpo_obj = self.env["tbl_budget_est_practical"]
                        skrg = fields.Date.today()
                        analitik = analytic_obj.search(
                            [("analytic_account_id", "=", item.analytic_account_id.id),
                             ("date_from", "<=", self.date_start), ("date_to", ">=", self.date_start)]
                        )
                        # if analitik:
                        #     subpo_obj.create({
                        #         'details': analitik.id,
                        #         'tipe': 'PR',
                        #         'date': self.date_start,
                        #         'desc': self.name,
                        #         'amount': item.estimated_cost,
                        #     })
                # return self.action_send_email()
            if self.harga_total > emp_id.value_awal:
                self.state = 'to_approve4'
                # self.appr4 = emp_id.approval_user.id  # emp.approve_user.id
                self.is_appr4 = True
                self.todo_user = emp_id.approval_user.id
                # return self.action_send_email()
        
        if not emp_id:
            self.state = 'approved'

    def button_approved4(self):
        emp_id = self.env['tbl_matrix_auth'].search(
            [('modul', '=', self.modul),('proc_group_id','=',self.proc_group_id.id),('company_id','=',self.company_id.id),('level', '=', '5')], limit=1)
        self.appr4_dt = fields.Datetime.now()
        self.todo_user = False
        if not self.appr4:
            raise UserError(
                _("Field Approved By belum diisi"))
        if self.appr4.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))

        if emp_id:
            if self.harga_total < emp_id.value_awal:
                self.state = 'approved'
                # self.appr4_dt = fields.Datetime.now()
                for item in self.line_ids:
                    if item.product_id:
                        analytic_obj = self.env["crossovered.budget.lines"]
                        # subpo_obj = self.env["tbl_budget_est_practical"]
                        skrg = fields.Date.today()
                        analitik = analytic_obj.search(
                            [("analytic_account_id", "=", item.analytic_account_id.id),
                             ("date_from", "<=", self.date_start), ("date_to", ">=", self.date_start)]
                        )
                        # if analitik:
                        #     subpo_obj.create({
                        #         'details': analitik.id,
                        #         'tipe': 'PR',
                        #         'date': self.date_start,
                        #         'desc': self.name,
                        #         'amount': item.estimated_cost,
                        #     })
                # return self.action_send_email()
            if self.harga_total > emp_id.value_awal:
                self.state = 'to_approve5'
                # self.appr5 = emp_id.approval_user.id  # emp.approve_user.id
                self.is_appr5 = True
                self.todo_user = emp_id.approval_user.id
                # return self.action_send_email()
        
        if not emp_id:
            self.state = 'approved'

    def button_approved5(self):
        emp_id = self.env['tbl_matrix_auth'].search(
            [('modul', '=', self.modul),('proc_group_id','=',self.proc_group_id.id),('company_id','=',self.company_id.id),('level', '=', '6')], limit=1)
        self.appr5_dt = fields.Datetime.now()
        self.todo_user = False
        if not self.appr5:
            raise UserError(
                _("Field Approved By belum diisi"))
        if self.appr5.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))

        if emp_id:
            if self.harga_total < emp_id.value_awal:
                self.state = 'approved'
                # self.appr5_dt = fields.Datetime.now()
                for item in self.line_ids:
                    if item.product_id:
                        analytic_obj = self.env["crossovered.budget.lines"]
                        # subpo_obj = self.env["tbl_budget_est_practical"]
                        skrg = fields.Date.today()
                        analitik = analytic_obj.search(
                            [("analytic_account_id", "=", item.analytic_account_id.id),
                             ("date_from", "<=", self.date_start), ("date_to", ">=", self.date_start)]
                        )
                        # if analitik:
                        #     subpo_obj.create({
                        #         'details': analitik.id,
                        #         'tipe': 'PR',
                        #         'date': self.date_start,
                        #         'desc': self.name,
                        #         'amount': item.estimated_cost,
                        #     })
                # return self.action_send_email()
            if self.harga_total > emp_id.value_awal:
                self.state = 'to_approve6'
                # self.appr5 = emp_id.approval_user.id  # emp.approve_user.id
                self.is_appr6 = True
                self.todo_user = emp_id.approval_user.id
                # return self.action_send_email()
        
        if not emp_id:
            self.state = 'approved'

    def button_approved6(self):
        emp_id = self.env['tbl_matrix_auth'].search(
            [('modul', '=', self.modul),('proc_group_id','=',self.proc_group_id.id),('company_id','=',self.company_id.id),('level', '=', '7')], limit=1)
        self.appr6_dt = fields.Datetime.now()
        self.todo_user = False
        if not self.appr6:
            raise UserError(
                _("Field Approved By belum diisi"))
        if self.appr6.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))

        if emp_id:
            if self.harga_total < emp_id.value_awal:
                self.state = 'approved'
                # self.appr6_dt = fields.Datetime.now()
                for item in self.line_ids:
                    if item.product_id:
                        analytic_obj = self.env["crossovered.budget.lines"]
                        # subpo_obj = self.env["tbl_budget_est_practical"]
                        skrg = fields.Date.today()
                        analitik = analytic_obj.search(
                            [("analytic_account_id", "=", item.analytic_account_id.id),
                             ("date_from", "<=", self.date_start), ("date_to", ">=", self.date_start)]
                        )
                        # if analitik:
                        #     subpo_obj.create({
                        #         'details': analitik.id,
                        #         'tipe': 'PR',
                        #         'date': self.date_start,
                        #         'desc': self.name,
                        #         'amount': item.estimated_cost,
                        #     })
                # return self.action_send_email()
            if self.harga_total > emp_id.value_awal:
                self.state = 'to_approve7'
                # self.appr6 = emp_id.approval_user.id  # emp.approve_user.id
                self.is_appr7 = True
                self.todo_user = emp_id.approval_user.id
                # return self.action_send_email()
        
        if not emp_id:
            self.state = 'approved'
            
    def button_approved7(self):
        emp_id = self.env['tbl_matrix_auth'].search(
            [('modul', '=', self.modul),('proc_group_id','=',self.proc_group_id.id),('company_id','=',self.company_id.id),('level', '=', '8')], limit=1)
        self.appr7_dt = fields.Datetime.now()
        self.todo_user = False
        if not self.appr7:
            raise UserError(
                _("Field Approved By belum diisi"))
        if self.appr7.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))

        if emp_id:
            if self.harga_total < emp_id.value_awal:
                self.state = 'approved'
                # self.appr7_dt = fields.Datetime.now()
                for item in self.line_ids:
                    if item.product_id:
                        analytic_obj = self.env["crossovered.budget.lines"]
                        # subpo_obj = self.env["tbl_budget_est_practical"]
                        skrg = fields.Date.today()
                        analitik = analytic_obj.search(
                            [("analytic_account_id", "=", item.analytic_account_id.id),
                             ("date_from", "<=", self.date_start), ("date_to", ">=", self.date_start)]
                        )
                        # if analitik:
                        #     subpo_obj.create({
                        #         'details': analitik.id,
                        #         'tipe': 'PR',
                        #         'date': self.date_start,
                        #         'desc': self.name,
                        #         'amount': item.estimated_cost,
                        #     })
                # return self.action_send_email()
            if self.harga_total > emp_id.value_awal:
                self.state = 'to_approve8'
                # self.appr7 = emp_id.approval_user.id  # emp.approve_user.id
                self.is_appr8 = True
                self.todo_user = emp_id.approval_user.id
                # return self.action_send_email()
        
        if not emp_id:
            self.state = 'approved'

    def button_approved8(self):
        # emp_id = self.env['tbl_matrix_auth'].search(
        #     [('modul', '=', self.modul),('proc_group_id','=',self.proc_group_id.id),('company_id','=',self.company_id.id),('level', '=', '5')], limit=1)
        # if emp_id:
        if self.appr8.id != self.env.uid:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr8_dt = fields.Datetime.now()
        self.todo_user = False
        self.state = 'approved'
        for item in self.line_ids:
            if item.product_id:
                analytic_obj = self.env["crossovered.budget.lines"]
                # subpo_obj = self.env["tbl_budget_est_practical"]
                skrg = fields.Date.today()
                analitik = analytic_obj.search(
                    [("analytic_account_id", "=", item.analytic_account_id.id),
                     ("date_from", "<=", self.date_start), ("date_to", ">=", self.date_start)]
                )
                # if analitik:
                #     subpo_obj.create({
                #         'details': analitik.id,
                #         'tipe': 'PR',
                #         'date': self.date_start,
                #         'desc': self.name,
                #         'amount': item.estimated_cost,
                #     })
        # return self.action_send_email()

    def action_preview_reject(self):
        if self.requested_by.id != self.env.uid and self.state =='draft':
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        # if self.prepared_by.id != self.env.uid:
        #     raise UserError(
        #         _("Anda tidak berhak melakukan proses ini -> 1"))
        if self.env.uid not in (self.todo_user_ids.ids) and self.state =='to_approve_matrix':
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        
        if self.requested_by.id != self.env.uid and self.state =='approved':
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
            
        view = self.env.ref('purchase_request.purchase_request_wizard')
        # picking_type_id = self.picking_type_id or self.picking_id.picking_type_id
        return {
            'name': _('Reason for Rejection'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.request',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
        }

    def action_preview_cancel(self):
        view = self.env.ref('purchase_request.purchase_request_cancel_wizard')
        # picking_type_id = self.picking_type_id or self.picking_id.picking_type_id
        for rec in self:
            allowed = True
            # if rec.state == 'draft':
            #     if self.requested_by.id != self.env.uid:
            #         allowed = False
            # elif rec.state == 'to_request_approve':
            #     if self.prepared_by.id != self.env.uid:
            #         allowed = False
            if rec.state == 'to_recommend':
                if self.recommended_by.id != self.env.uid:
                    allowed = False
            elif rec.state == 'to_check':
                if self.checked_by.id != self.env.uid:
                    allowed = False
            elif rec.state == 'to_verify':
                if self.verified_by.id != self.env.uid:
                    allowed = False
            elif rec.state == 'to_approve':
                if self.assigned_to.id != self.env.uid:
                    allowed = False
            elif rec.state == 'to_approve1':
                if self.appr1.id != self.env.uid:
                    allowed = False
            elif rec.state == 'to_approve2':
                if self.appr2.id != self.env.uid:
                    allowed = False
            elif rec.state == 'to_approve3':
                if self.appr3.id != self.env.uid:
                    allowed = False
            elif rec.state == 'to_approve4':
                if self.appr4.id != self.env.uid:
                    allowed = False
            elif rec.state == 'approved':
                if self.assigned_to.id != self.env.uid:
                    allowed = False
            elif rec.state == 'to_request_approve':
                if self.prepared_by.id != self.env.uid:
                    allowed = False

            if allowed == False:
                raise UserError(
                    _("Anda tidak berhak melakukan proses ini"))

            if self.line_ids:
                for line in self.line_ids:
                    if line.purchase_lines:
                        for po_line in line.purchase_lines:
                            if po_line.state != 'cancel':
                                raise UserError(
                                    _("Active PO must be Cancelled before PR can be Cancelled"))

        return {
            'name': _('Reason for Cancel'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.request',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
        }

    def action_preview_done(self):
        view = self.env.ref('purchase_request.purchase_request_done_wizard')
        # picking_type_id = self.picking_type_id or self.picking_id.picking_type_id
        for rec in self:
            allowed = True
            if rec.prepared_by.id != rec.env.uid and rec.requested_by.id != rec.env.uid:
                allowed = False

            if allowed == False:
                raise UserError(
                    _("Anda tidak berhak melakukan proses ini"))

        return {
            'name': _('Reason for Done'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.request',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
        }

    def button_set_to_draft(self):
        return self.write({"state": "draft"})

    def button_rejected(self):
        self.mapped("line_ids").do_cancel()
        analytic_obj = self.env["crossovered.budget.lines"]
        # analytic_detail_obj = self.env["tbl_budget_est_practical"]
        # self.state = 'draft'
        # self.requested_by = False
        self.requested_dt = ""
        # self.prepared_by = False
        self.prepare_dt = ''
        self.recommended_dt = ''
        self.checked_dt = ''
        self.verify_dt = ''
        self.assign_to_dt = ''
        self.assign_dt = ''
        self.appr1_dt = ''
        self.appr2_dt = ''
        self.appr3_dt = ''
        self.appr4_dt = ''
        self.appr5_dt = ''
        self.todo_user_ids = False
        # self.

        for item in self.line_ids:
            if item.product_id:
                analytic_obj = self.env["crossovered.budget.lines"]
                # subpo_obj = self.env["tbl_budget_est_practical"]
                skrg = fields.Date.today()
                analitik = analytic_obj.search(
                    [("analytic_account_id", "=", item.analytic_account_id.id), ("date_from", "<=", self.date_start),
                     ("date_to", ">=", self.date_start)]
                )
                # if analitik:
                #     analitik_detail = analytic_detail_obj.search(
                #         [("details", "=", analitik.id), ("desc", "=", self.name)])
                #     if analitik_detail:
                #         analitik_detail.status = 'not used'

                #     subpo_obj.create({
                #     'details' : analitik.id,
                #     'tipe' : 'PR',
                #     'date' : self.date_start,
                #     'desc' : self.name,
                #     'amount' : item.estimated_cost,
                # })

        # if self.state in ('draft','to_request_approve'):
        #     return self.write({"state": "cancel"})
        self.state = 'rejected'
        # return self.write({"state": "rejected"})

    def button_cancel(self):
        # if self.prepared_by.id != self.env.uid and self.requested_by.id != self.env.uid:
        #         raise UserError(
        #              _("Anda tidak berhak melakukan proses ini"))
        self.button_rejected()
        return self.write({"state": "cancel"})

    def button_done(self):
        # if self.prepared_by.id != self.env.uid and self.requested_by.id != self.env.uid:
        #         raise UserError(
        #              _("Anda tidak berhak melakukan proses ini"))
        return self.write({"state": "done"})

    def check_auto_reject(self):
        """When all lines are cancelled the purchase request should be
        auto-rejected."""
        for pr in self:
            if not pr.line_ids.filtered(lambda l: l.cancelled is False):
                pr.write({"state": "draft"})

    def to_approve_allowed_check(self):
        for rec in self:
            if not rec.to_approve_allowed:
                raise UserError(
                    _(
                        "You can't request an approval for a purchase request "
                        "which is empty. (%s)"
                    )
                    % rec.name
                )

    def action_create_po(self):
        po_obj = self.env['purchase.order']
        po_data = {
            'partner_id': self.env.company.id,
            'proc_group_id': self.proc_group_id.id,
            # 'name': self.name,
            # 'product_qty': self.product_qty,
            # 'price_unit': self.product_id.price
        }
        po_id = po_obj.create(po_data)
        po_line_obj = self.env['purchase.order.line']
        po_line_ids = []
        for line in self.line_ids:
            po_line_data = {
                'order_id': po_id.id,
                'product_id': line.product_id.id,
                'name': line.name,
                'product_qty': line.product_qty,
                'price_unit': line.estimated_price_unit,
                'price_subtotal': line.estimated_cost
            }
            po_line_id = po_line_obj.create(po_line_data)
            po_line_ids.append(po_line_id)
        return {
            'name': _('RFQ Form'),
            'view_mode': 'form',
            'view_id': self.env.ref('purchase.purchase_order_form').id,
            'view_type': 'form',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': po_id.id,
        }

    def create_approval_matrix(self):
        obj_app = self.env['config.approval.matrix'].search([('modul','=',self.modul),('proc_group_id','=',self.proc_group_id.id),('company_id','=',self.company_id.id),('department_id','=',self.department_id.id),('tag_warehouse', 'in', self.picking_type_id.warehouse_id.id),('expected_amount', '<=', self.harga_total)],order="matrix_level_name asc")
        for item in obj_app:
            vals = {
                "purchase_request_id":self.id,
                "user_ids": [(6, 0, item.approval_user_ids.ids)],
                "matrix_level_id":item.matrix_level_id.id,
                "config_approval_matrix_id":item.id,
                "state":"Tobe Approved Mtrx "+ item.matrix_level_name,
                "name":"Tobe Approved Mtrx "+ item.matrix_level_name,
            }
            obj_create = self.env['approval.matrix'].create(vals)


class InheritApprovalMatrixPR(models.Model):
    _inherit = "approval.matrix"

    purchase_request_id = fields.Many2one('purchase.request','Purchase Request')

class InheritConfigApprovalMatrix(models.Model):
    _inherit = "config.approval.matrix"

    proc_group_id = fields.Many2one('tbl_proc_group','Procurement Category')

class InheritCashSdvanceho(models.Model):
    _inherit = "cash.advance.ho"

    purchase_request_id = fields.Many2one('purchase.request','Purchase Request')

class InheritCashSdvanceSite(models.Model):
    _inherit = "cash.advance.site"

    purchase_request_id = fields.Many2one('purchase.request','Purchase Request')

class Inheritsundrysundry(models.Model):
    _inherit = "sundry"

    purchase_request_id = fields.Many2one('purchase.request','Purchase Request')

class InheritNoi(models.Model):
    _inherit = "noi"

    purchase_request_id = fields.Many2one('purchase.request','Purchase Request')