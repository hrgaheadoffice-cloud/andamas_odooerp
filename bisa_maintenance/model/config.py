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

class tbl_mnt_lokasi_stock(models.Model):
    _name = "tbl_mnt_lokasi_stock"
    _order = 'name desc'
    # _order = "id desc" 


    company_id = fields.Many2one('res.company', 'Company',  index=True, default=lambda self: self.env.company)

    name = fields.Many2one('stock.location','Lokasi Stock', require=True)


