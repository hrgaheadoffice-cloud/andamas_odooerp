# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import xlsxwriter
import base64
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp

class tbl_report_uangmuka(models.Model):
    _name = 'tbl_report_uangmuka'

    name = fields.Char('Name',default=' Aging Advance')
    tgl_awal = fields.Date('Tanggal Acuan', required=True, default=fields.Date.today())
    data = fields.Binary(string='File', readonly=True)
    detail = fields.One2many('tbl_report_uangmuka_detail','details', string='Detail')

    
    def act_get(self):
        detail_obj = self.env['tbl_report_uangmuka_detail']
        
        if self.detail:
            self.detail.unlink()

        dur=0
        dur_r=0
        age30=0
        age60=0
        age90=0
        age120=0
        age121=0
        self.env.cr.execute('Select name, date, employee_id, saldo From \
                            tbl_msi_acc_settlement\
                            where state in %s', (('submit2','appr2','post'),))
        for row in self.env.cr.fetchall():
                saldo=0
                dur = self.tgl_awal - row[1]
                dur_r = int(dur.days)
                #raise UserError(_('jam_kerja= %s dan %s ') % (dur,dur_r ))
                saldo = row[3]
                if dur_r < 31:
                   age30 = saldo
                   data_line2 = detail_obj.create({
                           'details': self.id,
                           'name': row[0],
                           'date': row[1],
                           'employee_id': row[2],
                           'saldo': saldo,
                           'age30': age30,
                           'age60': 0,
                           'age90': 0,
                           'age120': 0,
                           'age121': 0,
                  })

                else:
                   if dur_r > 30 and dur_r < 61:
                      age60 = saldo
                      data_line2 = detail_obj.create({
                           'details': self.id,
                           'name': row[0],
                           'date': row[1],
                           'employee_id': row[2],
                           'saldo': saldo,
                           'age30': 0,
                           'age60': age60,
                           'age90': 0,
                           'age120': 0,
                           'age121': 0,
                      })


                   else:
                      if dur_r > 60 and dur_r < 91:
                         age90 = saldo
                         data_line2 = detail_obj.create({
                           'details': self.id,
                           'name': row[0],
                           'date': row[1],
                           'employee_id': row[2],
                           'saldo': saldo,
                           'age30': 0,
                           'age60': 0,
                           'age90': age90,
                           'age120': 0,
                           'age121': 0,
                         })

                      else:
                         if dur_r > 90 and dur_r < 121:
                            age120 = saldo
                            data_line2 = detail_obj.create({
                                 'details': self.id,
                                 'name': row[0],
                                 'date': row[1],
                                 'employee_id': row[2],
                                 'saldo': saldo,
                                 'age30': 0,
                                 'age60': 0,
                                 'age90': 0,
                                 'age120': age120,
                                 'age121': 0,
                            })

                         else:
                            if dur_r > 120:
                               age121 = saldo
                               data_line2 = detail_obj.create({
                                 'details': self.id,
                                 'name': row[0],
                                 'date': row[1],
                                 'employee_id': row[2],
                                 'saldo': saldo,
                                 'age30': 0,
                                 'age60': 0,
                                 'age90': 0,
                                 'age120': 0,
                                 'age121': age121,
                               })


    def unlink(self):
        for rec in self:
            if self.detail:
                self.detail.unlink()
            if self.detail2:
                self.detail2.unlink()
        return super(tbl_report_sales_ete, self).unlink()


    def print_xls_report(self):
        xls_filename = 'Aging Advance Per '+str(self.tgl_awal)+'.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/' + xls_filename)

        header_merge_format = workbook.add_format({'bold':True, 'align':'center', 'valign':'vcenter', \
                                            'font_size':10, 'bg_color':'#D3D3D3', 'border':1})

        header_data_format = workbook.add_format({'align':'center', 'valign':'vcenter', \
                                                   'font_size':10, 'border':1})
        product_header_format = workbook.add_format({'valign':'vcenter', 'font_size':10, 'border':1})
        rows = 5
        worksheet = workbook.add_worksheet(self.name)
        worksheet.write(0, 0, 'Aging Advance', header_merge_format)
        worksheet.write(1, 0, 'Per :'+ str(self.tgl_awal), header_merge_format)
        for line in self.detail:
            worksheet.write(4, 0, 'Number', header_merge_format)
            worksheet.write(4, 1, 'Date', header_merge_format)
            worksheet.write(4, 2, 'Employee', header_merge_format)
            worksheet.write(4, 3, 'Value', header_merge_format)
            worksheet.write(4, 4, '0-30', header_merge_format)
            worksheet.write(4, 5, '31-60', header_merge_format)
            worksheet.write(4, 6, '62-90', header_merge_format)
            worksheet.write(4, 7, '91-120', header_merge_format)
            worksheet.write(4, 8, '121-..', header_merge_format)
 
            worksheet.write(rows, 0, line.name, header_data_format)
            worksheet.write(rows, 1, line.date, header_data_format)
            worksheet.write(rows, 2, str(line.employee_id.name), header_data_format)
            worksheet.write(rows, 3, str(line.saldo), header_data_format)
            worksheet.write(rows, 4, str(line.age30), header_data_format)
            worksheet.write(rows, 5, str(line.age60), header_data_format)
            worksheet.write(rows, 6, str(line.age90), header_data_format)
            worksheet.write(rows, 7, str(line.age120), header_data_format)
            worksheet.write(rows, 8, str(line.age121), header_data_format)
            rows += 1
        workbook.close()
        self.write({
            # 'state': 'get',
            'data': base64.b64encode(open('/tmp/' + xls_filename, 'rb').read()),
            # 'name': xls_filename
        })

class tbl_report_uangmuka_detail(models.Model):
    _name = 'tbl_report_uangmuka_detail'
    _order = 'name'

    details = fields.Many2one('tbl_report_sales_ete', string='Detail')

    name = fields.Char('Nomor',default='New', readonly=True)
    date = fields.Date('Date', default=fields.Date.today) 
    employee_id = fields.Many2one('hr.employee','Employee')
    saldo = fields.Float(string='Nominal')
    age30 = fields.Integer(string='0-30')
    age60 = fields.Integer(string='31-60')
    age90 = fields.Integer(string='61-90')
    age120 = fields.Integer(string='91-120')
    age121 = fields.Integer(string='121- ')
