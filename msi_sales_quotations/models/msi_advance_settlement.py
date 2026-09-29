# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo import api, fields, models
import datetime
from dateutil.relativedelta import relativedelta
import math
import logging
_logger = logging.getLogger(__name__)


class tbl_msi_acc_settlement(models.Model):
    _name = 'tbl_msi_acc_settlement'
    _order = 'name desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([
        ('draft', 'Draft'),
        ('appr', 'Approve Advanced'),
        ('reg_payment', 'Register Payment'),
        ('submit2', 'Submit Settlement'),
        ('appr2', 'Approve Settlement'),
        ('post', 'Post Journal Settlement'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    name = fields.Char('Nomor',default='New', readonly=True)
    date = fields.Date('Date', default=fields.Date.today) 
    employee_id = fields.Many2one('hr.employee','Employee')
    saldo = fields.Float(compute='_compute_total', string='Perkiraan Biaya', readonly=True, store=True)
    settlement = fields.Float(compute='_compute_settlement', string='Total Settlement', readonly=True, store=True)
    selisih = fields.Float(compute='_compute_selisih', string='Selisih', readonly=True, store=True)
    property_account_uang_muka = fields.Many2one('account.account', string="Advanced Account", required=True)
    date_settlement = fields.Date('Date Settlement') 
    property_account_intransit = fields.Many2one('account.account', string="Intransit Account Payable")
    property_account_intransit_recv = fields.Many2one('account.account', string="Intransit Account Receivable")
    journal_id = fields.Many2one('account.journal', string='Journal Advanced')

    detail_advanced_id = fields.One2many('tbl_msi_acc_settlement_advanced','detail_advanced_ids','Detail Advanced')
    detail_settlement_id = fields.One2many('tbl_msi_acc_settlement_settlement','detail_settlement_ids','Detail Settlement')
    payment_out_id = fields.Many2one('account.payment', 'Payment', readonly=True)
    payment_inout_id = fields.Many2one('account.payment', 'Settle Lebih/Kurang', readonly=True)

    @api.depends('detail_advanced_id')
    def _compute_total(self):
        debit=0
        credit=0
        for wo in self:
            for harga in wo.detail_advanced_id:        
               debit += harga.amount
            wo.saldo = debit


    @api.depends('detail_settlement_id')
    def _compute_settlement(self):
        debit=0
        credit=0
        for wo in self:
            for harga in wo.detail_settlement_id:        
               debit += harga.amount
            wo.settlement = debit



    @api.depends('saldo','settlement')
    def _compute_selisih(self):
        debit=0
        credit=0
        for wo in self:
            for harga in wo.detail_settlement_id:        
               debit = wo.saldo - wo.settlement

            wo.selisih = debit


    @api.model
    def create(self, vals):

        cari = self.env['tbl_msi_acc_settlement'].search([('employee_id','=',vals.get('employee_id',)),('state','not in',('done','cancel'))])
        for sett in cari:
          today = fields.Date.today()
          batas = sett.date+relativedelta(days=int(30))
          if today > batas:
           raise ValidationError(_('Tidak Dapat di simpan\nMasih ada Advance yang belum done'))
          # else:
        if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('acc_settlement') or _('New')
          #   raise UserError(_('%s dan %s' % (today, batas)))

        result = super(tbl_msi_acc_settlement, self).create(vals)
        return result




    def action_submit(self):
#      if self.selisih < 0:
#         raise UserError(_('Nilai Selisih harus > 0'))
      self.state = 'appr'

    def action_approve_adv(self):
#      if self.selisih < 0:
#         raise UserError(_('Nilai Selisih harus > 0'))
      self.state = 'reg_payment'



    def action_approve1(self):

      account_move_obj = self.env['account.move']
      account_move_line_obj = self.env['account.move.line']


      if not self.property_account_uang_muka:
         raise UserError(_('Account Advanced belum di set'))


      if not self.journal_id:
         raise UserError(_('Advanced Journal belum di set'))


      detail_obj = self.env['account.payment']
      data_line2 = detail_obj.create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.employee_id.address_home_id.id,
            'amount': self.saldo,
            'journal_id': self.journal_id.id,
            'payment_method_id': 2,
            'communication': self.env['ir.sequence'].next_by_code('seq_cc'),
            'communication1': 'Advanced # ' + str(self.name) + ' ' +str(self.employee_id.name),
            # 'x_studio_field_cqQTC': 'Advanced # ' + str(self.name) + ' ' +str(self.employee_id.name),
            'is_advance': True,
            'adv_account_id': self.property_account_uang_muka.id,
        })

      self.state = 'submit2'
      self.payment_out_id = data_line2



    def action_submit2(self):
        if self.settlement == 0:
            raise UserError(_('Isi Settlemen dahulu'))
        # Tambah validasi cek budget 211101
        for data in self.detail_settlement_id:
            budget_avail = 0
            budget = data.env['crossovered.budget.lines'].search(
                [
                    ('analytic_account_id', '=', data.analytic_id.id),
                    ('date_from', '<=', self.date_settlement),
                    ('date_to', '>=', self.date_settlement)
                ])
            if budget:
                for line in budget:
                    nilai = 0
                    # Dikurangi diubah menjadi ditambah.
                    nilai = line.planned_amount + line.practical_amount
                    budget_avail += nilai
            if not self.date_settlement:
                raise UserError(_("Mohon untuk mengisi Date Settlement."))
            if budget_avail == 0:
                raise UserError(_("Tidak ada Budget untuk Budget Code %s.") % (data.analytic_id.code))
            if data.amount > budget_avail:
                raise UserError(_("Amount Settlement %s Melebihi Budget.") % (data.name))
        self.state = 'appr2'

    def action_approve_set(self):
      if self.settlement == 0:
         raise UserError(_('Isi Settlemen dahulu'))
      self.state = 'post'

    def action_approve2(self):

      account_move_obj = self.env['account.move']
      account_move_line_obj = self.env['account.move.line']

      if not self.property_account_uang_muka:
         raise UserError(_('Account Advanced belum di set'))

      if not self.journal_id:
         raise UserError(_('Advanced Journal belum di set'))

      if not self.date_settlement:
         raise UserError(_('Tanggal Settlement belum di set'))



      data2 = account_move_obj.create({
                    'journal_id': self.journal_id.id,
                    'date': self.date_settlement,
                    'ref': 'Settlement # ' + str(self.name),

      })

      data4 = account_move_line_obj.with_context(check_move_validity=False).create({
                    'name': self.name,
                    'date': self.date_settlement,
                    'journal_id': self.journal_id.id,
                    'account_id': self.property_account_uang_muka.id,
                    'move_id': data2.id,
                    'date_maturity': fields.Date.today(),
                    'credit': self.settlement,

      })

          

      for line in self.detail_settlement_id:
          data3 = account_move_line_obj.with_context(check_move_validity=False).create({
                    'name': str(self.name) + ' ' + str(line.name),
                    'date': self.date_settlement,
                    'journal_id': self.journal_id.id,
                    'account_id': line.property_account_expense.id,
                    'move_id': data2.id,
                    'date_maturity': fields.Date.today(),
                    'debit': line.amount,
          })

      data2.post()



      if self.selisih < 0:

         detail_obj = self.env['account.payment']
         data_line2 = detail_obj.create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.employee_id.address_home_id.id,
            'amount': self.selisih*-1,
            'journal_id': self.journal_id.id,
            'payment_method_id': 2,
            'communication': self.env['ir.sequence'].next_by_code('seq_cc'),
            'communication1': 'Settlement Lebih Advanced # ' + str(self.name) + ' ' +str(self.employee_id.name),
            # 'x_studio_field_cqQTC':'Settlement Lebih Advanced # ' + str(self.name) + ' ' +str(self.employee_id.name),
            'is_advance': True,
            'adv_account_id': self.property_account_uang_muka.id,
         })
         self.payment_inout_id = data_line2

      if self.selisih > 0:

         detail_obj = self.env['account.payment']
         data_line2 = detail_obj.create({
            'payment_type': 'inbound',
            'partner_type': 'supplier',
            'partner_id': self.employee_id.address_home_id.id,
            'amount': self.selisih,
            'journal_id': self.journal_id.id,
            'payment_method_id': 2,
            'communication': self.env['ir.sequence'].next_by_code('seq_cc'),
            'communication1': 'Settlement Advanced # ' + str(self.name) + ' ' +str(self.employee_id.name),
            # 'x_studio_field_cqQTC':'Settlement Advanced # ' + str(self.name) + ' ' +str(self.employee_id.name),
            'is_advance': True,
            'adv_account_id': self.property_account_uang_muka.id,
         })

         self.payment_inout_id = data_line2

      self.state = 'done'


class tbl_msi_acc_settlement_advanced(models.Model):
    _name = 'tbl_msi_acc_settlement_advanced'

    detail_advanced_ids = fields.Many2one('tbl_msi_acc_settlement','Detail')
    name = fields.Char('Label')
    amount = fields.Float('Amount') 


class tbl_msi_acc_settlement_settlement(models.Model):
    _name = 'tbl_msi_acc_settlement_settlement'

    detail_settlement_ids = fields.Many2one('tbl_msi_acc_settlement','Detail')
    name = fields.Char('Label')
    amount = fields.Float('Amount') 
    property_account_expense = fields.Many2one('account.account', string="Expense Account", required=True)
    analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')




# class msi2_invoice(models.Model):
#     _inherit = 'account.invoice'
#
#     nama_bg = fields.Char('BG')
