# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models

import math


class msi_department_pc(models.Model):
    _inherit = 'hr.department'


    pc_limit = fields.Float('Limit Petty Cash')

