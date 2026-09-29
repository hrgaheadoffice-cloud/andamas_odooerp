from odoo import api, fields, models
from odoo import _
from odoo.exceptions import UserError
import datetime
class FSMCostAdvance(models.Model):
    _name = 'fsm.cost.advance'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = 'name'
    _description = 'Cash Advance'
    _order = 'id desc'

    @api.model
    def _get_default_manager(self):
        emp_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        svp_id = self.env['hr.employee'].browse(emp_id.coach_id.id)
        manager = self.env["res.users"].browse(svp_id.user_id.id)
        return manager

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    @api.model
    def _get_department(self):
        emp_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        department = self.env['hr.employee'].browse(emp_id.department_id.id)
        return department

    name = fields.Char(default='/', readonly=True)
    request_date = fields.Date(default=fields.Date.today)
    driver_id = fields.Many2one('fsm.driver', readonly=True)
    department = fields.Many2one(comodel_name='hr.department',  default=_get_department, string='Department', readonly=1)
    nip = fields.Char(related="driver_id.nip")
    transporter_task_id = fields.Many2one(comodel_name="fsm.transporter.task", string="Transporter Task", readonly=True)
    amount_requested = fields.Float(compute='_compute_amount_requested')
    payment_request_id = fields.Many2one(comodel_name="account.move", string="Payment Request", readonly=True, )
    delivery_order_id = fields.Many2one(comodel_name="fsm.delivery.order", string="Delivery Order", required=False, )
    settlement_date = fields.Date()
    settlement_amount = fields.Float(compute='_compute_settlement_amount')
    difference_to_be_paid = fields.Float()
    payment_settlement_id = fields.Many2one(comodel_name="account.move", string="Payment Settlement", readonly=True, )
    request_line_ids = fields.One2many(comodel_name="fsm.cost.advance.request.line", inverse_name="cost_advance_id",
                                       string="Request Line")
    settlement_line_ids = fields.One2many(comodel_name="fsm.cost.advance.settlement.line", inverse_name="cost_advance_id",
                                       string="Settlement Line", readonly=0)
    bank_account_id = fields.Many2one(comodel_name="account.journal", string="Bank Account", required=False, )
    advance_account_id = fields.Many2one(comodel_name="account.account", default= '_compute_default_account', string="Advance Account", required=False, )
    req_attachment = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_req_attachment_rel", column1="m2m_id", column2="attachment_id", string="Request Advance Attachment", )
    settle_attachment = fields.Many2many(comodel_name="ir.attachment", relation="m2m_ir_settle_attachment_rel", column1="m2m_id", column2="attachment_id", string="Advance Settlement Attachment", )
    state = fields.Selection(string="Status", selection=[
        ('draft', 'Draft'),
        ('requested', 'Request Approval'),
        ('submit', 'Approved'),
        ('rejected', 'Rejected'),
        ('to_settle', 'To Settle'),
        ('done', 'Done')
    ], default='draft', )
    is_difference_claimed = fields.Boolean()
    cost_difference_policy = fields.Selection(
        selection=[
            ('deduct_next_advance', 'Deduct Next Advance'),
            ('accumulate_in_payroll', 'Accumulate In Payroll'),
        ],
        default='deduct_next_advance',
        related="transporter_task_id.cost_difference_policy"
    )
    residual_advance = fields.Float(readonly=True)
    amount_actual_advance = fields.Float(compute='_compute_actual_advance')
    requested_by = fields.Many2one(
        comodel_name="res.users",
        string="Requested by",
        required=True,
        copy=False,
        track_visibility="onchange",
        default=_get_default_requested_by,
        readonly=1,
        index=True,
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        string="Approve by",
        track_visibility="onchange",
        required=True,
        readonly=1,
        default=_get_default_manager
    )

    petty = fields.Float(compute='_compute_petty', string='Petty Cash Balance')
    petty_ho = fields.Float(compute='_compute_petty_ho', string='Petty Cash Balance')
    ca_type = fields.Selection(string="Cash Advance Type", selection=[
        ('ca', 'Cash Advance'),
        ('pc', 'Petty Cash'),
    ], default='ca')

    @api.depends('assigned_to')
    def _compute_petty(self):
        for record in self:
            site_amount = 0.0
            ho_amount = 0.0
            site_petty_name = self.env['account.account'].search([('name', '=', 'Petty Cash Site Office 1')])
            ho_petty_name = self.env['account.account'].search([('name', '=', 'Petty Cash Head Office')])
            if site_petty_name or ho_petty_name:
                site_petty_id = self.env['account.move.line'].search([('account_id', '=', site_petty_name.id), ('parent_state', '=', 'posted')])
                ho_petty_id = self.env['account.move.line'].search([('account_id', '=', ho_petty_name.id), ('parent_state', '=', 'posted')])
                if site_petty_id or ho_petty_id:
                    site_amount = sum(petty.balance for petty in site_petty_id)
                    ho_amount = sum(petty.balance for petty in ho_petty_id)
            record.petty = site_amount
            record.petty_ho = ho_amount

    @api.onchange('ca_type')
    def _compute_default_account(self):
        for me in self:
            if me.ca_type == 'pc':
                me.advance_account_id = False
            else:
                me.advance_account_id = 3404


    def _compute_actual_advance(self):
        for me in self:
            me.amount_actual_advance = self.amount_requested - me.residual_advance
        return

    def action_submit(self):
        if self.assigned_to.id != self.env.uid:
            raise UserError(_("Anda tidak berhak melakukan proses ini"))
        for me in self:
            if me.state != 'requested':
                raise UserError("Cannot submit not requested document.")
            if not me.bank_account_id:
                raise UserError("Please set bank in tab account.")
            if not me.advance_account_id:
                raise UserError("Please set advance account in tab account.")
            amount_requested = me.amount_requested - me.residual_advance
            payment = me.env['account.move'].create({
                'partner_id': me.driver_id.name.user_partner_id.id,
                'ref': f"Request Cash Advance: {me.name}",
                'journal_id': me.bank_account_id.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': me.bank_account_id.payment_credit_account_id.id,
                        'partner_id': me.driver_id.name.user_partner_id.id,
                        'name': f'Request Cash Advance {me.name}',
                        'debit': 0,
                        'credit': amount_requested
                    }),
                    (0, 0, {
                        'account_id': me.advance_account_id.id,
                        'partner_id': me.driver_id.name.user_partner_id.id,
                        'name': f'Transfer from {me.bank_account_id.name}',
                        'debit': amount_requested,
                        'credit': 0
                    }),
                ]
            })
            if self.ca_type == 'ca':
                payment.action_post()
                me.update({
                    'state': 'submit',
                    'payment_request_id': payment.id
                })
        return

    def action_to_settle(self):
        for me in self:
            if me.ca_type == 'ca':
                if me.state != 'submit':
                    raise UserError("Cannot set to settle not submit document")
            # if not me.delivery_order_id:
            #     raise UserError("Please select document delivery order before set to settle.")
            #
            me.update({
                'state': 'to_settle',
                # 'settlement_date': datetime.datetime.now()
            })
        return

    def action_done(self):
        if self.state != 'to_settle':
            raise UserError("Cannot set done not to settle document")
        if any([not x.account_id for x in self.settlement_line_ids]):
            raise UserError("Please fill account for each detail settlement!")
        params = self.env['ir.config_parameter'].sudo()
        settlement_expense_account_id = int(params.get_param('settlement_expense_account_id', "0"))
        # if not settlement_expense_account_id:
        #     raise UserError("Please set an account for settlement expense in configuration setting.")
        advance_to_claim = min(self.amount_requested, self.settlement_amount)
        settlement_move_lines = []
        if self.ca_type == 'ca':
            settlement_move_lines = [
                (0, 0, {
                    'account_id': self.advance_account_id.id,
                    'partner_id': self.driver_id.name.user_partner_id.id,
                    'name': f'Settlement from {self.payment_request_id.name}',
                    'debit': 0,
                    'credit': self.settlement_amount

                }),
                # (0, 0, {
                #     'account_id': settlement_expense_account_id,
                #     'partner_id': self.driver_id.name.user_partner_id.id,
                #     'name': f'Settlement from {self.payment_request_id.name}',
                #     'debit': self.settlement_amount,
                #     'credit': 0
                # }),
            ]
        else:
            settlement_move_lines = [
                (0, 0, {
                    'account_id': self.bank_account_id.payment_credit_account_id.id,
                    'partner_id': self.driver_id.name.user_partner_id.id,
                    'name': f'Settlement from {self.payment_request_id.name}',
                    'debit': 0,
                    'credit': self.settlement_amount
                }),
                # (0, 0, {
                #     'account_id': settlement_expense_account_id,
                #     'partner_id': self.driver_id.name.user_partner_id.id,
                #     'name': f'Settlement from {self.payment_request_id.name}',
                #     'debit': self.settlement_amount,
                #     'credit': 0
                # }),
            ]
        for line in self.settlement_line_ids:
            settlement_move_lines.append((0, 0, {
                'account_id': line.account_id.id,
                'partner_id': self.driver_id.name.user_partner_id.id,
                'name': line.name,
                'debit': line.amount,
                'credit': 0
            }))
        if self.difference_to_be_paid < 0:
            settlement_move_lines.append((0, 0, {
                'account_id': self.bank_account_id.payment_credit_account_id.id,
                'partner_id': self.driver_id.name.user_partner_id.id,
                'name': f"Cash Advance {self.name} difference",
                'debit': 0,
                'credit': abs(self.difference_to_be_paid)
            }))
        payment = self.env['account.move'].create({
            'date': self.settlement_date,
            'partner_id': self.driver_id.name.user_partner_id.id,
            'ref': f"Settlement Cash Advance: {self.name}",
            'journal_id': self.bank_account_id.id,
            'line_ids': settlement_move_lines
        })
        if self.ca_type in ['ca', 'pc']:
            payment.action_post()
            self.update({
                'state': 'done',
                'payment_settlement_id': payment.id
            })

        if self.cost_difference_policy == "accumulate_in_payroll":
            return
        # set all previous advance as claimed
        all_previous = self.driver_id.cost_advance_ids.filtered(
            lambda x:
            x.id != self.id and
            x.transporter_task_id.cost_difference_policy == "deduct_next_advance" and
            not x.is_difference_claimed
        )
        for prev in all_previous:
            prev.is_difference_claimed = True

        return

    @api.onchange('amount_requested', 'settlement_amount')
    def onchange_difference_to_be_paid(self):
        for me in self:
            diff_amount = 0
            if me.amount_requested and me.settlement_amount:
                diff_amount = me.amount_requested - me.settlement_amount
            self.difference_to_be_paid = diff_amount

    @api.depends('request_line_ids.amount')
    def _compute_amount_requested(self):
        for advance in self:
            advance.amount_requested = sum(advance.request_line_ids.mapped('amount'))

    @api.depends('settlement_line_ids.amount')
    def _compute_settlement_amount(self):
        for advance in self:
            advance.settlement_amount = sum(advance.settlement_line_ids.mapped('amount'))

    @api.onchange('delivery_order_id')
    def onchange_settlement_line(self):
        if self.state != 'submit':
            return
        settle_line = [
            (5, 0, 0),
            (0, 0, {
                'name': 'Meal cost',
                'amount': self.delivery_order_id.meal_cost
            }),
            (0, 0, {
                'name': 'Fuel cost',
                'amount': self.delivery_order_id.fuel_cost
            }),
            (0, 0, {
                'name': 'Other cost',
                'amount': self.delivery_order_id.other_cost
            }),
        ]
        self.update({
            'settlement_line_ids': settle_line,
            'settlement_amount': sum([x[-1]['amount'] for x in settle_line[1:]])
        })
        return

    @api.model_create_single
    def create(self, values):
        if values.get('name', '/') == '/':
            values['name'] = self.env.ref('fieldservice_custom.fsm_cost_advance_seq').next_by_id()

        template = super(FSMCostAdvance, self).create(values)

        if template.req_attachment:
            template.req_attachment.write({'res_model': self._name, 'res_id': template.id})
        if template.settle_attachment:
            template.settle_attachment.write({'res_model': self._name, 'res_id': template.id})

        return template

    def button_to_prepare(self):
        self.state = 'requested'

    def button_to_reject(self):
        if self.assigned_to.id != self.env.uid:
            raise UserError(_("Anda tidak berhak melakukan proses ini"))
        self.state = 'rejected'


