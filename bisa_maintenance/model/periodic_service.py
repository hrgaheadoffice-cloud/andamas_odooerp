from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from datetime import datetime, timedelta


class PeriodicService(models.Model):
    _name = "periodic.service"
    _rec_name = 'id'

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,default=lambda self: self.env.company)
    maintenance_type = fields.Selection(selection=[
        ('corrective', 'Unschedule'),
        ('preventive', 'Schedule'),
        ('accident', 'Accident')
    ])
    brand = fields.Many2one('brand')
    model = fields.Many2one('model', domain="[('brand', '=', brand)]")
    meter_type = fields.Selection(selection=[('hm', 'HM'), ('km', 'KM'), ])
    periodic_service = fields.Many2one('maintenance.activity')
    periodic_service_2 = fields.Many2one('maintenance.activity')
    periodic_service_3 = fields.Many2one('maintenance.activity')
    periodic_service_4 = fields.Many2one('maintenance.activity')
    periodic_service_5 = fields.Many2one('maintenance.activity')
    periodic_service_detail_ids = fields.One2many('periodic.service.detail', 'periodic_service_id', domain=[('periodic_category', '=', 'ps1')])
    periodic_service_detail_2_ids = fields.One2many('periodic.service.detail', 'periodic_service_id', domain=[('periodic_category', '=', 'ps2')])
    periodic_service_detail_3_ids = fields.One2many('periodic.service.detail', 'periodic_service_id', domain=[('periodic_category', '=', 'ps3')])
    periodic_service_detail_4_ids = fields.One2many('periodic.service.detail', 'periodic_service_id', domain=[('periodic_category', '=', 'ps4')])
    periodic_service_detail_5_ids = fields.One2many('periodic.service.detail', 'periodic_service_id', domain=[('periodic_category', '=', 'ps5')])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit')
    ], default='draft')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def action_submit(self):
        for me in self:
            me.state = 'submit'

    def action_compute(self):
        for me in self:
            # periodic service 1
            cycle = self.env['periodic.service.detail'].search([('periodic_service_id', '=', me.id), ('periodic_category', '=', 'ps1')], limit=1, order='id DESC').cycle
            if not cycle:
                cycle = int(me.periodic_service.cycle)
            else:
                if me.meter_type == 'hm':
                    cycle += 500
                else:
                    cycle += 10000

            for i in range(8):
                if me.meter_type == 'hm':
                    limit_minimum = cycle - 50
                    limit_maximum = cycle + 50
                else:
                    limit_minimum = cycle - 250
                    limit_maximum = cycle + 250

                vals = {
                    'periodic_service_id': me.id,
                    'periodic_category': 'ps1',
                    'cycle': cycle,
                    'limit_minimum': limit_minimum,
                    'limit_maximum': limit_maximum,
                    'maintenance_activity_id': me.periodic_service.id
                }
                periodic_service_detail = me.periodic_service_detail_ids.create(vals)
                if me.meter_type == 'hm':
                    cycle += 500
                else:
                    cycle += 10000

            # periodic service 2
            cycle = self.env['periodic.service.detail'].search([('periodic_service_id', '=', me.id), ('periodic_category', '=', 'ps2')], limit=1, order='id DESC').cycle
            if not cycle:
                cycle = int(me.periodic_service_2.cycle)
            else:
                if me.meter_type == 'hm':
                    cycle += 1000
                else:
                    cycle += 20000

            for i in range(4):
                if me.meter_type == 'hm':
                    limit_minimum = cycle - 50
                    limit_maximum = cycle + 50
                else:
                    limit_minimum = cycle - 250
                    limit_maximum = cycle + 250

                vals = {
                    'periodic_service_id': me.id,
                    'periodic_category': 'ps2',
                    'cycle': cycle,
                    'limit_minimum': limit_minimum,
                    'limit_maximum': limit_maximum,
                    'maintenance_activity_id': me.periodic_service_2.id
                }
                periodic_service_detail_2 = me.periodic_service_detail_ids.create(vals)
                if me.meter_type == 'hm':
                    cycle += 1000
                else:
                    cycle += 20000

            # periodic service 3
            cycle = self.env['periodic.service.detail'].search([('periodic_service_id', '=', me.id), ('periodic_category', '=', 'ps3')], limit=1, order='id DESC').cycle
            if not cycle:
                cycle = int(me.periodic_service_3.cycle)
            else:
                if me.meter_type == 'hm':
                    cycle += 2000
                else:
                    cycle += 40000

            for i in range(2):
                if me.meter_type == 'hm':
                    limit_minimum = cycle - 50
                    limit_maximum = cycle + 50
                else:
                    limit_minimum = cycle - 250
                    limit_maximum = cycle + 250

                vals = {
                    'periodic_service_id': me.id,
                    'periodic_category': 'ps3',
                    'cycle': cycle,
                    'limit_minimum': limit_minimum,
                    'limit_maximum': limit_maximum,
                    'maintenance_activity_id': me.periodic_service_3.id
                }
                periodic_service_detail_3 = me.periodic_service_detail_ids.create(vals)
                if me.meter_type == 'hm':
                    cycle += 2000
                else:
                    cycle += 40000

            # periodic service 4
            cycle = self.env['periodic.service.detail'].search([('periodic_service_id', '=', me.id), ('periodic_category', '=', 'ps4')], limit=1, order='id DESC').cycle
            if not cycle:
                cycle = int(me.periodic_service_4.cycle)
            else:
                if me.meter_type == 'hm':
                    cycle += 4000
                else:
                    cycle += 80000

            for i in range(1):
                if me.meter_type == 'hm':
                    limit_minimum = cycle - 50
                    limit_maximum = cycle + 50
                else:
                    limit_minimum = cycle - 250
                    limit_maximum = cycle + 250

                vals = {
                    'periodic_service_id': me.id,
                    'periodic_category': 'ps4',
                    'cycle': cycle,
                    'limit_minimum': limit_minimum,
                    'limit_maximum': limit_maximum,
                    'maintenance_activity_id': me.periodic_service_4.id
                }
                periodic_service_detail_4 = me.periodic_service_detail_ids.create(vals)
                if me.meter_type == 'hm':
                    cycle += 4000
                else:
                    cycle += 80000

            # periodic service 5
            cycle = self.env['periodic.service.detail'].search([('periodic_service_id', '=', me.id), ('periodic_category', '=', 'ps5')], limit=1, order='id DESC').cycle
            if not cycle:
                cycle = int(me.periodic_service_5.cycle)
            else:
                if me.meter_type == 'hm':
                    cycle += 4000
                else:
                    cycle += 80000

            for i in range(1):
                if me.meter_type == 'hm':
                    limit_minimum = cycle - 50
                    limit_maximum = cycle + 50
                else:
                    limit_minimum = cycle - 250
                    limit_maximum = cycle + 250

                vals = {
                    'periodic_service_id': me.id,
                    'periodic_category': 'ps5',
                    'cycle': cycle,
                    'limit_minimum': limit_minimum,
                    'limit_maximum': limit_maximum,
                    'maintenance_activity_id': me.periodic_service_5.id
                }
                periodic_service_detail_5 = me.periodic_service_detail_ids.create(vals)
                if me.meter_type == 'hm':
                    cycle += 4000
                else:
                    cycle += 80000


