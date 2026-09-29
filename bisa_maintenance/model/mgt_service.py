# coding: utf-8
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import datetime
from datetime import date
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
import calendar

import base64  # file encode
from urllib.request import urlopen

class tbl_maintenance_aset(models.Model):
    _name = "tbl_maintenance_aset"
    # _order = "id desc" 


    nomor = fields.Char('Nomor', default='/')
    name = fields.Char('Nama Aset')
    aset_id = fields.Many2one('account.asset', 'Aset Akuntansi')
    product_id = fields.Many2one('product.product', 'Aset GA', index=True)
    deskripsi = fields.Text('Detail', required=True)
    vendor_id = fields.Many2one('res.partner', 'Vendor')
    tanggal_beli = fields.Date('Tanggal Beli', required=True, index=True)
    lokasi_update = fields.Many2one('tbl_aset_lokasi','Lokasi terkini', readony=True)
    pic_update = fields.Many2one('hr.employee','PIC terkini', readony=True)
    tanggal_serah_terima_update = fields.Date('Tanggal ST', index=True, help='Tanggal Serah Terima terkini', readony=True)
    detail_lokasi = fields.One2many('tbl_aset_detail_lokasi','details','Detail Lokasi')
    status = fields.Selection([
    	('draft', 'New'),
    	('running', 'Running'),
    	('repair', 'in Repair'),
    	('broken', 'Broken'),
    	], string='Status Aset',  copy=False, index=True, tracking=True, default='draft', readony=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('get', 'Set Nomor'),
        ('done', 'Done'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')

    @api.depends('aset_id','product_id')
    def compute_nama(self):
        for rec in self:
            if rec.product_id and rec.aset_id:
                raise UserError(_("Aset Akuntansi dan Aset GA harus dipilih salah satu"))
            else:
                if rec.aset_id:
                    rec.name = str(rec.aset_id.name)
                else:
                    if rec.product_id:
                        rec.name = str(rec.product_id.name)
                    else:
        # else:
                        rec.name='/'



    # @api.depends('detail_lokasi','detail_lokasi.state')
    # def compute_status(self):
    #     for rec in self:
    #         if rec.detail_lokasi:
    #             status = self.env["tbl_aset_detail_lokasi"].search([("details","=",self.id),("state","=","done")], limit=1, order = 'tanggal_serah_terima desc')
    #             if status:
    #                 rec.status = status.status
    #                 rec.pic_update = status.pic.id
    #                 rec.tanggal_serah_terima_update = status.tanggal_serah_terima
    #                 rec.lokasi_update = status.lokasi.id
    #             else:
    #                 rec.status = ''
    #                 rec.pic_update = ''
    #                 rec.tanggal_serah_terima_update = ''
    #                 rec.lokasi_update = ''
    #         else:
    #                 rec.status = ''
    #                 rec.pic_update = ''
    #                 rec.tanggal_serah_terima_update = ''
    #                 rec.lokasi_update = ''




    def action_nomor(self):
        for rec in self:
            if rec.nomor == '/':
                rec.nomor = self.env['ir.sequence'].next_by_code('ga_aset')


            rec.state = 'get'

    def action_confirm(self):
        for rec in self:
            rec.state = 'done'


class tbl_aset_detail_lokasi(models.Model):
    _name = "tbl_aset_detail_lokasi"

    details = fields.Many2one('tbl_maintenance_aset','Detail Aset')
    lokasi = fields.Many2one('tbl_aset_lokasi','Lokasi')
    pic = fields.Many2one('hr.employee','PIC')
    tanggal_serah_terima = fields.Date('Tanggal Serah Terima', required=True)
    status = fields.Selection([
    		('draft', 'New'),
    		('running', 'Running'),
    		('repair', 'in Repair'),
    		('broken', 'Broken'),
    		], string='Status Aset',  copy=False, index=True, tracking=True, default='draft')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ], string='Status',  copy=False, index=True, tracking=True, default='draft')

    def action_submit(self):
        for rec in self:
            rec.state = 'done'
            rec.details.status = rec.status
            rec.details.pic_update = rec.pic.id
            rec.details.tanggal_serah_terima_update = rec.tanggal_serah_terima
            rec.details.lokasi_update = rec.lokasi.id


class tbl_aset_lokasi(models.Model):
    _name = "tbl_aset_lokasi"

    name = fields.Char('Lokasi Lengkap',compute='compute_lokasi')
    lokasi = fields.Char('Lokasi')
    parent = fields.Many2one('tbl_aset_lokasi','Lokasi Parent')
    detail_alamat = fields.Char('Alamat Lengkap')



    @api.depends('lokasi','parent')
    def compute_lokasi(self):
        for rec in self:
            if rec.parent:
                rec.name = str(rec.parent.lokasi) + ' - ' + str(rec.lokasi)
            else:
                rec.name = str(rec.lokasi)