class FSMCostAdvanceRequestLine(models.Model):
    _name = 'fsm.cost.advance.request.line'
    _rec_name = 'name'
    _description = 'FSM Cash Advance Request Line'

    cost_advance_id = fields.Many2one(comodel_name="fsm.cost.advance", string="Cash Advance", required=False, )
    name = fields.Char('Item')
    description = fields.Text('Description')
    amount = fields.Float()


class FSMCostAdvanceSettlementLine(models.Model):
    _name = 'fsm.cost.advance.settlement.line'
    _rec_name = 'name'
    _description = 'FSM Cash Advance Settlement Line'

    cost_advance_id = fields.Many2one(comodel_name="fsm.cost.advance", string="Cash Advance", required=False, )
    advance_detail = fields.Many2one(comodel_name="fsm.cost.advance.request.line")
    name = fields.Char('Item', related="advance_detail.name", readonly=0)
    description = fields.Text('Description')
    amount = fields.Float()
    # # account_id = fields.Many2one(comodel_name="account.account", string="Expense Account", required=False, )
    # account_id = fields.Many2one(comodel_name="account.account", string="Expense Account", required=False,
    #                              domain="['&','|',('user_type_id', 'like', 15),('code', 'like', '60'),"
    #                                     "('code', 'like', '50')]")
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Expense Account',
        required=False,
        domain=lambda self: [('id', 'in', self._get_account_ids())]
    )

    @api.model
    def _get_account_ids(self):
        cr = self.env.cr
        cr.execute("""
                SELECT * 
                FROM account_account 
                WHERE LEFT(code, 1) = '6' or LEFT(code, 1) = '5'
            """)
        result = cr.fetchall()
        return [r[0] for r in result]



