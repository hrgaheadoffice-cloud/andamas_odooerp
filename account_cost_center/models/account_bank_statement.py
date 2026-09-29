from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools import float_is_zero
from odoo.tools import float_compare, float_round, float_repr
from odoo.tools.misc import formatLang, format_date
from odoo.exceptions import UserError, ValidationError

# from odoo import api, fields, models, _
import openpyxl
import base64
from io import BytesIO
# from odoo.exceptions import UserError
from datetime import datetime, date, time, timedelta, timezone

import time
import math
import base64
import re

class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    cost_center_id = fields.Many2one(
        "account.cost.center",
        readonly=False,
        required=True,
        help="Default Cost Center",
    )

    file = fields.Binary("File")
    file_name = fields.Char("File Name")

    def button_validate(self):
        if any(statement.state != 'posted' or not statement.all_lines_reconciled for statement in self):
            raise UserError(_('All the account entries lines must be processed in order to validate the statement.'))

        for statement in self:

            # Chatter.
            statement.message_post(body=_('Statement %s confirmed.', statement.name))

            # Bank statement report.
            if statement.journal_id.type == 'bank':
                try:
                    content, content_type = self.env.ref('account.action_report_account_statement')._render(statement.id)
                    self.env['ir.attachment'].create({
                        'name': statement.name and _("Bank Statement %s.pdf", statement.name) or _("Bank Statement.pdf"),
                        'type': 'binary',
                        'datas': base64.encodebytes(content),
                        'res_model': statement._name,
                        'res_id': statement.id
                    })
                except:
                    continue

        self._check_balance_end_real_same_as_computed()
        self.write({'state': 'confirm', 'date_done': fields.Datetime.now()})

    def action_generate(self):
        if not self.file:
            # raise UserError('The file must be filled.')
            raise UserError('Please insert a valid file')
        try:
                wb = openpyxl.load_workbook(filename=BytesIO(base64.b64decode(self.file)), read_only=True)
                ws = wb.active
                keys = ['Transaction Reference Number','Post Date','Transaction Date','Transaction Type',
                        'Description','Detail','Label','Debit Amount','Credit Amount','Ending Balance']
        except:
                raise UserError(_('Please insert a valid file'))
        if self.line_ids:
            self.line_ids.unlink()
        statement_line = self.env['account.bank.statement.line']
        for record in ws.iter_rows(min_row=3, max_row=None, min_col=None, max_col=None, values_only=True):
            values = dict(zip(keys, record))
            if values.get('Transaction Reference Number'):
                # raise UserError(values.get('Transaction Reference Number'))
                nominal = 0
                if values.get('Transaction Date'):
                    test_str = str(values.get('Transaction Date'))
                    format = "%Y-%m-%d %H:%M:%S"
                    res = True
                    try:
                                res = bool(datetime.strptime(test_str, format))
                    except ValueError:
                                res = False
                    if res == False:
                        raise UserError(_('The date format must be YYYY-MM-DD.'))
                    
                if values.get('Debit Amount') and values.get('Debit Amount') != 0:
                    nominal = values.get('Debit Amount')*-1
                else:
                    nominal = values.get('Credit Amount')
                data = ({
                                    'statement_id' : self.id,
                                    'payment_ref' : values.get('Label'),
                                    'date' : values.get('Transaction Date'),
                                    'amount' : nominal,
                                })
                line = statement_line.create(data)