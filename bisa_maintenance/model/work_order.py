from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import datetime, timedelta


class WorkOrder(models.Model):
    _name = "work.order"
    _order = "id desc"

    name = fields.Char('No WO')
    maintenance_request = fields.Many2one('work.request')
    maintenance_activity = fields.Many2one('maintenance.activity', domain="[('asset_list.unit_code', '=', equipment_id)]")
    actual_dtbd = fields.Datetime(string='Actual Date & Time BD')
    actual_dtrfu = fields.Datetime(string='Actual Date & Time RFU')
    wr_date = fields.Datetime(string='Date & Time BD')
    start_date = fields.Datetime('Date & Time Start', readonly=1, store=1)
    rfu_date = fields.Datetime('Date & Time Finish', readonly=1, store=1)
    created_by = fields.Many2one('res.users', 'Created by',default=lambda self: self.env.uid, readonly=1, store=1)

    @api.model
    def _compute_category(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return [(6, 0, employee_id.category_ids.ids)]

    tags = fields.Many2many(comodel_name='hr.employee.category',default=lambda self: self._compute_category(), store=1)
    # equipment_id = fields.Many2one(related='maintenance_request.equipment_id')
    equipment_id = fields.Many2one('master_asset_maintenance',domain="[('plotting_location', 'in', tags)]")
    # location_problem = fields.Char(related='maintenance_request.location_problem')
    location_problem = fields.Char()
    prioritas = fields.Selection(selection=[
        ('0', 'Very Low'),
        ('1', 'Low'),
        ('2', 'Normal'),
        ('3', 'High')
    ], related='maintenance_request.priority')
    hm = fields.Float()
    km = fields.Float()
    maintenance_type = fields.Selection(selection=[
        ('corrective', 'Unschedule'),
        ('preventive', 'Schedule'),
        ('accident', 'Accident'),
        ('general', 'General')
    ], default='preventive')
    description = fields.Text()
    mechanic = fields.Many2many('hr.employee', domain="[('job_title', 'ilike', 'Mekanik')]")
    pareto = fields.Many2one('component')
    delay_factor = fields.Many2one('delay.factor')

    @api.onchange('delay_factor')
    def onchange_delay_factor(self):
        for rec in self:
            if self.env.company.id == 4:
                rec.delay_start = False
                rec.delay_finish = False
        return

    status = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('rfu', 'RFU'),
        ('close', 'Closed'),
        ('pending', 'Pending'),
        ('cancel', 'Cancel'),
    ], default='draft')
    detail_task = fields.One2many('tbl_mnt_task', 'work_order_id', 'Mechanic Task')
    # detail_part = fields.One2many('tbl_mnt_request_part', 'work_order_id', 'Detail Part')
    detail_part = fields.One2many('tbl_mnt_matrial', 'work_order_id', 'Detail Part')
    handover_ids = fields.One2many('handover', 'work_order_id', string='Handover Report', related='maintenance_request.handover_ids', readonly=False)
    repair_update_ids = fields.One2many('repair_update','work_order_id')
    other_info_ids = fields.One2many('other_info','work_order_id')
    schedule_activity = fields.Many2many('schedule.activity')
    reserve_part = fields.Boolean(default=False)
    hm_km = fields.Char('HM/KM', compute='_compute_hm_km')
    tire_service_ids = fields.One2many('tire.service', 'work_order_id')
    tire_service_count = fields.Integer(compute='_compute_tire_service_count')
    requisition_ids = fields.One2many('requisition', 'wo_number')
    requisition_count = fields.Integer(compute='_compute_requisition_count')

    # move_ids = fields.One2many(comodel_name="stock.move", inverse_name="work_order_id", string="Moves", required=False, )
    canibal_ids = fields.One2many(comodel_name="part.canibal", inverse_name="work_order_id", string="Canibal", required=False, )
    purchase_request_id = fields.Many2one(comodel_name="purchase.request", string="Purchase Request", required=False, )
    purchase_order_ids = fields.One2many(comodel_name="purchase.order", inverse_name="work_order_id", string="Purchase Order", required=False, )
    is_po_done = fields.Boolean(compute='compute_po_done')
    kmhm_running = fields.Float(string="KM/HM Running", related="equipment_id.kmhm_running")
    meter_type = fields.Selection(selection=[('km', 'KM'), ('hm', 'HM'), ], default='km', )
    operation = fields.Selection(selection=[
        ('stockpile', 'Stockpile'),
        ('hauling_internal', 'Hauling Internal'),
        ('hauling_subcon', 'Hauling Sub Con'),
        ('bp_project', 'BP Project'),
        ('ldlspga_ops', 'LDL & SPGA Ops'),
        ('head_office', 'Head Office'),
        ('mining', 'MINING'),
        ])
    asset_id = fields.Many2one('master_asset_maintenance', string="Asset ID")
    delay_start = fields.Datetime('Delay Start')
    delay_finish = fields.Datetime('Delay Finish')
    delay_time = fields.Char('Delay Time', compute='_compute_delay')
    cancel_reason = fields.Text('Cancel Reason')
    is_periodic = fields.Boolean()
    timesheet_id = fields.Many2one('tbl_mnt_timesheet_equipment')
    periodic_service_detail_id = fields.Many2one('periodic.service.detail')
    plotting_location = fields.Many2one(related='equipment_id.plotting_location', store=1)
    search_ids = fields.Char(compute="_compute_search_ids", search="search_ids_search")
    can_proceed = fields.Boolean(compute='_compute_can_proceed')
    can_req = fields.Boolean(compute='_compute_can_proceed')
    period_cycle = fields.Many2one('periodic.calculation.plan')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.onchange('maintenance_type','status')
    def _compute_can_proceed(self):
        for me in self:
            if me.status == 'draft' and me.maintenance_type in ('corrective','accident'):
                if me.company_id == 4:
                    me.can_proceed = True
                else:
                    me.can_proceed = False
            elif me.status == 'draft' and me.maintenance_type == 'preventive':
                me.can_proceed = True
            elif me.status in ('draft','pending'):
                me.can_proceed = True
            else:
                me.can_proceed = False

            if me.status == 'close':
                if self.env.company.id == 4:
                    me.can_req = True
                else:
                    me.can_req = False
            elif me.status == 'draft' and me.maintenance_type in ('corrective','accident'):
                me.can_req = False
            else:
                me.can_req = True

    def get_attachment_image(self,res_id):
        # Search for the attachment
        attachment = self.env['ir.attachment'].search([('name', 'like', 'logo_andamas')], limit=1)

        # Return the image data if found, else return None
        return attachment.datas if attachment else None

    @api.depends('created_by')
    def _compute_search_ids(self):
        print('my compute')

    def search_ids_search(self, operator, operand):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        tags = employee_id.category_ids

        obj = []
        for tag in tags:
            if tag.name in ('LDP-SPGA') and tag.name in ('LDP-BP'):
                objek = self.env['work.order'].search([]).ids
                for ob in objek:
                    obj.append(ob)
            elif not tag.name:
                objek = self.env['work.order'].search([]).ids
                for ob in objek:
                    obj.append(ob)
            else:
                objek = self.env['work.order'].search([('plotting_location', '=', tag.name)]).ids
                for ob in objek:
                    obj.append(ob)

        return [('id', 'in', obj)]

    @api.onchange('equipment_id')
    def onchange_equipment(self):
        self.meter_type = self.equipment_id.meter_type

    @api.onchange('schedule_activity')
    def _compute_is_periodic(self):
        for rec in self:
            periodic_service = self.env['schedule.activity'].search([('name', 'like', 'PERIODIC SERVICE'),('company_id', '=', self.env.company.id)], limit=1).id
            # rec.is_periodic = any(activity.id == periodic_service for activity in rec.schedule_activity)

            # if rec.schedule_activity:

            schedule_activity = rec.schedule_activity.ids
            if periodic_service in schedule_activity:
                rec.is_periodic = True
            else:
                rec.is_periodic = False
                # if activity == periodic_service:
                #     rec.is_periodic = True
                # else:
                #     rec.is_periodic = False

    # @api.model
    def write(self, vals):
        # Panggil metode super untuk memproses pembaruan catatan
        res = super(WorkOrder, self).write(vals)

        for record in self:
            for field in vals:
                unit = self.env['master_asset_maintenance'].search([('id', '=', record.equipment_id.id)])
                wr = self.env['work.request'].search([('work_order_id', '=', record.id)])
                if 'location_problem' in vals:
                    wr.location_problem = vals['location_problem']
                if 'kmhm_running' in vals:
                    unit.kmhm_running = vals['kmhm_running']
                if 'actual_dtrfu' in vals:
                    wr.actual_dtrfu = vals['actual_dtrfu']
                if self.env.company.id == 4:
                    if 'status' in vals:
                        if vals['status'] == 'rfu':
                         wr.state = vals['status']


        return res

    @api.model
    def _compute_delay(self):
        for rec in self:
            if rec.start_date and rec.actual_dtbd:
                if rec.start_date < rec.actual_dtbd:
                    rec.delay_time = "Invalid Date"
                else:
                    delay = rec.start_date - rec.actual_dtbd
                    hours, remainder = divmod(delay.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    delay_formatted = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
                    rec.delay_time = delay_formatted
            else:
                rec.delay_time = False

    def action_list(self):
        for activity in self.maintenance_activity:
            for task in activity.task_ids:
                line_ids = []
                for line in task.detail_task:
                    line_ids.append(line.id)
                self.update({
                    'detail_task': [
                        (0, 0, {
                            'detail_task': [(6, 0, line_ids)]
                        })
                    ]
                })
            for product in activity.sparepart_ids:
                self.update({
                    'move_ids': [
                        (0, 0, {
                            'name': self.name,
                            'component': product.component.id,
                            'product_id': product.product_id.id,
                            'price': product.product_id.standard_price,
                            'product_uom_qty': product.product_uom_qty,
                            'coa': product.coa,
                            'product_uom': product.product_id.uom_id.id,
                            'location_id': product.location_id.id,
                            'location_dest_id': product.location_dest_id.id
                        })
                    ]
                })

    def action_set_back_to_progress(self):
        if self.status != 'purchase_request':
            raise UserError("Cannot set back to on progress document that is not in purchase request")
        self.status = 'progress'
        return

    def compute_po_done(self):
        for me in self:
            is_done = False
            if me.purchase_order_ids:
                is_done = all([x.qty_received == x.product_uom_qty for x in me.purchase_order_ids[0].order_line])
            me.is_po_done = is_done
        return

    def action_create_purchase_request(self):
        if self.status != 'progress':
            raise UserError("Cannot create purchase request from document with status not on progress")
        pr_line = []
        purchase_request = self.env['purchase.request'].create({
            'origin': self.name,
            'description': 'WO requirement',
            'prepare_by': self.env.user.employee_id.id,
            'approval_svp': self.env.user.employee_id.id,
            'assigned_to': self.env.user.employee_id.id,
            'line_ids': pr_line,
            'work_order_id': self.id
        })
        self.update({
            'purchase_request_id': purchase_request.id,
        })
        return

    def _compute_need_purchase(self):
        for me in self:
            need_purchase = False
            if me.status == 'progress':
                need_purchase = any([x.full_available < x.product_uom_qty for x in me.move_ids])
            me.is_need_purchase = need_purchase
        return

    def action_view_tire_service(self):
        self.ensure_one()
        return {
            'name': _('Tire Service'),
            'view_mode': 'tree,form',
            'res_model': 'tire.service',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'delete': False},
            'domain': [('work_order_id', '=', self.id)],
            'target': 'current',
        }

    def action_view_requisition(self):
        self.ensure_one()
        return {
            'name': _('Requisition'),
            'view_mode': 'tree,form',
            'res_model': 'requisition',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'delete': False},
            'domain': [('wo_number', '=', self.id)],
            'target': 'current',
        }

    def action_create_tire_service(self):
        self.ensure_one()
        view_ids = self.env['ir.ui.view'].sudo().search([('name', 'like', 'view.tire.service.form')]).id
        return {
            'name': _('Tire Service'),
            'view_mode': 'form',
            'view_id': view_ids,
            'res_model': 'tire.service',
            'type': 'ir.actions.act_window',
            'context': {
                'default_work_order_id': self.id
            },
            'target': 'new',
        }

    @api.depends('tire_service_ids')
    def _compute_tire_service_count(self):
        for me in self:
            me.tire_service_count = len(me.tire_service_ids)

    @api.depends('tire_service_ids')
    def _compute_requisition_count(self):
        for me in self:
            me.requisition_count = len(me.requisition_ids)

    @api.depends('hm', 'km')
    def _compute_hm_km(self):
        for rec in self:
            rec.hm_km = str(rec.hm) + "/" + str(rec.km)

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('work.order.seq')
        unit = self.env['master_asset_maintenance'].search([('id', '=', vals['equipment_id'])])
        plot_name = self.env['hr.employee.category'].search([('id', '=', unit.plotting_location.id)]).name
        wo_exist = self.env['work.order'].search([('id', '=', vals['equipment_id']), ('status', 'in', ['draft', 'open'])])
        if wo_exist:
            if wo_exist.company_id.id != 4:
                raise ValidationError("Unit memiliki work order yang belum di rfu/close")
        if 'kmhm_running' in vals:
            unit.kmhm_running = vals['kmhm_running']

        if not plot_name:
            raise UserError("Plotting Location is Empty")
        else:
            vals['name'] = plot_name + '.' + sequence
        res = super(WorkOrder, self).create(vals)
        res.maintenance_request.work_order_id = res.id
        return res

    def action_progress(self):
        self.created_by = self.env.uid
        self.start_date = datetime.now()
        self.status = 'open'
        if self.is_periodic and self.period_cycle:
            self.period_cycle.update({
                'wo_id': self.id,
                'kmhm_actual': self.kmhm_running
            })
        self.equipment_id.kmhm_running = self.kmhm_running

    def action_reserve(self):
        if self.status != 'progress':
            raise UserError("Cannot reserve while document is not in progress")
        move_line = []
        for move in self.move_ids:
            move_line.append((0, 0, {
                'product_id': move.product_id.id,
                'reserved_availability': move.product_id.qty_available,
                'quantity_done': move.product_uom_qty,
                'product_uom': move.product_id.uom_id.id,
                'name': move.name,
            }))
        picking_vals = self.env['stock.picking'].create({
            'picking_type_id': 2,
            'location_id': self.move_ids.location_id.id,
            'location_dest_id': self.move_ids.location_id.id,
            'origin': self.maintenance_request.name + ' /' + self.name,
            'description': self.description,
            'move_ids_without_package': move_line
        })

        self.move_ids._action_confirm()
        self.move_ids._action_assign()
        return

    def action_done(self):
        if self.status != 'progress':
            raise UserError("Cannot set to done document that is not in progress")
        self.rfu_date = datetime.today()
        self.move_ids._action_done()
        self.status = 'done'
        return

    def action_close(self):
        self.status = 'close'
        self.rfu_date = datetime.now()

    def action_cancel_reason(self):
        view = self.env.ref('bisa_maintenance.tbl_bisa_maintenance_cancel_wizard')
        return {
            'name': _('Cancel Reason'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'work.order',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
        }

    def action_cancel(self):
        self.status = 'cancel'
        self.equipment_id.state = 'running'
        self.equipment_id.unit_status = 'running'

    def action_create_req(self):
        view_id = self.env.ref('bisa_maintenance.requisition_form_wizard').id
        return {
            'name': _('Requisition'),
            'view_mode': 'form',
            'views': [[view_id, 'form']],
            'res_model': 'requisition',
            'type': 'ir.actions.act_window',
            'res_id': False,
            'target': 'new',
            'context': dict(self._context, default_wo_number=self.id, default_equipment_id=self.equipment_id.id)
        }

    def action_pending(self):
        self.status = 'pending'
        for me in self:
            if not me.delay_factor:
                raise UserError("The postpone field must be filled in!")
            me.delay_start = datetime.now()

    def action_rfu(self):
        self.status = 'rfu'
        self.equipment_id.state = 'running'
        self.equipment_id.unit_status = 'running'
        for rec in self:
            if not rec.actual_dtrfu:
                raise UserError("Actual Date & Time RFU must be filled in!")

            if rec.maintenance_type == 'accident':
                if not rec.handover_ids:
                    raise UserError("Berita acara  must be filled in!")

    def action_process(self):
        # active_ids = self.env.context.get('active_ids', [])
        # records = self.env['work.order'].browse(active_ids) or self
        for record in self:
            if record.status != 'draft':
                raise UserError("Please select draft record!")

            if record.status == 'pending' and not record.delay_finish:
                raise UserError("Delay Factor must be filled in!")
            record.status = 'open'
            if record.is_periodic and record.period_cycle:
                record.period_cycle.update({
                    'wo_id': record.id,
                    'kmhm_actual': record.kmhm_running
                })
            record.start_date = datetime.now()
            record.delay_factor = False

            if record.maintenance_type == 'preventive':
                record.equipment_id.write({
                    'bd_date': record.actual_dtbd,
                    'problem': record.description,
                    'unit_status': 'mt_period',
                    'state': 'service'
                })
            else:
                record.equipment_id.write({
                    'unit_status': 'mt',
                    'state': 'service'
                })
    def action_process_batch(self):
        active_ids = self.env.context.get('active_ids', [])
        records = self.env['work.order'].browse(active_ids) or self
        for record in records:
            if record.status != 'draft':
                raise UserError("Please select draft record!")

            if record.status == 'pending' and not record.delay_finish:
                raise UserError("Delay Factor must be filled in!")
            record.status = 'open'
            if record.is_periodic and record.period_cycle:
                record.period_cycle.update({
                    'wo_id': record.id,
                    'kmhm_actual': record.kmhm_running
                })
            record.start_date = datetime.now()
            record.delay_factor = False

            if record.maintenance_type == 'preventive':
                record.equipment_id.write({
                    'bd_date': record.actual_dtbd,
                    'problem': record.description,
                    'unit_status': 'mt_period',
                    'state': 'service'
                })
            else:
                record.equipment_id.write({
                    'unit_status': 'mt',
                    'state': 'service'
                })


class Handover(models.Model):
    _name = "handover"

    number = fields.Char()
    name = fields.Char()
    attachment_ids = fields.Many2many(comodel_name="ir.attachment", string="Attachment", )
    work_order_id = fields.Many2one('work.order', 'No WO', readonly=True)
    work_request_id = fields.Many2one('work.request', 'No WR', readonly=True)

    @api.model
    def create(self, vals):
        res = super(Handover, self).create(vals)
        for template in res:
            if template.attachment_ids:
                template.attachment_ids.write({'res_model': self._name, 'res_id': template.id})
        return res

class RepairUpdate(models.Model):
    _name = "repair_update"

    work_order_id = fields.Many2one('work.order', 'No WO', readonly=True)
    date_time = fields.Datetime('Date & Time',default=datetime.now(), store=1)
    activity = fields.Char('Activity')

    @api.model
    def create(self, vals):
        res = super(RepairUpdate, self).create(vals)
        res.work_order_id.equipment_id.write({
            'bd_date': res.date_time,
            'problem': res.activity
        })
        return res

class OtherInfo(models.Model):
    _name = "other_info"

    work_order_id = fields.Many2one('work.order', 'No WO', readonly=True)
    information_number = fields.Char()
    information_from = fields.Char()

class ScheduleActivity(models.Model):
    _name = "schedule.activity"
    _rec_name = "name"

    name = fields.Char()
    work_order_id = fields.Many2one('work.order', 'No WO', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)


class DelayFactor(models.Model):
    _name = "delay.factor"

    name = fields.Char()
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)

class DetailTask(models.Model):
    _name = "detail.task"

    name = fields.Char('Task Name')
    duration = fields.Float()


class Component(models.Model):
    _name = "component"

    name = fields.Char()
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
