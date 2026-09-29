from collections import defaultdict

from odoo import api, fields, models
from odoo.exceptions import UserError


class FSMAdvanceClaimPayroll(models.Model):
    _name = 'fsm.advance.claim.payroll'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = 'name'
    _description = 'FSM Advance Claim Payroll'
    _order = 'id desc'

    name = fields.Char(default='/', readonly=True)
    driver_id = fields.Many2one('fsm.driver', "Driver", required=True)
    payroll_date = fields.Date(required=True)
    state = fields.Selection(string="Status", selection=[
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
    ], default='draft', )
    total_diff_to_be_paid = fields.Float()
    line_ids = fields.One2many(comodel_name="fsm.advance.claim.payroll.line", inverse_name="payroll_id", string="Line",
                               required=False, )

    def unlink(self):
        if self.state != 'draft':
            raise UserError("Cannot delete not draft document.")
        return super(FSMAdvanceClaimPayroll, self).unlink()

    @api.model_create_single
    def create(self, values):
        values['name'] = self.env.ref('fieldservice_custom.fsm_advance_claim_payroll_seq').next_by_id()
        return super(FSMAdvanceClaimPayroll, self).create(values)

    def action_populate_diff(self):
        if self.state != 'draft':
            raise UserError("Cannot populate different in not draft document.")
        residual_advance = self.driver_id.cost_advance_ids.filtered(
            lambda x:
            x.transporter_task_id.cost_difference_policy == 'accumulate_in_payroll' and
            not x.is_difference_claimed and
            x.difference_to_be_paid > 0
        )
        payroll_line = [(5, 0, 0)]
        total = 0
        for adv in residual_advance:
            payroll_line.append((0, 0, {
                'cost_advance_id': adv.id,
                'difference_to_be_paid': adv.difference_to_be_paid
            }))
            total += adv.difference_to_be_paid
        self.update({
            'total_diff_to_be_paid': total,
            'line_ids': payroll_line
        })
        return

    def action_confirm(self):
        claim_move_lines = defaultdict(list)
        for line in self.line_ids:
            line.cost_advance_id.is_difference_claimed = True
            claim_move_lines[line.cost_advance_id.bank_account_id.id].extend([
                (0, 0, {
                    'account_id': line.cost_advance_id.bank_account_id.payment_debit_account_id.id,
                    'partner_id': self.driver_id.name.user_partner_id.id,
                    'name': f'Claim advance {line.cost_advance_id.name} from payroll',
                    'debit': line.difference_to_be_paid,
                    'credit': 0
                }),
                (0, 0, {
                    'account_id': line.cost_advance_id.advance_account_id.id,
                    'partner_id': self.driver_id.name.user_partner_id.id,
                    'name': f'Claim advance {line.cost_advance_id.name} from payroll',
                    'debit': 0,
                    'credit': line.difference_to_be_paid
                }),
            ])
        for bank_id in claim_move_lines:
            payment = self.env['account.move'].create({
                'date': self.payroll_date,
                'partner_id': self.driver_id.name.user_partner_id.id,
                'ref': f"Claim Payroll Advance: {self.name}",
                'journal_id': bank_id,
                'line_ids': claim_move_lines[bank_id]
            })
            payment.action_post()
        self.state = 'confirm'
        return


class FSMAdvanceClaimPayrollLine(models.Model):
    _name = 'fsm.advance.claim.payroll.line'
    _description = 'FSM Advance Claim Payroll Line'

    payroll_id = fields.Many2one(comodel_name="fsm.advance.claim.payroll", string="Payroll", required=False, )
    cost_advance_id = fields.Many2one(comodel_name="fsm.cost.advance", string="Cost Advance", required=True, )
    settlement_date = fields.Date(related="cost_advance_id.settlement_date")
    difference_to_be_paid = fields.Float()
