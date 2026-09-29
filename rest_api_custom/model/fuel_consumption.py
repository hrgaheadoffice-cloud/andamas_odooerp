from odoo import api, fields, models, _
import requests
from odoo.http import request
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class FuelConsumption(models.Model):
    _inherit = 'fuel.consumption'

    def fuel_consumption_journal(self):
        move = self.env['account.move']
        journal_id = self.env['account.journal'].search([('name', '=', 'Inventory Valuation'), ('company_id', '=', self.company_id.id)]).id

        generate_data_line = [
            (0, 0, {
                'account_id': self.fuel_source.incoming_account.id,
                'credit': self.total_price,
            }),
            (0, 0, {
                'account_id': self.equipment_id.category.outgoing_account.id,
                'debit': self.total_price,
            }),
        ]
        generate_data = {
            'ref': self.name,
            'journal_id': journal_id,
            'line_ids': generate_data_line,
        }
        move_id = move.create(generate_data)
        move_id.action_post()
        self.with_company(self.company_id).with_context(move_id=move_id.id).action_submit()
        return


