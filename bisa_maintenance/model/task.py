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

class tbl_mnt_task(models.Model):
    _name = "tbl_mnt_task"
    _order = 'name desc'
    # _order = "id desc"
    _rec_name = 'name'

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    name = fields.Char('Nomor', default='/', readonly=True)
    details = fields.Many2one('tbl_mnt_request','Nomor', readonly=True)
    task = fields.Char('Task Name')
    date_start = fields.Datetime('Start Date')
    date_end = fields.Datetime('End Date')
    employee = fields.Many2many('hr.employee',domain="[('department_id.name', 'like', 'PLANT')]")
    result = fields.Text('Result', default='Result')
    duration = fields.Float()

    state = fields.Selection([
        ('continue','Continue'),
        ('rfu', 'RFU'),
        ],'Status')
    detail_part = fields.One2many('tbl_mnt_request_part','details_task','Detail Task')
    detail_part2 = fields.One2many('tbl_mnt_request_part','details_task2','Detail Task')

    nomor_outsource = fields.Char('Nomor Outsource', default='/', readonly=True)
    wo_id = fields.Many2one('tbl_mnt_request','WO', readonly=True)
    tanggal = fields.Date('Tanggal', related='wo_id.tanggal', store=True)
    nama_aset = fields.Many2one('master_asset_maintenance','Nama Aset', related='wo_id.name', store=True)
    prepare_by = fields.Many2one('res.users','Prepare By', related='wo_id.prepare_by', store=True)
    request_by = fields.Many2one('res.users','Request By', related='wo_id.request_by', store=True)
    divisi = fields.Char('Divisi', related='wo_id.divisi', store=True)
    tipe_mt = fields.Selection([
        ('preventive','Preventive'),
        ('corrective','Corrective'),
        ],'Tipe MT', related='wo_id.tipe_mt', store=True)
    template_service = fields.Many2one('maintenance_master_service',string="Template Service", related='wo_id.template_service', store=True)
    unit = fields.Many2one('product.template',string="Unit", related='wo_id.unit', store=True)
    keluhan = fields.Text('Keluhan', related='wo_id.keluhan', store=True)
    kat_keluhan = fields.Many2one('tbl_mnt_katkeluhan','Kategori Keluhan', related='wo_id.kat_keluhan', store=True)
    lokasi = fields.Many2one('tbl_aset_lokasi',string="Lokasi", related='wo_id.lokasi', store=True)

    work_order_id = fields.Many2one('work.order', 'No WO', readonly=True)
    location = fields.Char(related='work_order_id.location_problem')
    shift = fields.Selection([
        ('day', 'Day'),
        ('night', 'Night')
    ])
    detail_task = fields.Many2many('detail.task')
    spv_id = fields.Many2one('hr.employee', 'Supervisor', domain="[('department_id.name', 'like', 'PLANT')]")
    maintenance_type = fields.Selection(selection=[
        ('corrective', 'Unschedule'),
        ('preventive', 'Schedule'),
        ('accident', 'Accident')
    ], related='work_order_id.maintenance_type')
    equipment_id = fields.Many2one(related='work_order_id.equipment_id', string='Unit Code')
    # working_time = fields.Char(compute='_compute_working_time', store=1)
    working_time = fields.Float()
    mechanic = fields.Many2many('hr.employee', related='work_order_id.mechanic')

    # @api.depends('date_end')
    # def _compute_working_time(self):
    #     for rec in self:
    #         rec.working_time = 0
    #         if rec.date_end and rec.date_start:
    #             rec.working_time = rec.date_end - rec.date_start


    def action_submit(self):
        for rec in self:
            rec.state = 'submit'
            rec.name = self.env['ir.sequence'].next_by_code('mnt_task')

    def action_start(self):
        for rec in self:
            rec.state = 'on_progress'
            rec.date_start = fields.Datetime.now()

    def action_matrial(self):
        for rec in self:
            a=1

    def action_done(self):
        for rec in self:
            rec.state = 'done'
            rec.nomor_outsource = self.env['ir.sequence'].next_by_code('mnt_outsource')
            rec.date_end = fields.Datetime.now()
            for wo in rec.detail_part:
                wo.details = rec.wo_id.id
            for wo in rec.detail_part2:
                wo.details = rec.wo_id.id
                wo.source = 'TASK : '+rec.name+' Outsource : '+ rec.nomor_outsource

    def action_get_matrial(self):
        for rec in self:
            if not rec.template_service:
                raise UserError('Tidak Ada Template Service')
            else:
                for part in rec.template_service.sparepart_line_ids:
                    data3 = self.env['tbl_mnt_request_part'].create({
                                                'details_task': rec.id,
                                                'name': part.produk.id,
                                                'qty': part.quantity,
                                    })


