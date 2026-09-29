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

class tbl_mnt_request(models.Model):
    _name = "tbl_mnt_request"
    # _order = "id desc"
    _rec_name = 'nomor'
    _order = 'tanggal desc'

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    tanggal = fields.Date('Tanggal', default=lambda self: fields.Date.today())
    nomor = fields.Char('Nomor', default='/', readonly=True)
    name = fields.Many2one('master_asset_maintenance','Nama Aset')
    prepare_by = fields.Many2one('res.users','Prepare By',default=lambda self: self.env.user, readonly=True)
    request_by = fields.Many2one('res.users','Request By',default=lambda self: self.env.user)
    divisi = fields.Char('Divisi',compute="compute_divisi", store=True)
    tipe_mt = fields.Selection([
        ('preventive','Preventive'),
        ('corrective','Corrective'),
        ],'Tipe MT')
    template_service = fields.Many2one('maintenance_master_service',string="Template Service")
    unit = fields.Many2one('product.template',string="Unit", related='name.product_asset', store=True)
    keluhan = fields.Text('Keluhan')
    kat_keluhan = fields.Many2one('tbl_mnt_katkeluhan','Kategori Keluhan')
    lokasi = fields.Many2one('tbl_aset_lokasi',string="Lokasi")
    status = fields.Selection([
        ('draft','Draft'),
        ('planning','Planning'),
        ('submit','Submit'),
        ('terima','WorkOrder'),
        ('on_progress','On Progress'),
        ('pending','Pending'),
        ('done','Done'),
        ],'Status', default='draft')

    # DETAIL
    tgl_submit = fields.Datetime('Tanggal Submit', readonly=True)
    tgl_terima = fields.Datetime('Tanggal Terima', readonly=True)
    tgl_mulai_kerja = fields.Datetime('Tanggal Mulai Pekerjaan', readonly=True)
    tgl_selesai_kerja = fields.Datetime('Tanggal Selesai Pekerjaan', readonly=True)
    mulai_pending = fields.Datetime('Mulai Pending', readonly=True)
    stop_pending = fields.Datetime('Stop Pending', readonly=True)
    alasan_pending = fields.Text('Alasan Pending')
    durasi = fields.Char('Durasi', readonly=True)

    detail_task = fields.One2many('tbl_mnt_task','details','Detail Task')
    detail_part = fields.One2many('tbl_mnt_request_part','details','Detail Task')
    details_asset = fields.Many2one('master_asset_maintenance',string="Detail Aset")

    @api.depends('request_by')
    def compute_divisi(self):
        for rec in self:
            if rec.request_by:
                div = self.env['hr.employee'].search([('user_id', '=', rec.request_by.id)]).department_id.name
                if div:
                    rec.divisi = div
                else:
                    rec.divisi = ''



    def action_submit(self):
        for rec in self:
            rec.status = 'submit'
            rec.tgl_submit = fields.Datetime.now()
            rec.nomor = self.env['ir.sequence'].next_by_code('mnt_request')
    def action_terima(self):
        for rec in self:
            rec.status = 'terima'
            rec.tgl_terima = fields.Datetime.now()
    def action_start(self):
        for rec in self:
            rec.status = 'on_progress'
            rec.tgl_mulai_kerja = fields.Datetime.now()
            rec.details_asset = rec.name.id
    def action_task(self):
        for rec in self:
            data3 = self.env['tbl_mnt_task'].create({
                                                'details': rec.id,
                                                'task': 'Task Name is .....',
                                                'result': ' Task Result id ....',
                                                'wo_id': rec.id,
                                    })
    def action_pending(self):
        for rec in self:
            rec.status = 'pending'
            rec.mulai_pending = fields.Datetime.now()
    def action_stop_pending(self):
        for rec in self:
            rec.stop_pending = fields.Datetime.now()
    def action_done(self):
        for rec in self:
            rec.status = 'done'


class tbl_mnt_request_part(models.Model):
    _name = "tbl_mnt_request_part"

    details = fields.Many2one('tbl_mnt_request',"Details")
    details_task = fields.Many2one('tbl_mnt_task',"Details Task")
    details_task2 = fields.Many2one('tbl_mnt_task',"Details Task Outsource")
    name = fields.Many2one('product.template',string="Name")
    qty = fields.Float("Qty", default=1)
    uom = fields.Many2one('uom.uom',string="Unit of Measure", related='name.uom_id')
    source = fields.Char("Source")
    ket = fields.Char("Keterangan")

    work_order_id = fields.Many2one('work.order', 'No WO', readonly=True)
    number = fields.Char('Part Number')
    reserve_qty = fields.Float('Reserve (Qty)')
    done_qty = fields.Float('Done (Qty)')


class tbl_mnt_katkeluhan(models.Model):
    _name = "tbl_mnt_katkeluhan"
    _rec_name = 'display_name'

    name = fields.Char(string="Name")
    parent = fields.Many2one('tbl_mnt_katkeluhan',string="Parent")
    display_name = fields.Char(string="Display_name",compute="compute_display_name", store=True)

    @api.depends('name','parent')
    def compute_display_name(self):
        for rec in self:
            if rec.name and not rec.parent:
                rec.display_name = rec.name
            elif rec.name and rec.parent:
                rec.display_name = rec.parent.name +'-'+rec.name
            else:
                rec.display_name = ''


