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

class tbl_mnt_timesheet_engineer(models.Model):
    _name = "tbl_mnt_timesheet_engineer"
    # _order = "id desc" 


    tanggal = fields.Date('Tanggal')
    shift = fields.Char('Shift')
    kode_operator = fields.Char('Kode Operator')
    name = fields.Many2one('hr.employee','Nama operator')
    lokasi = fields.Float('Lokasi')
    tgl_awal = fields.Datetime('Waktu Mulai')
    tgl_akhir = fields.Datetime('Waktu Selesai')
    desc = fields.Char('Deskripsi')
    unit = fields.Char('Unit')
