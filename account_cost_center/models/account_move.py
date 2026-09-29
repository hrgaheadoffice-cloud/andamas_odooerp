# Copyright 2015-2020 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from email.policy import default
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    # def init(self):
    #     super().init()
    #     self.env.cr.execute("""
    #         CREATE INDEX IF NOT EXISTS account_move_to_check_idx
    #         ON account_move(journal_id) WHERE to_check = true;
    #         CREATE INDEX IF NOT EXISTS account_move_payment_idx
    #         ON account_move(journal_id, state, payment_state, move_type, date);
    #     """)

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    # state = fields.Selection(selection_add=[ 
    #     ("po_draft", "PO Draft")])
    # state = fields.Selection(selection=[
    #         ('draft', 'Draft'),
    #         ('posted', 'Posted'),
    #         ('cancel', 'Cancelled'),
    #         ('po_draft', '-')
    #     ], string='Status', required=True, readonly=True, copy=False, tracking=True,
    #     default='draft')
    # state = fields.Selection(selection_add=[ 
    #     ("to_verify", "Tobe Verify"), 
    #     ("approved1", "Tobe Appr1"),
    #     ("approved2", "Tobe Appr2"),
    #     ("approved3", "Tobe Appr3"),
    #     ("posted",)])
    state_new = fields.Selection(selection=[
            ('pre', 'Pre'),
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
            ('approve_requested', 'Approve Requested'),
            ('admin_approved', 'Approved'),
            ('tax_approved', 'Tax Approved'),
        ], string='Status New', required=True, readonly=False, copy=False, tracking=True,
        default='pre', compute="_compute_state_new", store=True)

    cost_center_id = fields.Many2one(
        "account.cost.center",
        readonly=False,
        help="Default Cost Center",
    )

    prepared_by = fields.Many2one(
        comodel_name="res.users",
        string="Prepared By",
        required=False,
        copy=False,
        track_visibility="onchange",
        default=_get_default_requested_by,
        index=True,
    )
    prepare_dt = fields.Datetime('Prepare Datetime')
    verified_by = fields.Many2one(
        comodel_name="res.users",
        string="Verified By",
        track_visibility="onchange")
    verify_dt = fields.Datetime('Verify Datetime') 
    checked_by = fields.Many2one(
        comodel_name="res.users",
        string="Checked By",
        copy=False,
        track_visibility="onchange",
    )
    checked_dt = fields.Datetime('Checked Datetime')

    appr1 = fields.Many2one(
        comodel_name="res.users",
        string="Approved 1",
        copy=False,
        track_visibility="onchange",
    )
    appr1_dt = fields.Datetime('Appr1 Datetime')
    appr2 = fields.Many2one(
        comodel_name="res.users",
        string="Approved 2",
        copy=False,
        track_visibility="onchange",
    )
    appr2_dt = fields.Datetime('Appr2 Datetime')
    appr3 = fields.Many2one(
        comodel_name="res.users",
        string='Approved 3',
        copy=False,
        track_visibility="onchange",
    )
    appr3_dt = fields.Datetime('Appr3 Datetime')

    alasan_cancel = fields.Text(
        string="Reason for Cancel",
        track_visibility="onchange"
    )
    
    # invoice_date_new = fields.Date('Invoice Date')
    agreement = fields.Char('Agreement')
    other = fields.Char('Other')
    invoice = fields.Char('Invoice')
    faktur_pajak = fields.Char('Faktur Pajak')
    ba = fields.Char('BA')

    is_ho = fields.Char('Is HO', compute="_compute_cost_center_id", store=True)
    is_samarinda = fields.Char('Is SAMARINDA', compute="_compute_cost_center_id", store=True)
    is_isp = fields.Char('Is ISP JETTY BUKIT JERING', compute="_compute_cost_center_id", store=True)
    is_site = fields.Char('Is SITE', compute="_compute_cost_center_id", store=True)
    is_jetty = fields.Char('Is JETTY LONG MAHLI', compute="_compute_cost_center_id", store=True)
    is_other = fields.Char('Is OTHER', compute="_compute_cost_center_id", store=True)

    verified1_by = fields.Many2one(comodel_name="res.users",string="Verified 1 By",track_visibility="onchange")
    verified2_by = fields.Many2one(comodel_name="res.users",string="Verified 2 By",track_visibility="onchange")
    verified3_by = fields.Many2one(comodel_name="res.users",string="Verified 3 By",track_visibility="onchange")
    verified4_by = fields.Many2one(comodel_name="res.users",string="Verified 4 By",track_visibility="onchange")
    verified5_by = fields.Many2one(comodel_name="res.users",string="Verified 5 By",track_visibility="onchange")
    verified6_by = fields.Many2one(comodel_name="res.users",string="Verified 6 By",track_visibility="onchange")

    verified1 = fields.Boolean(string="Verified 1",track_visibility="onchange")
    verified2 = fields.Boolean(string="Verified 2",track_visibility="onchange")
    verified3 = fields.Boolean(string="Verified 3",track_visibility="onchange")
    verified4 = fields.Boolean(string="Verified 4",track_visibility="onchange")
    verified5 = fields.Boolean(string="Verified 5",track_visibility="onchange")
    verified6 = fields.Boolean(string="Verified 6",track_visibility="onchange")

    pre_num = fields.Char('Pre Num',readonly=True, default="New")

    def action_submit(self):
        self = self.with_company(self.company_id.id)
        if self.pre_num == 'New':
            seq_date = None
            date = fields.Datetime.now
            seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(self.date))
            self.pre_num = self.env['ir.sequence'].next_by_code('pre_vendor_bill', sequence_date=seq_date) or _('New')
        for rec in self:
            rec.state_new = 'draft'

    @api.onchange('verified1')
    def _onchange_verified1(self):
        # for rec in self:
        #   if self.verified1_by and self.verified1 == True:
          if self.verified1:
            if self.verified1_by.id != self.env.uid:
                raise UserError(
                     _("Anda tidak berhak melakukan proses ini"))

    @api.onchange('verified2')
    def _onchange_verified2(self):
        # for rec in self:
        #   if self.verified2_by:
          if self.verified2:
            if self.verified2_by.id != self.env.uid:
                raise UserError(
                     _("Anda tidak berhak melakukan proses ini"))

    @api.onchange('verified3')
    def _onchange_verified3(self):
        # for rec in self:
        #   if self.verified3_by:
          if self.verified3:
            if self.verified3_by.id != self.env.uid:
                raise UserError(
                     _("Anda tidak berhak melakukan proses ini"))

    @api.onchange('verified4')
    def _onchange_verified4(self):
        # for rec in self:
        #   if self.verified4_by:
          if self.verified4:
            if self.verified4_by.id != self.env.uid:
                raise UserError(
                     _("Anda tidak berhak melakukan proses ini"))

    @api.onchange('verified5')
    def _onchange_verified5(self):
        # for rec in self:
        #   if self.verified5_by:
          if self.verified5:
            if self.verified5_by.id != self.env.uid:
                raise UserError(
                     _("Anda tidak berhak melakukan proses ini"))

    @api.onchange('verified6')
    def _onchange_verified6(self):
        # for rec in self:
        #   if self.verified6_by:
          if self.verified6:
            if self.verified6_by.id != self.env.uid:
                raise UserError(
                     _("Anda tidak berhak melakukan proses ini"))

    @api.depends('state')
    def _compute_state_new(self):
        for rec in self:
            if rec.state and rec.state != 'draft':
                rec.state_new = rec.state

    @api.depends('cost_center_id')
    def _compute_cost_center_id(self):
        for rec in self:
            rec.is_ho = ''
            rec.is_samarinda = ''
            rec.is_isp = ''
            rec.is_site = ''
            rec.is_jetty = ''
            rec.is_other = ''
            if rec.cost_center_id:
                if rec.cost_center_id.code == 'HO':
                    rec.is_ho = "\u2713"
                if rec.cost_center_id.code == 'SMRD':
                    rec.is_samarinda = "\u2713"
                if rec.cost_center_id.code == 'ISP JBJ':
                    rec.is_isp = "\u2713"
                if rec.cost_center_id.code == 'SITE':
                    rec.is_site = "\u2713"
                if rec.cost_center_id.code == 'JLM':
                    rec.is_jetty = "\u2713"
                if rec.cost_center_id.code == 'OTH':
                    rec.is_other = "\u2713"

    def button_samakan(self):
        cari = self.env["account.move"].sudo().search([('move_type', '=', 'in_invoice'),('state', 'in', ('draft','posted','cancel'))])
        if cari:
            for rec in cari:
                rec.state_new = rec.state

    def button_draft(self):
        # Tambahkan kode yang Anda inginkan di sini sebelum pemanggilan fungsi asli
        result = super(AccountMove, self).button_draft()
        self.write({'state_new': 'pre'})
        # Tambahkan kode yang Anda inginkan di sini setelah pemanggilan fungsi asli
        return result
    # def button_verify(self):
    #     if self.verified_by.id != self.env.uid:
    #         raise UserError(
    #              _("Anda tidak berhak melakukan proses ini"))
    #     self.verify_dt = fields.Datetime.now()
    #     if self.appr1:
    #         self.state_new = 'approved1'
    #     else:
    #         return self.action_post()

    # def button_approved1(self):
    #     if self.appr1.id != self.env.uid:
    #             raise UserError(
    #                  _("Anda tidak berhak melakukan proses ini"))
    #     self.appr1_dt = fields.Datetime.now()
    #     if self.appr2:
    #         self.state_new = 'approved2'
    #     else:
    #         return self.action_post()
        
    # def button_approved2(self):
    #     if self.appr2.id != self.env.uid:
    #             raise UserError(
    #                  _("Anda tidak berhak melakukan proses ini"))
    #     self.appr2_dt = fields.Datetime.now()
    #     if self.appr3:
    #         self.state_new = 'approved3'
    #     else:
    #         return self.action_post()

    # def button_approved3(self):
    #     if self.appr3.id != self.env.uid:
    #             raise UserError(
    #                  _("Anda tidak berhak melakukan proses ini"))
    #     self.appr3_dt = fields.Datetime.now()
    #     return self.action_post()

    # def action_preview_cancel(self):
    #     view = self.env.ref('account_cost_center.account_move_cancel_wizard')
    #     for rec in self:
    #         allowed = True
    #         if rec.state_new == 'draft':
    #             if self.prepared_by.id != self.env.uid:
    #                 allowed = False
    #         elif rec.state_new == 'to_verify':
    #             if self.verified_by.id != self.env.uid:
    #                 allowed = False
    #         elif rec.state_new == 'approved1':
    #             if self.appr1.id != self.env.uid:
    #                 allowed = False
    #         elif rec.state_new == 'approved2':
    #             if self.appr2.id != self.env.uid:
    #                 allowed = False
    #         elif rec.state_new == 'approved3':
    #             if self.appr3.id != self.env.uid:
    #                 allowed = False
    #         if allowed == False:
    #             raise UserError(
    #                     _("Anda tidak berhak melakukan proses ini"))
    #     return {
    #         'name': _('Reason for Cancel'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'account.move',
    #         'views': [(view.id, 'form')],
    #         'view_id': view.id,
    #         'target': 'new',
    #         'res_id': self.id,
    #     }



    def action_print(self):

        self._compute_cost_center_id()
        if self.company_id and self.company_id.name == 'PT RENCANA MULIA BARATAMA':
            # if not self.checked_by and not self.verified_by:
            #     if not self.appr1 and not self.appr2 and not self.appr3:
            #         # raise UserError(_("appr1"))
            #         return self.env.ref('account_cost_center.print_vb_rmb_prepared').report_action(self)
            #     elif self.appr1 and not self.appr2 and not self.appr3:
            #         # raise UserError(_("appr2"))
            #         return self.env.ref('account_cost_center.print_vb_rmb_prepared_a1').report_action(self)
            #     elif self.appr1 and self.appr2 and not self.appr3:
            #         # raise UserError(_("appr3"))
            #         return self.env.ref('account_cost_center.print_vb_rmb_prepared_a2').report_action(self)
            #     elif self.appr1 and self.appr2 and self.appr3:
            #         # raise UserError(_("appr4"))
            #         return self.env.ref('account_cost_center.print_vb_rmb_prepared_a3').report_action(self)
                
            # elif self.checked_by and not self.verified_by:
            #     if not self.appr1 and not self.appr2 and not self.appr3:
            #         # raise UserError(_("appr1"))
            #         return self.env.ref('account_cost_center.print_vb_rmb_prepared_checked').report_action(self)
            #     elif self.appr1 and not self.appr2 and not self.appr3:
            #         # raise UserError(_("appr2"))
            #         return self.env.ref('account_cost_center.print_vb_rmb_prepared_checked_a1').report_action(self)
            #     elif self.appr1 and self.appr2 and not self.appr3:
            #         # raise UserError(_("appr3"))
            #         return self.env.ref('account_cost_center.print_vb_rmb_prepared_checked_a2').report_action(self)
            #     elif self.appr1 and self.appr2 and self.appr3:
            #         # raise UserError(_("appr4"))
            #         return self.env.ref('account_cost_center.print_vb_rmb_prepared_checked_a3').report_action(self)
                
            # elif not self.checked_by and self.verified_by:
            #     if not self.appr1 and not self.appr2 and not self.appr3:
            #         # raise UserError(_("appr1"))
            #         return self.env.ref('account_cost_center.print_vb_rmb_prepared_verified').report_action(self)
            #     elif self.appr1 and not self.appr2 and not self.appr3:
            #         # raise UserError(_("appr2"))
            #         return self.env.ref('account_cost_center.print_vb_rmb_prepared_verified_a1').report_action(self)
            #     elif self.appr1 and self.appr2 and not self.appr3:
            #         # raise UserError(_("appr3"))
            #         return self.env.ref('account_cost_center.print_vb_rmb_prepared_verified_a2').report_action(self)
            #     elif self.appr1 and self.appr2 and self.appr3:
            #         # raise UserError(_("appr4"))
            #         return self.env.ref('account_cost_center.print_vb_rmb_prepared_verified_a3').report_action(self)
                
            # else:
            #     if not self.appr1 and not self.appr2 and not self.appr3:
            #         # raise UserError(_("appr1"))
            #         return self.env.ref('account_cost_center.print_vb_rmb_prepared_checked_verified').report_action(self)
            #     elif self.appr1 and not self.appr2 and not self.appr3:
            #         # raise UserError(_("appr2"))
            #         return self.env.ref('account_cost_center.print_vb_rmb_prepared_checked_verified_a1').report_action(self)
            #     elif self.appr1 and self.appr2 and not self.appr3:
            #         # raise UserError(_("appr3"))
            #         return self.env.ref('account_cost_center.print_vb_rmb_prepared_checked_verified_a2').report_action(self)
            #     elif self.appr1 and self.appr2 and self.appr3:
            #         # raise UserError(_("appr4"))
                    return self.env.ref('account_cost_center.print_vb_rmb_prepared_checked_verified_a3').report_action(self)
            
        if self.company_id and self.company_id.name == 'PT INDO BARA PRATAMA':
            # if not self.checked_by and not self.verified_by:
            #     if not self.appr1 and not self.appr2 and not self.appr3:
            #         # raise UserError(_("appr1"))
            #         return self.env.ref('account_cost_center.print_vb_ibp_prepared').report_action(self)
            #     elif self.appr1 and not self.appr2 and not self.appr3:
            #         # raise UserError(_("appr2"))
            #         return self.env.ref('account_cost_center.print_vb_ibp_prepared_a1').report_action(self)
            #     elif self.appr1 and self.appr2 and not self.appr3:
            #         # raise UserError(_("appr3"))
            #         return self.env.ref('account_cost_center.print_vb_ibp_prepared_a2').report_action(self)
            #     elif self.appr1 and self.appr2 and self.appr3:
            #         # raise UserError(_("appr4"))
            #         return self.env.ref('account_cost_center.print_vb_ibp_prepared_a3').report_action(self)
                
            # elif self.checked_by and not self.verified_by:
            #     if not self.appr1 and not self.appr2 and not self.appr3:
            #         # raise UserError(_("appr1"))
            #         return self.env.ref('account_cost_center.print_vb_ibp_prepared_checked').report_action(self)
            #     elif self.appr1 and not self.appr2 and not self.appr3:
            #         # raise UserError(_("appr2"))
            #         return self.env.ref('account_cost_center.print_vb_ibp_prepared_checked_a1').report_action(self)
            #     elif self.appr1 and self.appr2 and not self.appr3:
            #         # raise UserError(_("appr3"))
            #         return self.env.ref('account_cost_center.print_vb_ibp_prepared_checked_a2').report_action(self)
            #     elif self.appr1 and self.appr2 and self.appr3:
            #         # raise UserError(_("appr4"))
            #         return self.env.ref('account_cost_center.print_vb_ibp_prepared_checked_a3').report_action(self)
                
            # elif not self.checked_by and self.verified_by:
            #     if not self.appr1 and not self.appr2 and not self.appr3:
            #         # raise UserError(_("appr1"))
            #         return self.env.ref('account_cost_center.print_vb_ibp_prepared_verified').report_action(self)
            #     elif self.appr1 and not self.appr2 and not self.appr3:
            #         # raise UserError(_("appr2"))
            #         return self.env.ref('account_cost_center.print_vb_ibp_prepared_verified_a1').report_action(self)
            #     elif self.appr1 and self.appr2 and not self.appr3:
            #         # raise UserError(_("appr3"))
            #         return self.env.ref('account_cost_center.print_vb_ibp_prepared_verified_a2').report_action(self)
            #     elif self.appr1 and self.appr2 and self.appr3:
            #         # raise UserError(_("appr4"))
            #         return self.env.ref('account_cost_center.print_vb_ibp_prepared_verified_a3').report_action(self)
                
            # else:
            #     if not self.appr1 and not self.appr2 and not self.appr3:
            #         # raise UserError(_("appr1"))
            #         return self.env.ref('account_cost_center.print_vb_ibp_prepared_checked_verified').report_action(self)
            #     elif self.appr1 and not self.appr2 and not self.appr3:
            #         # raise UserError(_("appr2"))
            #         return self.env.ref('account_cost_center.print_vb_ibp_prepared_checked_verified_a1').report_action(self)
            #     elif self.appr1 and self.appr2 and not self.appr3:
            #         # raise UserError(_("appr3"))
            #         return self.env.ref('account_cost_center.print_vb_ibp_prepared_checked_verified_a2').report_action(self)
            #     elif self.appr1 and self.appr2 and self.appr3:
            #         # raise UserError(_("appr4"))
                    return self.env.ref('account_cost_center.print_vb_ibp_prepared_checked_verified_a3').report_action(self)
            