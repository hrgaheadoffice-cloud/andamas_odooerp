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

    is_petty_cash = fields.Boolean()
    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money'),
    ], string='Payment Type', default='outbound', required=True)
    amount = fields.Float(compute=_amount_sundry)
    show_amount = fields.Float('Amount')

    @api.model
    def create(self, vals):
        myctx = self._context.get('default_is_petty_cash')
        if myctx:
            vals['is_petty_cash'] = True
            if 'reversed_entry_id' not in vals:
                line_vals = {}
                journal_id = vals.get('journal_id')
                account_id = self.env['account.journal'].browse(journal_id).default_account_id.id
                line_vals['account_id'] = account_id
                print('is line ids ', vals.get('line_ids'))
                if vals.get('payment_type') == 'outbound':
                    line_vals['credit'] = vals.get('amount')
                else:
                    line_vals['debit'] = vals.get('amount')
                vals.get('line_ids').append([0, 0, line_vals])
            vals['show_amount'] = vals.get('amount')

        res = super(AccountMove, self).create(vals)
        return res

    # @api.model
    # def _get_default_journal(self):
    #     ''' Get the default journal.
    #     It could either be passed through the context using the 'default_journal_id' key containing its id,
    #     either be determined by the default type.
    #     '''
    #     move_type = self._context.get('default_move_type', 'entry')
    #     if move_type in self.get_sale_types(include_receipts=True):
    #         journal_types = ['sale']
    #     elif move_type in self.get_purchase_types(include_receipts=True):
    #         journal_types = ['purchase']
    #     elif self._context.get('default_is_petty_cash'):
    #         journal_types = ['cash']
    #     else:
    #         journal_types = self._context.get('default_move_journal_types', ['general'])
    #
    #     if self._context.get('default_journal_id'):
    #         journal = self.env['account.journal'].browse(self._context['default_journal_id'])
    #
    #         if move_type != 'entry' and journal.type not in journal_types:
    #             raise UserError(_(
    #                 "Cannot create an invoice of type %(move_type)s with a journal having %(journal_type)s as type.",
    #                 move_type=move_type,
    #                 journal_type=journal.type,
    #             ))
    #     else:
    #         journal = self._search_default_journal(journal_types)
    #
    #     return journal

    # @api.depends('company_id', 'invoice_filter_type_domain')
    # def _compute_suitable_journal_ids(self):
    #     for m in self:
    #         journal_type = m.invoice_filter_type_domain or 'general'
    #         company_id = m.company_id.id or self.env.company.id
    #         domain = [('company_id', '=', company_id), ('type', '=', journal_type)]
    #         if m.is_sundry:
    #             domain = [('company_id', '=', company_id), ('type', 'in', ['bank', 'cash'])]
    #         m.suitable_journal_ids = self.env['account.journal'].search(domain)
    #
    # @api.depends('posted_before', 'state', 'journal_id', 'date')
    # def _compute_name(self):
    #     def journal_key(move):
    #         return (move.journal_id, move.journal_id.refund_sequence and move.move_type)
    #
    #     def date_key(move):
    #         return (move.date.year, move.date.month)
    #
    #     grouped = defaultdict(  # key: journal_id, move_type
    #         lambda: defaultdict(  # key: first adjacent (date.year, date.month)
    #             lambda: {
    #                 'records': self.env['account.move'],
    #                 'format': False,
    #                 'format_values': False,
    #                 'reset': False
    #             }
    #         )
    #     )
    #     self = self.sorted(lambda m: (m.date, m.ref or '', m.id))
    #
    #     # Group the moves by journal and month
    #     for move in self:
    #         name = move.name
    #         move_has_name = move.name and move.name != '/'
    #         if move_has_name or move.state != 'posted':
    #             try:
    #                 if not move.posted_before:
    #                     # The move was never posted, so the name can potentially be changed.
    #                     move._constrains_date_sequence()
    #                 # Either the move was posted before, or the name already matches the date (or no name or date).
    #                 # We can skip recalculating the name when either
    #                 # - the move already has a name, or
    #                 # - the move has no name, but is in a period with other moves (so name should be `/`), or
    #                 # - the move has (temporarily) no date set
    #                 if (
    #                     move_has_name and move.posted_before
    #                     or not move_has_name and move._get_last_sequence(lock=False)
    #                     or not move.date
    #                 ):
    #                     continue
    #             except ValidationError:
    #                 # The move was never posted and the current name doesn't match the date. We should calculate the
    #                 # name later on, unless ...
    #                 if move._get_last_sequence(lock=False):
    #                     # ... we are in a period already containing moves: reset the name to `/` (draft)
    #                     move.name = '/'
    #                     continue
    #         group = grouped[journal_key(move)][date_key(move)]
    #         if not group['records']:
    #             # Compute all the values needed to sequence this whole group
    #             move._set_next_sequence()
    #             # if move.move_type == 'out_invoice':
    #             if move.move_type in ('out_invoice', 'in_invoice') and name:
    #                 move.name = name
    #             group['format'], group['format_values'] = move._get_sequence_format_param(move.name)
    #             group['reset'] = move._deduce_sequence_number_reset(move.name)
    #         group['records'] += move
    #
    #     # Fusion the groups depending on the sequence reset and the format used because `seq` is
    #     # the same counter for multiple groups that might be spread in multiple months.
    #     final_batches = []
    #     for journal_group in grouped.values():
    #         journal_group_changed = True
    #         for date_group in journal_group.values():
    #             if (
    #                 journal_group_changed
    #                 or final_batches[-1]['format'] != date_group['format']
    #                 or dict(final_batches[-1]['format_values'], seq=0) != dict(date_group['format_values'], seq=0)
    #             ):
    #                 final_batches += [date_group]
    #                 journal_group_changed = False
    #             elif date_group['reset'] == 'never':
    #                 final_batches[-1]['records'] += date_group['records']
    #             elif (
    #                 date_group['reset'] == 'year'
    #                 and final_batches[-1]['records'][0].date.year == date_group['records'][0].date.year
    #             ):
    #                 final_batches[-1]['records'] += date_group['records']
    #             else:
    #                 final_batches += [date_group]
    #
    #     # Give the name based on previously computed values
    #     for batch in final_batches:
    #         for move in batch['records']:
    #             move.name = batch['format'].format(**batch['format_values'])
    #             batch['format_values']['seq'] += 1
    #         batch['records']._compute_split_sequence()
    #
    #     self.filtered(lambda m: not m.name).name = '/'
    #
    # def submit_act(self):
    #     self.state = 'approve_requested'
    #     if self.move_type in ['out_invoice','in_invoice'] and self.journal_id:
    #         sequence = self.env['ir.sequence'].search([('name', '=', self.journal_id.name)])
    #         if not sequence:
    #             raise ValidationError("Cannot found sequence configuration for %r journal" % self.journal_id.name)
    #         elif self.name in ['/', '/0']:
    #             self.name = sequence.next_by_id()