class PeriodicServiceDetail(models.Model):
    _name = "periodic.service.detail"
    _rec_name = "id"

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    periodic_service_id = fields.Many2one(comodel_name='periodic.service', ondelete='cascade')
    brand = fields.Many2one('brand', related='periodic_service_id.brand', store=1)
    model = fields.Many2one('model', related='periodic_service_id.model', store=1)
    periodic_category = fields.Selection([
        ('ps1', 'PS1'),
        ('ps2', 'PS2'),
        ('ps3', 'PS3'),
        ('ps4', 'PS4'),
        ('ps5', 'PS5'),
    ])
    cycle = fields.Float()
    limit_minimum = fields.Float()
    limit_maximum = fields.Float()
    work_order_ids = fields.One2many('work.order', 'periodic_service_detail_id')
    maintenance_activity_id = fields.Many2one('maintenance.activity')
    company_id = fields.Many2one('res.company', related='periodic_service_id.company_id')


class PeriodicServiceDetail2(models.Model):
    _name = "periodic.service.detail2"

    periodic_service_id = fields.Many2one(comodel_name='periodic.service')
    cycle = fields.Float()
    limit_minimum = fields.Float()
    limit_maximum = fields.Float()


class PeriodicServiceDetail3(models.Model):
    _name = "periodic.service.detail3"

    periodic_service_id = fields.Many2one(comodel_name='periodic.service')
    cycle = fields.Float()
    limit_minimum = fields.Float()
    limit_maximum = fields.Float()


class PeriodicServiceDetail4(models.Model):
    _name = "periodic.service.detail4"

    periodic_service_id = fields.Many2one(comodel_name='periodic.service')
    cycle = fields.Float()
    limit_minimum = fields.Float()
    limit_maximum = fields.Float()
