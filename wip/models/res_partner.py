from odoo import fields,models,api

class resPartner(models.Model):
    _inherit = 'res.partner'
    
    wip_account_id = fields.Many2one('account.account') 
    accrue_account_id = fields.Many2one('account.account') 
    expense_account_id = fields.Many2one('account.account') 