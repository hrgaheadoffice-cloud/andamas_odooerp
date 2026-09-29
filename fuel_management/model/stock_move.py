from odoo import _, api, fields, models
from odoo.exceptions import ValidationError,UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    consumption_id = fields.Many2one('fuel.consumption')

    # def _get_dest_account(self, accounts_data):
    #     category_id = self.env['master.asset.category'].search([('id', '=', self.consumption_id.equipment_id.category.id)])
    #     account = False
    #     if self.consumption_id:
    #         account = category_id.outgoing_account.id
    #     return account or self.location_dest_id.valuation_in_account_id.id or accounts_data['stock_output'].id
