# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, _, api


class Users(models.Model):
    _inherit = 'res.users'

    cost_center_ids = fields.Many2many('account.cost.center', 'account_cost_center_users_rel', 'user_id', 'ccid',
        string='Cost Center')
    
    # journal_tujuan_id = fields.Many2one('account.journal','Jurnal Bank Tujuan')
