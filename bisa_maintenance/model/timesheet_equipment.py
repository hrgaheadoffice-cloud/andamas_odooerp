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

class tbl_mnt_timesheet_equipment(models.Model):
    _name = "tbl_mnt_timesheet_equipment"
    _order = "tanggal desc"

    tanggal = fields.Date('Tanggal')
    kode_unit = fields.Char('Kode Unit')
    name = fields.Many2one('master_asset_maintenance','Nama Unit')
    brand = fields.Many2one('brand')
    model = fields.Many2one('model')
    shift = fields.Char('Shift')
    kode_operator = fields.Char('Kode Operator')
    nama_operator = fields.Many2one('hr.employee','Nama operator')
    meter_type = fields.Selection(selection=[('km', 'KM'), ('hm', 'HM'), ])
    hm_awal = fields.Float('HM Awal')
    hm_akhir = fields.Float('HM AKhir')
    km_awal = fields.Float('KM Awal')
    km_akhir = fields.Float('KM AKhir')
    fuel = fields.Float('Fuel')
    running_hr = fields.Float('Running Hour')
    stndby_hr = fields.Float('Standby Hour')
    total_hr = fields.Float('Total Hour')
    activity_hour = fields.Float()
    general_hour = fields.Float()
    idle_hour = fields.Float()
    breakdown_hour = fields.Float()
    mohh = fields.Float('MOHH')
    ewh = fields.Float('EWH/EWD')
    plan_bd = fields.Boolean(compute='_compute_plan_bd')
    periodic_service_detail_id = fields.Many2one('periodic.service.detail')
    sm_id = fields.Char()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def _compute_plan_bd(self):
        for me in self:
            periodic_service = self.env['periodic.service.detail'].search([('brand', '=', me.name.brand.id), ('model', '=', me.name.model.id),])
            wo = self.env['work.order'].search_count([('timesheet_id', '=', me.id)])
            if wo:
                me.plan_bd = False
                return
            for ps in periodic_service:
                if (me.hm_akhir > ps.limit_minimum) and (me.hm_akhir < ps.limit_maximum):
                    me.plan_bd = True
                    me.periodic_service_detail_id = ps.id
                    me.name.unit_status = 'need_mt'
                    return
            me.plan_bd = False
            return

    @api.onchange('activity_hour', 'general_hour')
    def onchange_ewh(self):
        self.ewh = self.activity_hour + self.general_hour

    @api.onchange('name')
    def onchange_unit(self):
        self.brand = self.name.brand
        self.model = self.name.model

    def action_planned_bd(self):
        compose_form = self.env.ref('bisa_maintenance.work_order_form')
        return {
            'name': _('Work Order'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'work.order',
            'target': 'self',
            'context': {
                'default_equipment_id': self.name.id,
                'default_kmhm_running': self.hm_akhir,
                'default_timesheet_id': self.id,
                'default_periodic_service_detail_id': self.periodic_service_detail_id.id
            },
        }
