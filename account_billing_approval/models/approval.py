from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError\


class AccountMove(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(selection_add=[
        ('draft', 'Draft'),
        ("payment_draft", "Payment Draft"),
        ('approve_requested', 'Approve Requested'),
        ('manager_approved', 'Manager Approved'),
        ('tax_approved', 'Tax Approved'),
        ('admin_approved', 'Approved'),
        ('payment_approved', 'Approve payment'),
        ("approved1", "Tobe Approved"),
        ("approved2", "Tobe Approved 2"),
        ("approved3", "Tobe Approved 3"),
        ("approved4", "Tobe Approved 4"),
        ("approved5", "Tobe Approved 5"),
        ("approved", "Approved"),
        ('cancel', 'Cancel'),
        ('posted', 'Posted'),
        ("done", "Done"),
    ],
        ondelete={
            'draft': 'set default',
            'payment_draft': 'set default',
            'approve_requested': 'set default',
            'admin_approved': 'set default',
            'manager_approved': 'set default',
            'tax_approved': 'set default',
            'payment_approved': 'set default',
            'approved1': 'set default',
            'approved2': 'set default',
            'approved3': 'set default',
            'approved4': 'set default',
            'approved5': 'set default',
            'approved': 'set default',
            'cancel': 'set default',
            'posted': 'set default',
            'done': 'set default',
        })

    state_a = fields.Selection(related='state')
    state_b = fields.Selection(related='state')
    state_c = fields.Selection(related='state')
    state_d = fields.Selection(related='state')
    state_e = fields.Selection(related='state')

    def submit_act(self):
        self.state = 'approve_requested'

    def admin_approve_act(self):
        self.state = 'admin_approved'

    def tax_approve_act(self):
        self.state = 'tax_approved'
        

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.depends('journal_id')
    def _compute_approval_stage(self):
        for rec in self:
            approval_stage = 0
            if rec.payment_type == 'inbound':
                emp_id = rec.env['tbl_matrix_auth'].search([('modul', '=', 'receive')])
            else:
                emp_id = rec.env['tbl_matrix_auth'].search([('modul', '=', 'PAYMENT')])
            for me in emp_id:
                if rec.amount_total > me.value_awal:
                    approval_stage += 1
            rec.approval_stage = approval_stage
        return

    origin_invoice_ids = fields.Many2many('account.move', string='Invoice Origin')
    to_reconcile_inv = fields.Many2one('account.move.line', string='Reconcile Move Line')
    approval_stage = fields.Integer(compute=_compute_approval_stage)
    next_approver_ids = fields.Many2many('res.users', compute='_compute_next_approver_ids')

    appr4 = fields.Many2one(
        comodel_name="res.users",
        string='Approved By',
        copy=False,
        track_visibility="onchange",
    )

    def action_post(self):
        """Overwrites the _post() to validate the payment in the 'approved' stage too.
        Currently Odoo allows payment posting only in draft stage.
        """

        if self._context.get('active_model') == 'account.move':
            if self._context.get('active_ids'):
                if len(self._context.get('active_ids')) == 1:
                    self.write({
                        'origin_invoice_ids': [(4, self._context.get('active_ids')[0])]
                    })
                    validation = self._check_payment_approval()
                    if not validation:
                        if self.state in ('approved1'):
                            return True
                        if self.state not in ('draft', 'approved'):
                            raise UserError(_("Only a draft or approved payment can be posted."))

                        if any(inv.state != 'posted' for inv in self.reconciled_invoice_ids):
                            raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
                        self.move_id._post(soft=False)
                    else:
                        self.move_id._post(soft=False)

                if len(self._context.get('active_ids')) > 1:

                    for rec in self:
                        validation = rec._check_payment_approval()

        else:
            validation = self._check_payment_approval()
            if not validation:
                if self.state in ('approved1'):
                    return True
                if self.state not in ('draft', 'approved'):
                    raise UserError(_("Only a draft or approved payment can be posted."))

                if any(inv.state != 'posted' for inv in self.reconciled_invoice_ids):
                    raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
                self.move_id._post(soft=False)
                self.reconcile_move_payment()
            else:
                self.move_id._post(soft=False)
                self.reconcile_move_payment()

    def reconcile_move_payment(self):
        if self.to_reconcile_inv:
            domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
            payment_lines = self.line_ids.filtered_domain(domain)
            lines = self.to_reconcile_inv

            for account in payment_lines.account_id:
                (payment_lines + lines) \
                    .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)]) \
                    .reconcile()
    
    def _check_payment_approval(self):
        if not self.state:
            return True
        if self.state == "draft":
            if self.approval_stage > 0:
                self.write({
                    'state': 'approved1'
                })
                return False
        return True

    @api.depends('state')
    def _compute_next_approver_ids(self):
        for rec in self:
            if rec.state == 'draft':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'receives'), ('level', '=', '1')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved1':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'PAYMENT'), ('level', '=', '1')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved2':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'PAYMENT'), ('level', '=', '2')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved3':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'PAYMENT'), ('level', '=', '3')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved4':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'PAYMENT'), ('level', '=', '4')]).approval_user
                rec.next_approver_ids = next_approver
            elif rec.state == 'approved5':
                next_approver = self.env['tbl_matrix_auth'].search(
                    [('modul', '=', 'PAYMENT'), ('level', '=', '5')]).approval_user
                rec.next_approver_ids = next_approver
            else:
                rec.next_approver_ids = False
    
    def button_appr1(self):
        if self.env.user not in self.next_approver_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr1 = self.env.user
        # self.appr1_dt = fields.Datetime.now()
        if self.approval_stage > 1:
            self.state = 'approved2'
        else:
            self.state = 'approved'

    def button_appr2(self):
        if self.env.user not in self.next_approver_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr2 = self.env.user
        # self.appr2_dt = fields.Datetime.now()
        if self.approval_stage > 2:
            self.state = 'approved3'
        else:
            self.state = 'approved'

    def button_appr3(self):
        if self.env.user not in self.next_approver_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr3 = self.env.user
        # self.appr3_dt = fields.Datetime.now()
        if self.approval_stage > 3:
            self.state = 'approved4'
        else:
            self.state = 'approved'

    def button_appr4(self):
        if self.env.user not in self.next_approver_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr4 = self.env.user
        # self.appr4_dt = fields.Datetime.now()
        if self.approval_stage > 4:
            self.state = 'approved5'
        else:
            self.state = 'approved'

    def button_appr5(self):
        if self.env.user not in self.next_approver_ids:
            raise UserError(
                _("Anda tidak berhak melakukan proses ini"))
        self.appr5 = self.env.user
        # self.appr5_dt = fields.Datetime.now()
        self.state = 'approved'

    def button_to_approve(self):

        if self.payment_type == 'inbound':
            if self.env.user not in self.next_approver_ids:
                raise UserError(
                    _("Anda tidak berhak melakukan proses ini"))
            self.state = 'approved'
        else:
            self.state = 'approved1'





