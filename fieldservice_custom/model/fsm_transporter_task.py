from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class FSMTransporterTask(models.Model):
    _name = 'fsm.transporter.task'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = 'name'
    _description = 'FSM Transporter Task'
    _order = 'id desc'

    @api.onchange('nip')
    def _onchange_nip(self):
        self.action_check()

    @api.onchange('transport_order_id')
    def _compute_transporter_cost(self):
        route_id = self.transport_order_id.route_id.id
        self.transporter_cost_id = self.env['fsm.transporter.cost'].search([('route_id', '=', route_id)])

    name = fields.Char('No. Task')
    created_by = fields.Many2one('res.users', 'Created by', default=lambda self: self.env.uid, readonly=1, store=1)
    date = fields.Datetime(string='Date & Time', default=fields.Datetime.now, store=True)
    nip = fields.Char('NIP')
    driver_id = fields.Many2one('fsm.driver')
    equipment_id = fields.Many2one('master_asset_maintenance', 'Unit Code')
    equipment_spare_id = fields.Many2one('master_asset_maintenance', 'Unit Spare')
    start_date = fields.Datetime('Date & Time Start', store=1)
    end_date = fields.Datetime('Date & Time Finish', store=1)
    transport_order_id = fields.Many2one('fsm.orders', 'No Transport Order', domain="[('id', 'in', transport_order_ids)]")
    transporter_cost_id = fields.Many2one('fsm.transporter.cost', 'Route Code')
    loading_location = fields.Many2one(related='transporter_cost_id.loading_location', readonly=1)
    unloading_location = fields.Many2one(related='transporter_cost_id.unloading_location', readonly=1)
    transporter_cost = fields.Float('Transporter Cost', related='transporter_cost_id.cost', readonly=1)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'On Progress'),
        ('loading', 'Loading'),
        ('closed', 'Closed'),
        ('cancel', 'Cancel'),
        ('reject', 'Reject')
    ], default='draft')
    cancel_reason = fields.Text(string="Cancel Reason", track_visibility="onchange")
    reject_reason = fields.Text(string="Reject Reason", track_visibility="onchange")
    delivery_order_status = fields.Selection(selection=[
        ('clear', 'Clear'),
        ('not_clear', 'Not Clear'), ], default="clear", )
    disciplinary_status = fields.Selection(selection=[
        ('clear', 'Clear'),
        ('not_clear', 'Not Clear'), ], default="clear", )
    maintenance_status = fields.Selection(selection=[
        ('clear', 'Clear'),
        ('not_clear', 'Not Clear'), ], default="clear", )
    delivery_order_id = fields.Many2one('fsm.delivery.order')
    cost_difference_policy = fields.Selection(selection=[
        ('deduct_next_advance', 'Deduct Next Advance'),
        ('accumulate_in_payroll', 'Accumulate In Payroll'),
    ], default='deduct_next_advance', )
    residual_advance = fields.Float()
    shift = fields.Selection(selection=[
        ('day', 'Day'),
        ('night', 'Night'), ], default="day", )
    transport_order_ids = fields.Many2many('fsm.orders', compute='_compute_transport_order_ids')
    due_date = fields.Date(compute='compute_due_date', store=True)

    @api.onchange('start_date', 'transporter_cost_id')
    def compute_due_date(self):
        for me in self:
            if not me.start_date or not me.transporter_cost_id:
                continue
            me.due_date = me.start_date + timedelta(days=me.transporter_cost_id.duration//24)
        return

    @api.depends('date')
    def _compute_transport_order_ids(self):
        schedule_route = self.env['fsm.schedule.route'].search([('state', '=', 'confirm')])
        order_ids = []
        for schedule in schedule_route:
            if schedule.route:
                order_ids.append(schedule.route.id)
            if schedule.route_2:
                order_ids.append(schedule.route_2.id)
            if schedule.route_3:
                order_ids.append(schedule.route_3.id)
            if schedule.route_4:
                order_ids.append(schedule.route_4.id)
            if schedule.route_5:
                order_ids.append(schedule.route_5.id)
            if schedule.route_change:
                order_ids.append(schedule.route_change.id)
            if schedule.route_change_2:
                order_ids.append(schedule.route_change_2.id)
            if schedule.route_change_3:
                order_ids.append(schedule.route_change_3.id)
            if schedule.route_change_4:
                order_ids.append(schedule.route_change_4.id)
            if schedule.route_change_5:
                order_ids.append(schedule.route_change_5.id)
        self.update({
            'transport_order_ids': [(6, 0, order_ids)]
        })

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('fsm.transporter.task.seq')
        return super(FSMTransporterTask, self).create(vals)

    def action_check(self):
        driver = self.env['fsm.driver'].search([('nip', '=', self.nip)], limit=1)
        maintenance_status = disciplinary_status = delivery_order_status = 'clear'
        driver_id = equipment_id = None

        residual_advance = 0
        if driver and self.state == 'draft':
            residual_advance = driver.cost_advance_to_deduct
            driver_id = driver.name.id
            equipment_id = driver.equipment_id.id
            disciplinary_action = self.env['disciplinary.action'].search_count([('employee_name', '=', driver_id), ('state', 'in', ['draft', 'explain', 'submitted'])])
            if disciplinary_action:
                disciplinary_status = 'not_clear'

            pending_delivery_order = self.env['fsm.delivery.order'].search_count([('driver_id', '=', driver_id), ('state', '=', 'draft')])
            if pending_delivery_order:
                delivery_order_status = 'not_clear'

            wo_on_progrss = self.env['work.order'].search_count([('equipment_id', '=', equipment_id), ('status', '=', 'progress')])
            if self.equipment_id.is_in_service_periodic or wo_on_progrss:
                maintenance_status = 'not_clear'

        self.update({
            'driver_id': driver.id,
            'equipment_id': equipment_id,
            'delivery_order_status': delivery_order_status,
            'disciplinary_status': disciplinary_status,
            'maintenance_status': maintenance_status,
            'residual_advance': residual_advance
        })

    def action_confirm(self):
        for me in self:
            if not me.driver_id:
                raise UserError("Please input valid NIP")
            if not me.transporter_cost_id:
                raise UserError("Please select Route Code")
            if not me.transporter_cost:
                raise UserError("Please select valid Route Code containing cost detail")
            request_line = [
                (0, 0, {
                    'name': 'Meal cost',
                    'amount': me.transporter_cost_id.meal_cost
                }),
                (0, 0, {
                    'name': 'Fuel cost',
                    'amount': me.transporter_cost_id.fuel_cost
                }),
                (0, 0, {
                    'name': 'Other cost',
                    'amount': me.transporter_cost_id.other_cost
                }),
            ]
            driver = me.env['fsm.driver'].search([('nip', '=', me.nip)], limit=1)
            me.env['fsm.cost.advance'].create({
                'driver_id': driver.id,
                'transporter_task_id': me.id,
                'amount_requested': me.transporter_cost,
                'residual_advance': me.residual_advance if me.cost_difference_policy == "deduct_next_advance" else 0,
                'request_line_ids': request_line,
                'settlement_amount': sum([x[2]['amount'] for x in request_line])
            })
            me.state = 'confirm'

    def action_loading(self):
        for me in self:
            # me.start_date = datetime.today()
            me.state = 'loading'
            me.delivery_order_status = 'not_clear'

    def action_create_delivery_order(self):
        view = self.env.ref('fieldservice_custom.view_fsm_delivery_order_form')
        return {
            'name': _('Create Delivery Order'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fsm.delivery.order',
            # 'views': [(view.id, 'form')],
            # 'view_id': view.id,
            'target': 'new',
            'context': {
                'default_transporter_task_id': self.id,
                'default_nip': self.nip,
                'default_driver_id': self.driver_id.id,
                'default_transport_order_id': self.transport_order_id.id,
                'default_equipment_spare_id': self.equipment_spare_id.id if self.equipment_spare_id else None
            }
        }
    
    def action_create_delivery_order_tree(self):
        for me in self:
            if me.state != 'loading' or me.delivery_order_id:
                raise ValidationError(_('Cannot create delivery order for %s' % me.name))
            delivery_order = me.env['fsm.delivery.order']
            delivery_order.create({
                'transporter_task_id': me.id,
                'nip': me.nip,
                'driver_id': me.driver_id.id,
                'transport_order_id': me.transport_order_id.id,
                'equipment_spare_id': me.equipment_spare_id.id if me.equipment_spare_id else None
            })

    def action_delivery_order_confirm(self):
        # self.end_date = datetime.today()
        self.delivery_order_status = 'clear'

    def action_close(self):
        self.state = 'closed'

    def action_cancel(self):
        self.state = 'cancel'

    def action_cancel_reason(self):
        view = self.env.ref('fieldservice_custom.fsm_transporter_task_cancel_wizard')
        return {
            'name': _('Cancel Reason'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fsm.transporter.task',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
        }

    def action_reject(self):
        self.state = 'reject'

    def action_reject_reason(self):
        view = self.env.ref('fieldservice_custom.fsm_transporter_task_reject_wizard')
        return {
            'name': _('Reject Reason'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fsm.transporter.task',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
        }

    def action_draft(self):
        self.state = 'draft'

    def send_24_hours_notification(self):
        params = self.env['ir.config_parameter'].sudo()
        email_transporter_task_exceed_24_hours = params.get_param('email_transporter_task_exceed_24_hours',
                                                                  "hery.halim@bombagrup.com")
        email_template = self.env.ref('fieldservice_custom.mail_template_transporter_task_after_24_hours')
        email_values = {
            "email_to": email_transporter_task_exceed_24_hours
        }
        for me in self:
            email_template.send_mail(me.id, force_send=True, email_values=email_values)
        return

    def send_48_hours_notification(self):
        params = self.env['ir.config_parameter'].sudo()
        email_transporter_task_exceed_48_hours = params.get_param('email_transporter_task_exceed_48_hours', "widiyono@bombagrup.com")
        email_template = self.env.ref('fieldservice_custom.mail_template_transporter_task_after_48_hours')
        email_values = {
            "email_to": email_transporter_task_exceed_48_hours
        }
        for me in self:
            email_template.send_mail(me.id, force_send=True, email_values=email_values)
        return

    @api.model
    def execute_task_after_24_hours(self):
        print("Send notification exceed 48 hours: STARTING...")
        tasks = self.env['fsm.transporter.task'].search([
            ('end_date', '=', False),
            ('due_date', '<=', datetime.now() - relativedelta(hours=24)),
        ])
        print(f"{len(tasks)} tasks found exceed 48 hours")
        tasks.send_24_hours_notification()
        return

    @api.model
    def execute_task_after_48_hours(self):
        print("Send notification exceed 48 hours: STARTING...")
        tasks = self.env['fsm.transporter.task'].search([
            ('end_date', '=', False),
            ('due_date', '<=', datetime.now() - relativedelta(hours=48)),
        ])
        print(f"{len(tasks)} tasks found exceed 48 hours")
        tasks.send_48_hours_notification()
        return
