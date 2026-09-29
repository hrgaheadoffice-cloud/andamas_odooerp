from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from collections import defaultdict


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('line_ids.debit', 'line_ids.credit')
    def _amount_sundry(self):
        for rec in self:
            total_debit = 0.0
            total_credit = 0.0
            for line in rec.line_ids:
                total_debit += line.debit
                total_credit += line.credit
            amount = abs(total_debit-total_credit)
            rec.update({
                'amount': amount
            })

    is_sundry = fields.Boolean()
    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money'),
    ], string='Payment Type', default='inbound', required=True)
    amount = fields.Float(compute=_amount_sundry)
    show_amount = fields.Float('Amount')

    @api.model
    def create(self, vals):
        if vals.get('is_sundry'):
            if 'reversed_entry_id' not in vals:
                line_vals = {}
                journal_id = vals.get('journal_id')
                account_id = self.env['account.journal'].browse(journal_id).default_account_id.id
                line_vals['account_id'] = account_id
                if vals.get('payment_type') == 'outbound':
                    line_vals['credit'] = vals.get('amount')
                else:
                    line_vals['debit'] = vals.get('amount')
                vals.get('line_ids').append([0, 0, line_vals])
                vals['show_amount'] = vals.get('amount')

        res = super(AccountMove, self).create(vals)
        return res

class InheritAccountAccount(models.Model):
    _inherit = 'account.account'

    grouping_dashboard = fields.Selection(
        [('HM', 'HM'),
         ('FUEL', 'FUEL'),
         ('MAINTENANCE', 'MAINTENANCE'),
         ('SUB-CONTRACTOR', 'SUB-CONTRACTOR'),
         ('MAN POWER', 'MAN POWER'),
         ('OTHER OPS COST', 'OTHER OPS COST'),
         ('RENT DT & A2B', 'RENT DT & A2B'),
         ('DEPRECIATION', 'DEPRECIATION'),
         ('BACK CHARGE', 'BACK CHARGE'),
         ('OPEX', 'OPEX'),
         ('INSTALMENT', 'INSTALMENT'),
         ],
        string='Grouping Dashboard',
        )

class InheritAccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    activity = fields.Selection(
        [('Stockpile', 'Stockpile'),
         ('Hauling Internal', 'Hauling Internal'),
         ('Hauling Subcon', 'Hauling Subcon'),
         ('Rental', 'Rental'),
         ('Overburden', 'Overburden')],
        string='Activity',
        )