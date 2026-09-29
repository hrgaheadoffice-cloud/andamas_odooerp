# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models

import math


class tbl_msi_bonds(models.Model):
    _name = 'tbl_msi_bonds'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
        ('out', 'Pay Out'),
        ('inprogress', 'Inprogress'),
        ('done', 'Done'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    jenis = fields.Selection([
        ('Bid_Bonds', 'Bind Bonds'),
        ('Performace_Bonds', 'Performace Bonds'),
        ('Maintenance_Bonds', 'Maintenance Bonds'),
        ('Deposito', 'Deposito'),
        ('Lainnya', 'Lainnya'),
        ], string='Jenis', copy=False, index=True, default='lainnya', readonly=True, states={'draft': [('readonly', False)]})

    name = fields.Char('Nomor', readonly=True)
    keterangan = fields.Char('Keterangan', track_visibility='onchange')
    date = fields.Date('Date', default=fields.Date.today, readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one("res.partner", string="Customer", required=True, readonly=True, states={'draft': [('readonly', False)]})
    sso = fields.Many2one('sale.order','Nomor SSO', required=True, readonly=True, states={'draft': [('readonly', False)]})
    journal_asal_id = fields.Many2one('account.journal', string='Rekening Asal', required=True, readonly=True, states={'draft': [('readonly', False)]})
    journal_tujuan_id = fields.Many2one('account.journal', string='Rekening Tujuan', required=True, readonly=True, states={'draft': [('readonly', False)]})
    amount = fields.Float(string="Nilai", required=True, readonly=True, states={'draft': [('readonly', False)]})
    lama = fields.Float(string="Jangka Waktu (Bulan)", required=True, readonly=True, states={'draft': [('readonly', False)]})
    due_date = fields.Date(string="Jatuh Tempo", required=True, readonly=True, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one("res.currency", string="Mata Uang",  required=True, readonly=True, states={'draft': [('readonly', False)]})
    payment_out_id = fields.Many2one('account.payment', 'Transfer Out Id', readonly=True)
    payment_in_id = fields.Many2one('account.payment', 'Transfer Out Id', readonly=True)


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('seq_bonds')

        result = super(tbl_msi_bonds, self).create(vals)
        return result


    def action_submit(self):
        self.state = 'approve'


    def action_approve(self):
        self.state = 'out'


    def action_out(self):
        detail_obj = self.env['account.payment']
        data_line2 = detail_obj.create({
                 'payment_type': 'transfer',
                 'amount': self.amount,
                 'journal_id': self.journal_asal_id.id,
                 'destination_journal_id': self.journal_tujuan_id.id,
                 'payment_method_id': 2,
                 'payment_date': self.date,
                 'communication':'Trf out ' + str(self.jenis) + ' No : '+str(self.name) + ' Nama : '+str(self.partner_id.name) + ' No SSO : ' + str(self.sso.name),
#                 'desc':'Trf out ' + str(self.jenis) + ' No : '+str(self.name) + ' Nama : '+str(self.partner_id.name) + ' No SSO : ' + str(self.sso.name),
                 'x_studio_field_cqQTC':'Trf out ' + str(self.jenis) + ' No : '+str(self.name) + ' Nama : '+str(self.partner_id.name) + ' No SSO : ' + str(self.sso.name),
 
        })
        self.state = 'inprogress'
        self.payment_out_id = data_line2

    def action_in(self):
        detail_obj = self.env['account.payment']
        data_line3 = detail_obj.create({
                 'payment_type': 'transfer',
                 'amount': self.amount,
                 'destination_journal_id': self.journal_asal_id.id,
                 'journal_id': self.journal_tujuan_id.id,
                 'payment_method_id': 2,
                 'payment_date': self.date,
                 'communication': 'Trf In ' +str(self.jenis) + ' No : '+str(self.name) + ' Nama : '+str(self.partner_id.name) + ' No SSO : ' + str(self.sso.name),
                 'x_studio_field_cqQTC': 'Trf In ' +str(self.jenis) + ' No : '+str(self.name) + ' Nama : '+str(self.partner_id.name) + ' No SSO : ' + str(self.sso.name),

        })
        self.state = 'done'
        self.payment_in_id = data_line3