class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payments(self):
        self.ensure_one()
        batches = self._get_batches()
        edit_mode = self.can_edit_wizard and (len(batches[0]['lines']) == 1 or self.group_payment)
        to_process = []

        if edit_mode:
            payment_vals = self._create_payment_vals_from_wizard()
            to_process.append({
                'create_vals': payment_vals,
                'to_reconcile': batches[0]['lines'],
                'batch': batches[0],
            })
        else:
            # Don't group payments: Create one batch per move.
            if not self.group_payment:
                new_batches = []
                for batch_result in batches:
                    for line in batch_result['lines']:
                        new_batches.append({
                            **batch_result,
                            'lines': line,
                        })
                batches = new_batches

            for batch_result in batches:
                to_reconcile_inv = batch_result['lines']
                to_process.append({
                    'create_vals': self._create_payment_vals_from_batch(batch_result),
                    'to_reconcile': batch_result['lines'],
                    'batch': batch_result,
                })

        payments = self._init_payments(to_process, edit_mode=edit_mode)
        self._post_payments(to_process, edit_mode=edit_mode)

        for item_rec in to_process:
            item_rec.get('payment').write({
                'to_reconcile_inv': item_rec.get('to_reconcile'),

            })

        for rec in payments:
            if rec.state == 'posted':
                self._reconcile_payments(to_process, edit_mode=edit_mode)
        return payments
