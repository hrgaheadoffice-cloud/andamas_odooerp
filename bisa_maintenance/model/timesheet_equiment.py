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
    # _order = "id desc" 


    nomor = fields.Char('Nomor', default='/')
    name = fields.Char('Nama Aset')
