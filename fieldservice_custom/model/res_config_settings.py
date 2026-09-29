import ipdb

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    settlement_expense_account_id = fields.Many2one(comodel_name="account.account", string="Settlement Expense Account", required=False, )
    email_transporter_task_exceed_24_hours = fields.Char()
    email_transporter_task_exceed_48_hours = fields.Char()

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('settlement_expense_account_id', self.settlement_expense_account_id.id)
        param.set_param('email_transporter_task_exceed_24_hours', self.email_transporter_task_exceed_24_hours)
        param.set_param('email_transporter_task_exceed_48_hours', self.email_transporter_task_exceed_48_hours)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        settlement_expense_account_id = int(params.get_param('settlement_expense_account_id', "0"))
        email_transporter_task_exceed_24_hours = params.get_param('email_transporter_task_exceed_24_hours', "hery.halim@bombagrup.com")
        email_transporter_task_exceed_48_hours = params.get_param('email_transporter_task_exceed_48_hours', "widiyono@bombagrup.com")
        res.update({
            'settlement_expense_account_id': settlement_expense_account_id,
            'email_transporter_task_exceed_24_hours': email_transporter_task_exceed_24_hours,
            'email_transporter_task_exceed_48_hours': email_transporter_task_exceed_48_hours,
        })
        return res
