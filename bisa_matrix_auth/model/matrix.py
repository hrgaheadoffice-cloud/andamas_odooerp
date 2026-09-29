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

class tbl_matrix_auth(models.Model):
    _name = "tbl_matrix_auth"
    # _order = "id desc" 
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = 'modul'

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    proc_group_id = fields.Many2one('tbl_proc_group','Procurement Category')
    location1 = fields.Many2one('account.analytic.account','Location')
    cost_center = fields.Many2one('account.cost.center','Cost Center')
    persen_awal = fields.Integer('% Budget Start')
    persen_akhir = fields.Integer('% Budget End')
    value_awal = fields.Integer('Amount Start')
    value_akhir = fields.Integer('Amount End')  
    maker = fields.Selection([
        ('ALL_USERS', 'ALL USERS'),
        ('SELECTED_USER', 'SELECTED USER'),
        ], string='Maker',  copy=False, index=True, tracking=True, default='ALL_USERS')
    maker_position = fields.Many2one('hr.job','Maker Position')
    review_position = fields.Many2one('hr.job','Reviewer Position')
    approval_position = fields.Many2one('hr.job','Approval Position')
    approval_user = fields.Many2one('res.users','Approval User', required=True)

    modul = fields.Selection([
        ('PR', 'PR'),
        ('PO', 'PO'),
        ('PAYMENT', 'PAYMENT PLAN'),
        ('EXPENSE', 'EXPENSE'),
        ('ADVANCE', 'ADVANCE'),
        ], string='Modul',  copy=False, index=True, tracking=True, default='PR')

    level = fields.Selection([
        ('1', 'Level 1'),
        ('2', 'Level 2'),
        ('3', 'Level 3'),
        ('4', 'Level 4'),
        ('5', 'Level 5'),
        ], string='Level',  copy=False, index=True, tracking=True, default='1')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archive', 'Archive'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')


    def action_active(self):
        a=1

    def action_inactive(self):
        a=1

class ConfigApprovalMatrix(models.Model):
    _name = "config.approval.matrix"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    matrix_level_id = fields.Many2one('matrix.level','Level', required=True)
    matrix_level_name = fields.Char(related="matrix_level_id.name",string='Level Name', store=True)
    proc_group_id = fields.Many2one('tbl_proc_group','Procurement Category')
    approval_user_ids = fields.Many2many(comodel_name='res.users',string='Approval User', required=True)
    delegate_user = fields.Many2one('res.users','Delegate User')
    modul = fields.Selection([
        ('PR', 'Purchase Request'),
        ('PO', 'Purchase Order'),
        ('PAYMENT', 'Payment Plan'),
        ('Vendor Bills', 'Vendor Bills'),
        # ('EXPENSE', 'Expense'),
        # ('ADVANCE', 'Advance'),
        ('NOI HO', 'Noi HO'),
        ('Cash Advance ho', 'Cash Advance HO'),
        ('Settlement Ho', 'Settlement HO'),
        ('Cash Advance Site', 'Cash Advance SITE'),
        ('Settlement Site', 'Settlement SITE'),
        ('Cash Request', 'Cash Request'),
        ('Reimbursement HO', 'Reimbursement HO'),
        ('Reimbursement Site', 'Reimbursement SITE'),
        ('Sundry Site', 'Sundry SITE'),        
        ], string='Modul',  copy=False, index=True, tracking=True, default='PR')
    tag_warehouse = fields.Many2many('stock.warehouse','rel_conf_appr_matrix',string='Location',index=True)
    department_id  = fields.Many2one('hr.department',string='Department',index=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company.id)
    expected_amount = fields.Float('Expected Amount', store=True, required=True)
    
class MatrixLevel(models.Model):
    _name = "matrix.level"

    name = fields.Char('Name')

class ApprovalMatrixLevel(models.Model):
    _name = "approval.matrix"

    name            = fields.Char('Name')
    config_approval_matrix_id = fields.Many2one('config.approval.matrix','Config Approval Matrix', ondelete='restrict')
    matrix_level_id = fields.Many2one('matrix.level','Matrix Level')
    user_ids = fields.Many2many(comodel_name='res.users',string='Approval User')
    realization_user_id = fields.Many2one('res.users','Approved By')
    date = fields.Datetime('Date')
    note = fields.Char('Note')
    state = fields.Char('State')








