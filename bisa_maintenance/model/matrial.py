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

class tbl_mnt_matrial(models.Model):
    _name = "tbl_mnt_matrial"
    _order = 'id desc'


    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    name = fields.Char('Nomor', default='/', readonly=True)
    detail = fields.One2many('tbl_mnt_matrial_line','details','Detail Part')
    task = fields.Many2one('tbl_mnt_task','Task Name', readonly=True)
    keperluan = fields.Char('Keperluan')
    do_id = fields.Many2one('stock.picking','DO Id', readonly=True)
    date = fields.Datetime('Date', readonly=True)
    employee = fields.Many2one('hr.employee','Teknisi', readonly=True)


    state = fields.Selection([
        ('draft','Draft'),
        ('submit','Submit'),
        ('pr','Progress Purchase Request'),
        ('do','Progress Matrial Request'),
        ('done','Done'),
        ],'Status', default='draft')

    created_by = fields.Many2one('res.users', 'Created by', readonly=1, store=1)
    maintenance_type = fields.Selection(selection=[
        ('corrective', 'Unschedule'),
        ('preventive', 'Schedule'),
        ('accident', 'Accident')
    ])
    equipment_id = fields.Many2one(related='work_order_id.equipment_id', string='Unit Code')
    model = fields.Char()
    part_number = fields.Char(related='part_name.default_code')
    part_name = fields.Many2one('product.template')
    quantity = fields.Float()
    uom = fields.Many2one('uom.uom', 'Unit of Measure')
    hm = fields.Float()
    km = fields.Float()
    price = fields.Float()
    total_price = fields.Float()
    hm_km = fields.Char('HM/KM', compute='_compute_hm_km')
    work_order_id = fields.Many2one('work.order', 'No WO', readonly=True)
    component = fields.Many2one('component')
    avail_qty = fields.Float()
    reserve_qty = fields.Float()
    qty_done = fields.Float()

    @api.onchange('part_name')
    def _compute_part(self):
        for rec in self:
            if rec.state != 'draft':
                continue
            rec.price = rec.part_name.standard_price
            rec.avail_qty = rec.part_name.qty_available

    @api.onchange('quantity', 'price')
    def _compute_amount(self):
        for rec in self:
            if rec.state != 'draft':
                continue
            rec.total_price = rec.price * rec.quantity

    @api.depends('hm', 'km')
    def _compute_hm_km(self):
        for rec in self:
            rec.hm_km = str(rec.hm) + "/" + str(rec.km)

    def action_submit(self):
        for rec in self:
            rec.state = 'submit'
            rec.date = fields.Datetime.now()
            rec.name = self.env['ir.sequence'].next_by_code('mnt_matrial')

    def action_cek_oh(self):
        for rec in self:
            a=1
    def action_po(self):
        for rec in self:
            a=1
    def action_do(self):
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

class tbl_mnt_matrial_line(models.Model):
    _name = "tbl_mnt_matrial_line"

    details = fields.Many2one('tbl_mnt_matrial',"Details")
    name = fields.Many2one('product.template',string="Name")
    qty = fields.Float("Qty", default=1)
    qoh = fields.Float("Qty On Hand", readonly=True)
    uom = fields.Many2one('uom.uom',string="Unit of Measure", related='name.uom_id')
    pilih = fields.Boolean(".")

