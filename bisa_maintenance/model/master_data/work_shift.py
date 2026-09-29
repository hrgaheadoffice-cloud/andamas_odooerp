from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import datetime
from datetime import date
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
import calendar

import base64
from urllib.request import urlopen


class WorkShift(models.Model):
    _name = "work_shift"
    _description = "Master Work Shift"
    # _order = "id desc"

    name = fields.Char()
    start_shift = fields.Float()
    end_shift = fields.Float()
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)



