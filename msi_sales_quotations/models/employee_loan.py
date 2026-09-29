# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import math


class tbl_msi_employee_loan(models.Model):
    _name = 'tbl_msi_employee_loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
        ('out', 'Pay Out'),
        ('progress', 'In Progress'),
        ('done', 'Done'),
        ], string='Status', copy=False, index=True, track_visibility='onchange', default='draft')


    name = fields.Char('Nomor', readonly=True)
    keterangan = fields.Char('Keterangan', track_visibility='onchange')
    date = fields.Date('Date', default=fields.Date.today, readonly=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    amount = fields.Float(string="Nilai", required=True)
    lama = fields.Float(string="Jangka Waktu (Bulan)", required=True)
    cicilan = fields.Float(string="Nilai Cicilan", required=True)
    jenis = fields.Selection([
        ('cicilan', 'Cicilan'),
        ('durasi', 'Jangka Waktu'),
        ], string='Jenis',  copy=False, index=True, track_visibility='onchange', default='durasi')
    guna = fields.Char('Kegunaan Pinjaman', track_visibility='onchange')
    start_date = fields.Date(string="Tgl Mulai", required=True)
    detail = fields.One2many('tbl_msi_employee_loan_detail','details', 'Detail')
    account = fields.Many2one('account.account', string="Loan Account", domain=[('deprecated', '=', False)], copy=False, required=True)
    account_settle = fields.Many2one('account.account', string="Settlement Account", domain=[('deprecated', '=', False)], copy=False, required=True)
    journal_id = fields.Many2one('account.journal', string='Journal Settlement', required=True)
    amount1 = fields.Float(string="Nilai Pinjaman", compute='_compute_amount1', store=True,)
    total_bayar = fields.Float(string="Total Bayar", compute='_compute_total_bayar', store=True,)
    total_amount_jad = fields.Float(string="Total Jadual Bayar", compute='_compute_total_bayar', store=True,)
    total_kurang = fields.Float(string="Total Kurang", compute='_compute_total_kurang', store=True,)
    currency_id = fields.Many2one('res.currency', string='Currency')
    lama_cicil = fields.Float(string="Waktu (Bulan)", readonly=True)
    payment_id = fields.Many2one('account.payment', 'Payment_id', readonly=True)

    
    @api.depends('detail')
    def _compute_total_bayar(self):
        for rec in self:
            for tot in rec.detail:
                rec.total_bayar += tot.amount_bayar
                rec.total_amount_jad += tot.amount

    
    @api.depends('amount')
    def _compute_amount1(self):
        for rec in self:
            rec.amount1 = rec.amount

    
    @api.depends('amount', 'total_bayar' )
    def _compute_total_kurang(self):
        for rec in self:
            rec.total_kurang = rec.amount - rec.total_bayar


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('seq_msi_emp_loan')
        result = super(tbl_msi_employee_loan, self).create(vals)
        return result

    def action_submit(self):
        self.state = 'approve'

    def action_approve(self):
        self.state = 'out'

    def action_out(self):
        detail_obj = self.env['account.payment']
        data_line2 = detail_obj.create({
                 'payment_type': 'outbound',
                 'partner_type': 'supplier',
                 'partner_id': self.employee_id.address_home_id.id,
                 'amount': self.amount,
                 'journal_id': 11,
                 'payment_method_id': 2,
                 'payment_date': self.date,
                 'communication': 'Employee Loan : '+str(self.name) + ' Nama : '+str(self.employee_id.name),
                 'x_studio_field_cqQTC': 'Employee Loan : '+str(self.name) + ' Nama : '+str(self.employee_id.name),
                 'is_advance': True,
                 'adv_account_id': self.account.id,
        })
        self.state = 'progress'
        self.payment_id = data_line2

    def action_lunas(self):
        self.state = 'done'

    def done(self):
        self.state = 'done'


    def act_hitung(self):
        order_obj = self.env['tbl_msi_employee_loan_detail']
        if self.detail:
           self.env.cr.execute('delete from tbl_msi_employee_loan_detail where details = %s' ,(self.id,))

        if self.amount <= 0:
           raise UserError(_("Nilai Harus Diisi nilai positif"))
        
        angs=0
        if self.jenis == 'durasi':
           if self.amount == 0 or self.amount == 0:
               raise ValidationError(_("Jangka waktu atau nilai pinjaman tidak boleh 0"))
           angs=self.amount/self.lama
           loop_on=self.lama
           angs_ke=1
           count=0
           while count < loop_on:
                 jad_bayar = self.start_date+ relativedelta(months=count)
                 self.lama_cicil = angs_ke
                 data5 = order_obj.create({
                    'details': self.id,
                    'angs_ke': angs_ke,
                    'amount': angs,
                    'jadual_bayar': jad_bayar,
                    'state': 'draft',
                 })
                 count += 1
                 angs_ke += 1


        if self.jenis == 'cicilan':
           if self.cicilan == 0 or self.amount == 0:
               raise ValidationError(_("Cicilan atau nilai pinjaman tidak boleh 0"))
           angs=math.floor(self.amount/self.cicilan)   
           loop_on=angs
           angs_ke=1
           count=0
           while count < loop_on:
                 jad_bayar = self.start_date+ relativedelta(months=count)
                 data5 = order_obj.create({
                    'details': self.id,
                    'angs_ke': angs_ke,
                    'amount': self.cicilan,
                    'jadual_bayar': jad_bayar,
                    'state': 'draft',
                 })
                 count += 1
                 angs_ke += 1
           self.lama_cicil = angs
           selisih = self.amount - self.total_amount_jad
           if selisih > 0:
              data6 = order_obj.create({
                    'details': self.id,
                    'angs_ke': angs+1,
                    'amount': self.amount - self.total_amount_jad,
                    'jadual_bayar': self.start_date+ relativedelta(months=(angs)),
                    'state': 'draft',
              })
              self.lama_cicil = angs+1






class tbl_msi_employee_loan_detail(models.Model):
    _name = 'tbl_msi_employee_loan_detail'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ], string='Status', readonly=True, default='draft')
    angs_ke = fields.Integer('Angs Ke', readonly=True)
    keterangan = fields.Char('Keterangan', track_visibility='onchange')
    jadual_bayar = fields.Date('Jadual Bayar', readonly=True)
    amount = fields.Float(string="Nilai Jadual", readonly=True)
    aktual_bayar = fields.Date('Tgl Bayar', readonly=True)
    amount_bayar = fields.Float(string="Nilai Bayar")
    payment_id = fields.Many2one('account.payment', 'Payment_id', readonly=True)
    move_id = fields.Many2one('account.move', 'Move Id', readonly=True)

    cara_bayar = fields.Selection([
        ('gaji', 'Salary'),
        ('bank', 'Cash/Bank'),
        ], string='Cara Bayar', default='gaji')

    details = fields.Many2one('tbl_msi_employee_loan', 'Detail')

    def action_settle(self):
        order_obj = self.env['tbl_msi_employee_loan_detail']
        self.state = 'done'
        if self.cara_bayar == 'gaji':
              if self.amount_bayar == 0:
                 raise ValidationError(_("Nilai Pembayaran tidak boleh 0"))

              self.aktual_bayar = fields.Date.today()
              account_move_obj = self.env['account.move']
              account_move_line_obj = self.env['account.move.line']
              data_accr_bonus = account_move_obj.create({
                    'journal_id': self.details.journal_id.id,
                    'date': fields.Date.today(),
                    'ref': 'Settlement Employee Loan : '+str(self.details.name) + ' Nama : '+str(self.details.employee_id.name),

              })
              data3 = account_move_line_obj.with_context(check_move_validity=False).create({
                    'name': 'Settlement Employee Loan',
                    'partner_id': self.details.employee_id.address_home_id.id,
                    'date': fields.Date.today(),
                    'journal_id': self.details.journal_id.id,
                    'account_id': self.details.account.id,
                    'move_id': data_accr_bonus.id,
                    'currency_id': self.details.currency_id.id,
                    'amount_currency': 0,
                    'date_maturity': fields.Date.today(),
                    'credit': self.amount_bayar,

              })

              data31 = account_move_line_obj.with_context(check_move_validity=False).create({
                    'name': 'Settlement Employee Loan : '+str(self.details.name) + ' Nama : '+str(self.details.employee_id.name),
                    'partner_id': self.details.employee_id.address_home_id.id,
                    'date': fields.Date.today(),
                    'journal_id': self.details.journal_id.id,
                    'account_id': self.details.account_settle.id,
                    'move_id': data_accr_bonus.id,
                    'currency_id': self.details.currency_id.id,
                    'amount_currency': 0,
                    'date_maturity': fields.Date.today(),
                    'debit': self.amount_bayar,
              })
              self.move_id = data_accr_bonus


        if self.cara_bayar == 'bank':
           if self.amount_bayar == 0:
                 raise ValidationError(_("Nilai Pembayaran tidak boleh 0"))
           self.aktual_bayar = fields.Date.today()
           detail_obj = self.env['account.payment']
           data_line2 = detail_obj.create({
                 'payment_type': 'inbound',
                 'partner_type': 'supplier',
                 'partner_id': self.details.employee_id.address_home_id.id,
                 'amount': self.amount_bayar,
                 'journal_id': 11,
                 'payment_method_id': 2,
                 'payment_date': fields.Date.today(),
                 'communication': 'Settlement Employee Loan : '+str(self.details.name) + ' Nama : '+str(self.details.employee_id.name),
                 'x_studio_field_cqQTC': 'Settlement Employee Loan : '+str(self.details.name) + ' Nama : '+str(self.details.employee_id.name),
                 'is_advance': True,
                 'adv_account_id': self.details.account.id,
           })
           self.payment_id = data_line2
        total_bayar=0   
        if self.amount == self.amount_bayar:
           self.state = 'done'

        else:
           self.state = 'done'

           cari = self.env['tbl_msi_employee_loan_detail'].search([('details','=',self.details.id),('angs_ke','>',self.angs_ke)])
           if cari:
              #raise ValidationError(_(cari))
              cari.unlink()

           cari_bayar = self.env['tbl_msi_employee_loan_detail'].search([('details','=',self.details.id),('angs_ke','<=',self.angs_ke)])
           if cari_bayar:
              for cari_bayar_r in cari_bayar:
                  total_bayar += cari_bayar_r.amount_bayar
                  
              
           if (self.details.amount1 - total_bayar) != 0 :
              angs=math.floor((self.details.amount1 - total_bayar)/(self.details.lama_cicil-int(self.angs_ke)))   
              loop_on=self.details.lama_cicil-int(self.angs_ke)
              angs_ke=(self.details.lama_cicil-int(self.angs_ke))+1
              count=0
              jad_bayar=self.jadual_bayar + relativedelta(months=1)
              while count < loop_on:
                 jad_bayar = jad_bayar + relativedelta(months=count)
                 data5 = order_obj.create({
                    'details': self.details.id,
                    'angs_ke': angs_ke,
                    'amount': angs,
                    'jadual_bayar': jad_bayar,
                    'state': 'draft',
                 })
                 count += 1
                 angs_ke += 1

                 self.lama_cicil = angs_ke
              selisih = self.details.amount - self.details.total_amount_jad
              if selisih > 0:
                data6 = order_obj.create({
                    'details': self.details.id,
                    'angs_ke': self.details.lama_cicil+1,
                    'amount': self.details.amount - self.details.total_amount_jad,
                    'jadual_bayar': self.details.start_date+ relativedelta(months=(int(self.details.lama_cicil+1))),
                    'state': 'draft',
                })
                self.details.lama_cicil = self.details.lama_cicil+1
