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


class maintenance_report(models.Model):
    _name = "maintenance_report"
    # _order = "id desc"

    name = fields.Char('Name', default='Generate Report')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    tgl_awal = fields.Date('Tanggal Awal', required=True)
    tgl_akhir = fields.Date('Tanggal Akhir', required=True)
    detail = fields.One2many('maintenance_report_detail', 'details')

    def action_submit(self):
        for rec in self:
            # Hapus laporan maintenance sebelumnya jika ada
            rep = self.env['maintenance_report_detail'].search([('tanggal1', '=', rec.tgl_awal)])
            if rep:
                raise UserError("Dilarang nge generate dua kali")
            for reps in rep:
                reps.unlink()

            assets = self.env['master_asset_maintenance'].search([])
            start_wh = 0
            end_wh = 0
            total_wh = 0
            breakdown = 0
            mohh = 0
            mtbf = 0
            mttr = 0
            even = 0
            general = 0
            standby = 0
            idle = 0
            pa = 0
            ua = 0
            ma = 0
            eu = 0
            for asset in assets:
                timesheet = self.env['tbl_mnt_timesheet_equipment'].search([('name', '=', asset.id),
                                                                            ('tanggal', '>=', rec.tgl_awal),
                                                                            ('tanggal', '<=', rec.tgl_akhir)])
                if timesheet:
                    # Urutkan timesheet berdasarkan tanggal
                    sorted_timesheet = timesheet.sorted(key=lambda r: r.tanggal)
                    start_wh = sorted_timesheet[0].hm_awal
                    end_wh = sorted_timesheet[-1].hm_akhir
                    total_wh = sum(sheet.activity_hour for sheet in timesheet)
                    mohh = sum(sheet.mohh for sheet in timesheet)
                    breakdown = sum(sheet.breakdown_hour for sheet in timesheet)
                    even = sum(1 for sheet in timesheet if sheet.breakdown_hour > 0)
                    general = sum(sheet.general_hour for sheet in timesheet)
                    standby = sum(sheet.stndby_hr for sheet in timesheet)
                    idle = sum(sheet.idle_hour for sheet in timesheet)
                    pa = (total_wh + general + standby + idle) / (total_wh + general + standby + idle + breakdown) * 100
                    ua = (total_wh + general + idle) / (total_wh + general + standby + idle) * 100
                    ma = (total_wh + general + idle) / (total_wh + general + idle + breakdown) * 100
                    eu = (total_wh + general + idle) / (total_wh + general + standby + idle + breakdown) * 100
                    data = self.env['maintenance_report_detail'].create({
                        'details': rec.id,
                        'name': asset.id,
                        'tanggal1': rec.tgl_awal,
                        'tanggal2': rec.tgl_akhir,
                        'start_wh': start_wh,
                        'end_wh': end_wh,
                        'total_wh': total_wh,
                        'total_bd': breakdown,
                        'mohh': mohh,
                        'even': even,
                        'pa': pa,
                        'ma': ma,
                        'ua': ua,
                        'eu': eu,
                    })

                    if data.total_bd > 0 or even > 0:
                        data.mttr = data.total_bd / data.even

                    if total_wh == 0 or data.even == 0:
                        data.mtbf = 0
                    else:
                        data.mtbf = total_wh / data.even





class maintenance_report_detail(models.Model):
    _name = "maintenance_report_detail"

    details = fields.Many2one('maintenance_report', 'Details')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    tanggal1 = fields.Date('Tanggal Awal')
    tanggal2 = fields.Date('Tanggal Akhir')
    name = fields.Many2one('master_asset_maintenance', 'Nama Aset', readonly=True)
    lokasi = fields.Many2one('tbl_aset_lokasi', string="Lokasi", related='name.lokasi', store=True)
    tipe = fields.Char(string="Tipe", related='name.tipe', store=True)
    merek = fields.Char(string="Manufacture", related='name.merek', store=True)
    kat_asset = fields.Many2one('asset_maintenance_kategori', string="Kategori Asset", related='name.kat_asset',
                                store=True)
    start_wh = fields.Float('Start WH', help='Start Working Hours', readonly=True)
    end_wh = fields.Float('End WH', help='End Working Hours', readonly=True)
    total_wh = fields.Float('Total WH', help='Total Working Hours', readonly=True)
    mtbf = fields.Float('MTBF', help='Mean Time Between Failures', readonly=True)
    bs = fields.Float('BS', help='Breakdown Schedulle Tak ada Kendala', readonly=True)
    b0 = fields.Float('B0', help='	Breakdown dalam proses pekerjaan (tak ada kendala)', readonly=True)
    b1 = fields.Float('B1', help='Breakdown dikarenakan menunggu parts', readonly=True)
    b2 = fields.Float('B2', help='Breakdown menunggu Mechanic, tools, & Trasnport', readonly=True)
    b3 = fields.Float('B3', help='	Breakdown karena accident ataupun missoperation', readonly=True)
    b4 = fields.Float('B4', help='Breakdown karena perbaikan diluar site (out site repair)', readonly=True)
    b5 = fields.Float('B5', help='	Breakdown dikarenakan kerusakan dini (warranty)', readonly=True)
    b6 = fields.Float('B6', help='	Breakdown menunggu area /Waiting Space bay', readonly=True)
    b7 = fields.Float('B7', help='Waiting Weather', readonly=True)
    total_bd = fields.Float('Total BD', help='Total Breakdown', readonly=True)
    mttr = fields.Float('MTTR', help='Mean Time To Repair', readonly=True)
    even = fields.Float('Even', help='Even', readonly=True)
    mohh = fields.Float('MOHH', help='Machine On Hand Hours (sering disebut total jam dunia)', readonly=True)
    ma = fields.Float('MA', help='Physical Availability', readonly=True)
    pa = fields.Float('PA', help='Physical Availability', readonly=True)
    ua = fields.Float('UA', help='Use Of Availability', readonly=True)
    eu = fields.Float('EU', help='Effective Utilization', readonly=True)
