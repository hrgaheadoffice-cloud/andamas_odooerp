from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import UserError, AccessError, ValidationError


class WorkRequest(models.Model):
    _name = "work.request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    @api.onchange('work_order_rfu')
    def _compute_duration(self):
        for rec in self:
            wo = self.env['work.order'].search([('id', '=', rec.work_order_id.id)], limit=1)
            duration = 0
            if wo.actual_dtbd and wo.actual_dtrfu:
                duration = (wo.actual_dtrfu - wo.actual_dtbd).total_seconds() / 3600.0
            rec.duration_db = round(duration, 1)

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    name = fields.Char('No. PPA')
    user_id = fields.Many2one('res.users', 'Created by', default=lambda self: self.env.uid, readonly=True, store=True)
    search_ids = fields.Char(compute="_compute_search_ids", search="search_ids_search")

    @api.depends('user_id')
    def _compute_search_ids(self):
        print('my compute')

    def search_ids_search(self, operator, operand):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        tags = employee_id.category_ids
        obj = []
        for tag in tags:
            if tag.name in ('LDP-SPGA') and tag.name in ('LDP-BP'):
                objek = self.env['work.request'].search([])
                for ob in objek:
                    obj.append(ob.id)
            elif not tag.name:
                objek = self.env['work.request'].search([])
                for ob in objek:
                    obj.append(ob.id)
            else:
                objek = self.env['work.request'].search([('equipment_id.plotting_location', '=', tag.id)])
                for ob in objek:
                    obj.append(ob.id)

        return [('id', 'in', obj)]


    @api.model
    def _compute_category(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return [(6, 0, employee_id.category_ids.ids)]

    employee_category = fields.Many2many(comodel_name='hr.employee.category',default=lambda self: self._compute_category(), store=1)
    date = fields.Datetime(string='Date & Time BD', default=fields.Datetime.now)
    shift = fields.Selection(selection=[
        ('day', 'Day'),
        ('night', 'Night')
    ], default='_compute_shift')
    location_problem = fields.Char('Location BD')
    priority = fields.Selection(selection=[
        ('0', 'Very Low'),
        ('1', 'Low'),
        ('2', 'Normal'),
        ('3', 'High')
    ])
    maintenance_type = fields.Selection(selection=[
        ('corrective', 'Unschedule'),
        ('preventive', 'Schedule'),
        ('accident', 'Accident'),
        ('general', 'General')
    ], default='corrective')
    operator_driver = fields.Many2one('hr.employee', 'Operator/Driver', domain="['|',('job_title', 'like', 'Driver'),('job_title', 'like', 'Operator')]")
    equipment_id = fields.Many2one('master_asset_maintenance', 'Unit Code', domain="[('plotting_location', 'in', employee_category)]", store='True')
    category_equipment = fields.Many2one(related='equipment_id.kat_asset')
    hm = fields.Float()
    km = fields.Float()
    description = fields.Text('Problem Description')
    bd = fields.Char('Duration BD')
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('rfu', 'RFU'),
        ('cancel', 'Cancel')
    ], default='draft')
    work_order_id = fields.Many2one('work.order', 'No. Work Order', readonly=1)
    work_order_state = fields.Selection(related='work_order_id.status', string='Status Work Order')
    work_order_start = fields.Datetime('Date & Time Start', related='work_order_id.start_date', readonly=1)
    work_order_rfu = fields.Datetime('Date & Time Finish', related='work_order_id.rfu_date', readonly=1)
    duration_db = fields.Float('Duration BD', compute='_compute_duration', digits=(12, 2))
    delay_factor_state = fields.Many2one(related='work_order_id.delay_factor', string='Status Postpone')
    handover_ids = fields.One2many('handover', 'work_request_id', 'Handover Report')
    kmhm_running = fields.Float(string="KM/HM Running", related='equipment_id.kmhm_running', readonly=0)
    meter_type = fields.Selection(selection=[('km', 'KM'), ('hm', 'HM'), ], compute='get_meter_type', readonly=1)
    plotting_location = fields.Many2one(related="equipment_id.plotting_location", store=True)
    operation = fields.Selection(
        selection=[
            ('stockpile', 'STOCKPILE'),
            ('hauling_internal', 'HAULING INTERNAL'),
            ('hauling_subcon', 'HAULING SUB CON'),
            ('bp_project', 'BP PROJECT'),
            ('ldlspga_ops', 'LDL & SPGA OPS'),
            ('head_office', 'HEAD OFFICE'),
            ('mining', 'MINING'),
        ], required=1)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    actual_dtrfu = fields.Datetime(string='Actual Date & Time RFU')

    @api.onchange('date')
    def _compute_shift(self):
        for rec in self:
            if rec.date:
                hour = (rec.date.hour + 7) % 24
                shifts = self.env['work_shift'].search([])
                rec.shift = 'night'
                for shift in shifts:
                    start_time = int(shift.start_shift / 3600)
                    end_time = int(shift.end_shift / 3600)
                    if start_time <= end_time:
                        # Shift does not cross midnight
                        if start_time <= hour < end_time:
                            rec.shift = 'day'
                            break

    @api.depends('equipment_id')
    def get_meter_type(self):
        for rec in self:
            if rec.equipment_id:
                rec.meter_type = rec.equipment_id.meter_type
            else:
                rec.meter_type = False


    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('work.request.seq')
        plot = self.env['master_asset_maintenance'].search([('id', '=', vals['equipment_id'])]).plotting_location.id
        plot_name = self.env['hr.employee.category'].search([('id', '=', plot)]).name
        wr_exist = self.env['work.request'].search([('id', '=', vals['equipment_id']),('state', 'in', ['draft', 'submit'])])
        if wr_exist:
            if wr_exist.company_id.id != 4:
                raise ValidationError("Unit memiliki work request yang belum di rfu")
        if not plot:
            raise UserError("Plotting Location is Empty")
        else:
            vals['name'] = plot_name+'.'+ sequence
        return super(WorkRequest, self).create(vals)

    def action_submit(self):
        for record in self:
            if record.state != 'draft':
                raise UserError("Please select draft record!")

            work_order = self.env['work.order']
            vals = {
                'maintenance_request': record.id,
                'maintenance_type': record.maintenance_type,
                'wr_date': record.date,
                'actual_dtbd': record.date,
                'equipment_id': record.equipment_id.id,
                'location_problem': record.location_problem,
                'meter_type': record.meter_type,
                'kmhm_running': record.kmhm_running,
                'prioritas': record.priority,
                'description': record.description,
                'status': 'open',
                'operation': record.operation
            }
            if record.company_id.id == 4:
                vals['status'] = 'draft'
            work_order.create(vals)
            if record.maintenance_type != 'preventive':
                record.equipment_id.write({
                    'bd_date': record.date,
                    'problem': record.description,
                    'state': 'service'
                })
            record.state = 'submit'

    def action_submit_batch(self):
        active_ids = self.env.context.get('active_ids', [])
        records = self.env['work.request'].browse(active_ids) or self
        for record in records:
            if record.state != 'draft':
                raise UserError("Please select draft record!")

            work_order = self.env['work.order']
            vals = {
                'maintenance_request': record.id,
                'maintenance_type': record.maintenance_type,
                'wr_date': record.date,
                'actual_dtbd': record.date,
                'equipment_id': record.equipment_id.id,
                'location_problem': record.location_problem,
                'meter_type': record.meter_type,
                'kmhm_running': record.kmhm_running,
                'prioritas': record.priority,
                'description': record.description,
                'status': 'open',
                'operation': record.operation
            }
            if record.company_id.id == 4:
                vals['status'] = 'draft'
            work_order.create(vals)
            if record.maintenance_type != 'preventive':
                record.equipment_id.write({
                    'bd_date': record.date,
                    'problem': record.description,
                    'state': 'service'
                })
            record.state = 'submit'

    def action_cancel(self):
        self.state = 'cancel'

    def action_rfu(self):
        self.update({
            'state': 'rfu',
        })
        if self.work_order_id.status != 'close':
            self.work_order_id.update({
                'status': 'rfu',
                'actual_dtrfu': self.actual_dtrfu
            })
