from datetime import datetime
from odoo import fields,models,api
from odoo.exceptions import ValidationError

class doCategory(models.Model):
    _name = 'do.category'
    
    name = fields.Char()
    wip_account_id = fields.Many2one('account.account') 
    accrue_account_id = fields.Many2one('account.account') 
    expense_account_id = fields.Many2one('account.account') 
    # product_id = fields.Many2one('product.product')