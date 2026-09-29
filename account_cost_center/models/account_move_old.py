# Copyright 2015-2020 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, date_utils, email_split, email_re, float_is_zero
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.osv import expression

from datetime import date, timedelta
from collections import defaultdict
from itertools import zip_longest
from hashlib import sha256
from json import dumps
from datetime import datetime, timedelta
import ast
import json
import re
import warnings

MAX_HASH_VERSION = 2

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    # name = fields.Char(string='Number', copy=False, compute='_compute_name', readonly=False, store=True, index=True, tracking=True)
    # state = fields.Selection(selection_add=[ 
    #     ("to_verify", "Tobe Verify"), 
    #     ("approved1", "Tobe Appr1"),
    #     ("approved2", "Tobe Appr2"),
    #     ("approved3", "Tobe Appr3"),
    #     ("posted",)])
    state_new = fields.Selection(selection=[
            ('draft', 'Draft'),
            ("to_verify", "Tobe Verify"), 
            ("approved1", "Tobe Appr1"),
            ("approved2", "Tobe Appr2"),
            ("approved3", "Tobe Appr3"),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ], string='Status New', required=True, readonly=False, copy=False, tracking=True,
        default='draft', compute='_compute_state_new', store=True)

    cost_center_id = fields.Many2one(
        "account.cost.center",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Default Cost Center",
    )

    prepared_by = fields.Many2one(
        comodel_name="res.users",
        string="Prepared By",
        required=True,
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

    appr1 = fields.Many2one(
        comodel_name="res.users",
        string="Approved By",
        copy=False,
        track_visibility="onchange",
    )
    appr1_dt = fields.Datetime('Appr1 Datetime')
    appr2 = fields.Many2one(
        comodel_name="res.users",
        string="Approved By",
        copy=False,
        track_visibility="onchange",
    )
    appr2_dt = fields.Datetime('Appr2 Datetime')
    appr3 = fields.Many2one(
        comodel_name="res.users",
        string='Approved By',
        copy=False,
        track_visibility="onchange",
    )
    appr3_dt = fields.Datetime('Appr3 Datetime')

    alasan_cancel = fields.Text(
        string="Reason for Cancel",
        track_visibility="onchange"
    )
    # def action_samakan(self):
    #     domain = [
    #                 ('state', 'in', ('posted','cancel'))
    #             ]
    #     # cari = self.env['account.move'].search(domain)
    #     cari = self.env['account.move'].search([])
    #     if cari:
    #         for rec in cari:
    #             rec.state_new = rec.state
    @api.depends('state')
    def _compute_state_new(self):
        for rec in self:
            if rec.state:
                rec.state_new = rec.state

    # @api.depends('posted_before', 'state_new', 'state', 'journal_id', 'date')
    # def _compute_name(self):
    #     def journal_key(move):
    #         return (move.journal_id, move.journal_id.refund_sequence and move.move_type)

    #     def date_key(move):
    #         return (move.date.year, move.date.month)

    #     grouped = defaultdict(  # key: journal_id, move_type
    #         lambda: defaultdict(  # key: first adjacent (date.year, date.month)
    #             lambda: {
    #                 'records': self.env['account.move'],
    #                 'format': False,
    #                 'format_values': False,
    #                 'reset': False
    #             }
    #         )
    #     )
    #     self = self.sorted(lambda m: (m.date, m.ref or '', m.id))

    #     # Group the moves by journal and month
    #     for move in self:
    #         move_has_name = move.name and move.name != '/'
    #         if move_has_name or move.state != 'posted':
    #             try:
    #                 if not move.posted_before:
    #                     # The move was never posted, so the name can potentially be changed.
    #                     move._constrains_date_sequence()
    #                 # Either the move was posted before, or the name already matches the date (or no name or date).
    #                 # We can skip recalculating the name when either
    #                 # - the move already has a name, or
    #                 # - the move has no name, but is in a period with other moves (so name should be `/`), or
    #                 # - the move has (temporarily) no date set
    #                 if (
    #                     move_has_name and move.posted_before
    #                     or not move_has_name and move._get_last_sequence(lock=False)
    #                     or not move.date
    #                 ):
    #                     continue
    #             except ValidationError:
    #                 # The move was never posted and the current name doesn't match the date. We should calculate the
    #                 # name later on, unless ...
    #                 if move._get_last_sequence(lock=False):
    #                     # ... we are in a period already containing moves: reset the name to `/` (draft)
    #                     move.name = '/'
    #                     continue
    #         group = grouped[journal_key(move)][date_key(move)]
    #         if not group['records']:
    #             # Compute all the values needed to sequence this whole group
    #             move._set_next_sequence()
    #             group['format'], group['format_values'] = move._get_sequence_format_param(move.name)
    #             group['reset'] = move._deduce_sequence_number_reset(move.name)
    #         group['records'] += move

    #     # Fusion the groups depending on the sequence reset and the format used because `seq` is
    #     # the same counter for multiple groups that might be spread in multiple months.
    #     final_batches = []
    #     for journal_group in grouped.values():
    #         journal_group_changed = True
    #         for date_group in journal_group.values():
    #             if (
    #                 journal_group_changed
    #                 or final_batches[-1]['format'] != date_group['format']
    #                 or dict(final_batches[-1]['format_values'], seq=0) != dict(date_group['format_values'], seq=0)
    #             ):
    #                 final_batches += [date_group]
    #                 journal_group_changed = False
    #             elif date_group['reset'] == 'never':
    #                 final_batches[-1]['records'] += date_group['records']
    #             elif (
    #                 date_group['reset'] == 'year'
    #                 and final_batches[-1]['records'][0].date.year == date_group['records'][0].date.year
    #             ):
    #                 final_batches[-1]['records'] += date_group['records']
    #             else:
    #                 final_batches += [date_group]

    #     # Give the name based on previously computed values
    #     for batch in final_batches:
    #         for move in batch['records']:
    #             move.name = batch['format'].format(**batch['format_values'])
    #             batch['format_values']['seq'] += 1
    #         batch['records']._compute_split_sequence()

    #     # self.filtered(lambda m: not m.name).name = '/'

    def button_to_approve_request(self):
        # for move in self:
        #     move_has_name = move.name and move.name != '/'
        #     raise UserError(
        #          _(move.posted_before) )
        if self.prepared_by.id != self.env.uid:
            raise UserError(
                 _("Anda tidak berhak melakukan proses ini") )
        if self.name == '/' and self.date:
            tanggal = self.date
            tanggal_awal_bulan = tanggal.replace(day=1)
            bulan_berikutnya = tanggal.month + 1 if tanggal.month != 12 else 1
            tahun_berikutnya = tanggal.year + 1 if tanggal.month == 12 else tanggal.year
            tanggal_akhir_bulan = tanggal.replace(year=tahun_berikutnya, month=bulan_berikutnya, day=1) - timedelta(days=1)
            query = """
                    SELECT name
                    FROM account_move
                    WHERE date <= %s AND date >= %s AND move_type = %s AND company_id = %s and name != %s
                    ORDER BY name DESC
                    LIMIT 1
                    """

            values = (
                        tanggal_akhir_bulan, tanggal_awal_bulan, 'in_invoice', self.company_id.id, '/'
                    )

            self.env.cr.execute(query, values)
            result = self.env.cr.fetchone()
            no_terakhir = None
            if result:
                no_terakhir = result[0]

            if no_terakhir:
                parts = no_terakhir.split('/')
                last_number = int(parts[-1])
                next_number = last_number + 1
                prefix = '/'.join(parts[:-1])
            else:
                next_number = 1
                prefix = f"{self.journal_id.code}/{tanggal.year}/{tanggal.month:02d}"

            self.name = f"{prefix}/{next_number:04d}"

        self.prepare_dt = fields.Datetime.now()
        self.state_new = 'to_verify'

    def button_verify(self):
        if self.verified_by.id != self.env.uid:
            raise UserError(
                 _("Anda tidak berhak melakukan proses ini"))
        self.verify_dt = fields.Datetime.now()
        if self.appr1:
            self.state_new = 'approved1'
        else:
            return self.action_post()

    def button_approved1(self):
        if self.appr1.id != self.env.uid:
                raise UserError(
                     _("Anda tidak berhak melakukan proses ini"))
        self.appr1_dt = fields.Datetime.now()
        if self.appr2:
            self.state_new = 'approved2'
        else:
            return self.action_post()
        
    def button_approved2(self):
        if self.appr2.id != self.env.uid:
                raise UserError(
                     _("Anda tidak berhak melakukan proses ini"))
        self.appr2_dt = fields.Datetime.now()
        if self.appr3:
            self.state_new = 'approved3'
        else:
            return self.action_post()

    def button_approved3(self):
        if self.appr3.id != self.env.uid:
                raise UserError(
                     _("Anda tidak berhak melakukan proses ini"))
        self.appr3_dt = fields.Datetime.now()
        return self.action_post()

    def action_preview_cancel(self):
        view = self.env.ref('account_cost_center.account_move_cancel_wizard')
        for rec in self:
            allowed = True
            if rec.state_new == 'draft':
                if self.prepared_by.id != self.env.uid:
                    allowed = False
            elif rec.state_new == 'to_verify':
                if self.verified_by.id != self.env.uid:
                    allowed = False
            elif rec.state_new == 'approved1':
                if self.appr1.id != self.env.uid:
                    allowed = False
            elif rec.state_new == 'approved2':
                if self.appr2.id != self.env.uid:
                    allowed = False
            elif rec.state_new == 'approved3':
                if self.appr3.id != self.env.uid:
                    allowed = False
            if allowed == False:
                raise UserError(
                        _("Anda tidak berhak melakukan proses ini"))
        return {
            'name': _('Reason for Cancel'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
        }

    def action_print(self):

        if self.company_id and self.company_id.name == 'PT RENCANA MULIA BARATAMA':
            if not self.appr1 and not self.appr2 and not self.appr3:
                # raise UserError(_("appr1"))
                return self.env.ref('account_cost_center.print_vb_rmb_a1').report_action(self)
            elif self.appr1 and not self.appr2 and not self.appr3:
                # raise UserError(_("appr2"))
                return self.env.ref('account_cost_center.print_vb_rmb_a2').report_action(self)
            elif self.appr1 and self.appr2 and not self.appr3:
                # raise UserError(_("appr3"))
                return self.env.ref('account_cost_center.print_vb_rmb_a3').report_action(self)
            elif self.appr1 and self.appr2 and self.appr3:
                # raise UserError(_("appr4"))
                return self.env.ref('account_cost_center.print_vb_rmb_a4').report_action(self)
            
        if self.company_id and self.company_id.name == 'PT INDO BARA PRATAMA':
            if not self.appr1 and not self.appr2 and not self.appr3:
                # raise UserError(_("appr1"))
                return self.env.ref('account_cost_center.print_vb_ibp_a1').report_action(self)
            elif self.appr1 and not self.appr2 and not self.appr3:
                # raise UserError(_("appr2"))
                return self.env.ref('account_cost_center.print_vb_ibp_a2').report_action(self)
            elif self.appr1 and self.appr2 and not self.appr3:
                # raise UserError(_("appr3"))
                return self.env.ref('account_cost_center.print_vb_ibp_a3').report_action(self)
            elif self.appr1 and self.appr2 and self.appr3:
                # raise UserError(_("appr4"))
                return self.env.ref('account_cost_center.print_vb_ibp_a4').report_action(self)
            