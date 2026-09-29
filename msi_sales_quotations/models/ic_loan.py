# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models

import math


class tbl_msi_ic_loan(models.Model):
    _name = 'tbl_msi_ic_loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
        ('out', 'Pay Out'),
        ('inprogress', 'In Progress'),
        ('done', 'Done'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')


    name = fields.Char('Nomor', readonly=True)
    keterangan = fields.Char('Keterangan', track_visibility='onchange')
    date = fields.Date('Date', default=fields.Date.today)
    partner_id = fields.Many2one("res.partner", string="Perusahaan", required=True, readonly=True, states={'draft': [('readonly', False)]})
    amount = fields.Float(string="Nilai", required=True, readonly=True, states={'draft': [('readonly', False)]})

    detail = fields.One2many('tbl_msi_ic_loan_detail','details', 'Settle')
    account = fields.Many2one('account.account', string="Settlement Account", domain=[('deprecated', '=', False)], copy=False, required=True,)
    payment_id = fields.Many2one('account.payment', 'Transfer Out Id', readonly=True)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('seq_msi_ic_loan')

        result = super(tbl_msi_ic_loan, self).create(vals)
        return result

    def action_submit(self):
        self.state = 'approve'


    def action_approve(self):
        self.state = 'out'


    def action_pay_out(self):
        detail_obj = self.env['account.payment']
        data_line2 = detail_obj.create({
                 'payment_type': 'outbound',
                 'partner_type': 'supplier',
                 'partner_id': self.partner_id.id,
                 'amount': self.amount,
                 'journal_id': 11,
                 'payment_method_id': 2,
                 'payment_date': self.date,
                 'communication': 'InterCompany Loan : '+str(self.name) + ' Nama : '+str(self.partner_id.name),
                 'x_studio_field_cqQTC': 'InterCompany Loan : '+str(self.name) + ' Nama : '+str(self.partner_id.name),
                 'is_advance': True,
                 'adv_account_id': self.account.id,
        })
        self.state = 'inprogress'
        self.payment_id = data_line2



    def action_done(self):
        self.state = 'done'






class tbl_msi_ic_loan_detail(models.Model):
    _name = 'tbl_msi_ic_loan_detail'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ], string='Status', readonly=True, default='draft')


    keterangan = fields.Char('Keterangan', track_visibility='onchange')
    date = fields.Date('Date', default=fields.Date.today)
    amount = fields.Float(string="Nilai")
    payment_id = fields.Many2one('account.payment', 'Payment Id', readonly=True)

    details = fields.Many2one('tbl_msi_ic_loan', 'Settle')

    def action_settle(self):
        detail_obj = self.env['account.payment']
        data_line2 = detail_obj.create({
                 'payment_type': 'inbound',
                 'partner_type': 'supplier',
                 'partner_id': self.details.partner_id.id,
                 'amount': self.amount,
                 'journal_id': 11,
                 'payment_method_id': 2,
                 'payment_date': self.date,
                 'communication': 'Settlement InterCompany Loan : '+str(self.details.name) + ' Nama : '+str(self.details.partner_id.name),
                 'x_studio_field_cqQTC': 'Settlement InterCompany Loan : '+str(self.details.name) + ' Nama : '+str(self.details.partner_id.name),
                 'is_advance': True,
                 'adv_account_id': self.details.account.id,
        })
        self.state = 'done'
        self.payment_id = data_line2


