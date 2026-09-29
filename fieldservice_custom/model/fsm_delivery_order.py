from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class FSMDeliveryOrder(models.Model):
    _name = 'fsm.delivery.order'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = 'id desc'

    name = fields.Char()
    delivery_order = fields.Char('Physical DO')
    created_by = fields.Many2one('res.users', 'Created by', default=lambda self: self.env.uid, readonly=1, store=1)
    date = fields.Datetime(string='Date & Time', default=fields.Datetime.now, store=True)
    transporter_task_id = fields.Many2one('fsm.transporter.task', 'No. Transporter Task')
    nip = fields.Char('NIP', store=1)
    driver_id = fields.Many2one('hr.employee', 'Driver Name', compute="_compute_driver", store=1)
    equipment_id = fields.Many2one('master_asset_maintenance', 'Unit Code', related='transporter_task_id.equipment_id')
    equipment_spare_id = fields.Many2one('master_asset_maintenance', 'Unit Spare', related='transporter_task_id.equipment_spare_id')
    brutto_weight = fields.Float()
    terra_weight = fields.Float()
    netto_weight = fields.Float('Netto Weight (MT)')
    transport_order_id = fields.Many2one('fsm.orders', 'No Transport Order')
    transporter_cost_id = fields.Many2one('fsm.transporter.cost', 'Route Code', compute='_compute_transporter_cost')
    loading_location = fields.Many2one(related='transporter_cost_id.loading_location')
    unloading_location = fields.Many2one(related='transporter_cost_id.unloading_location')
    transporter_cost = fields.Float('Transporter Cost', related='transporter_cost_id.cost')
    meal_cost = fields.Float(compute='_compute_other_cost')
    fuel_cost = fields.Float(compute='_compute_other_cost')
    other_cost = fields.Float(compute='_compute_other_cost')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm')
    ], default='draft')
    distance = fields.Float(related='transporter_cost_id.distance', readonly=1)
    ready_hour = fields.Float()
    general_hour = fields.Float()
    asset_id = fields.Many2one('master_asset_maintenance', string="Asset ID")
    working_hour = fields.Float('Working Hour', default=12)
    ewh = fields.Float('EWH')
    delay_hour = fields.Float('Delay Hour')
    idle_hour = fields.Float('Idle Hour')
    breakdown_hours = fields.Float('Breakdown Hour')
    shift = fields.Selection([
        ('day', 'Day Shift'),
        ('night', 'Night Shift')
    ])

    @api.depends('nip')
    def _compute_driver(self):
        for me in self:
            me.driver_id = me.env['hr.employee'].search([('barcode', '=', me.nip)]).id


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('fsm.delivery.order.seq')
        res = super(FSMDeliveryOrder, self).create(vals)
        res.transporter_task_id.delivery_order_id = res.id
        return res

    # @api.onchange('transport_task_id')
    # def _compute_transport_order(self):
    #     for me in self:
    #         if me.transport_task_id:
    #             me.update({
    #                 'transport_order_id': me.transport_task_id.transport_order_id,
    #                 'nip': me.transport_task_id.nip,
    #                 'driver_id': me.transport_task_id.driver_id
    #             })

    @api.depends('transport_order_id')
    def _compute_transporter_cost(self):
        for me in self:
            if me.transport_order_id:
                route_id = me.transport_order_id.route_id
                transporter_cost_id = self.env['fsm.transporter.cost'].search([('route_id', '=', route_id.id)])
                me.transporter_cost_id = transporter_cost_id
            else:
                me.transporter_cost_id = False

    @api.depends('transporter_cost_id')
    def _compute_other_cost(self):
        for me in self:
            if me.transporter_cost_id:
                me.update({
                    'meal_cost': me.transporter_cost_id.meal_cost,
                    'fuel_cost': me.transporter_cost_id.fuel_cost,
                    'other_cost': me.transporter_cost_id.other_cost
                })
            else:
                me.update({
                    'meal_cost': 0,
                    'fuel_cost': 0,
                    'other_cost': 0
                })


    def action_confirm(self):
        for me in self:
            if not me.equipment_spare_id and not me.equipment_id:
                raise UserError("Please set Unit properly.")
            if not me.transporter_cost_id or not me.transporter_cost_id.distance:
                raise UserError("Please set Route code with valid distance")
            add_km = me.transporter_cost_id.distance * 2
            add_km *= 1.05
            equipment_used = me.equipment_spare_id or me.equipment_id
            if equipment_used.meter_type == "hm":
                add_km /= 20
            me.env['fsm.asset.kmhm.move'].create({
                'date': datetime.today(),
                'equipment_id': equipment_used.id,
                'meter_type': equipment_used.meter_type,
                'addition_meter': add_km,
                'kmhm_running': equipment_used.kmhm_running
            })
            equipment_used.kmhm_running += add_km
            me.state = 'confirm'
            me.transporter_task_id.action_delivery_order_confirm()
            me.transport_order_id.achieve_qty += me.netto_weight


class AssetKMHMMove(models.Model):
    _name = 'fsm.asset.kmhm.move'
    _rec_name = 'name'
    _description = 'Asset KM/HM Move'
    _order = "id desc"

    name = fields.Char(readonly=True)
    date = fields.Date("Date & Time")
    equipment_id = fields.Many2one('master_asset_maintenance', 'Unit Code', readonly=True)
    meter_type = fields.Selection(selection=[('km', 'KM'), ('hm', 'HM'), ], default='km', readonly=True)
    addition_meter = fields.Float(readonly=True)
    kmhm_running = fields.Float(readonly=True)
    hm_begin = fields.Float('HM Begin')
    hm_end = fields.Float('HM End')
    shift = fields.Selection([
        ('day', 'Day Shift'),
        ('night', 'Night Shift')
    ])


    @api.model_create_single
    def create(self, vals):
        vals['name'] = self.env.ref('fieldservice_custom.fsm_asset_kmhm_move_seq').next_by_id()
        return super(AssetKMHMMove, self).create(vals)
