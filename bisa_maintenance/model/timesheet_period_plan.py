from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from dateutil.relativedelta import relativedelta

import math

class TimesheetPeriodPlan(models.Model):
    _name = "timesheet.period.plan"
    _rec_name = 'unit_code'

    name = fields.Char()
    unit_code = fields.Many2one('master_asset_maintenance', 'Unit Code')
    equipment_id = fields.Char(related='unit_code.equipment_id', string='Equipment ID', readonly=1)
    asset_name = fields.Many2one(related='unit_code.kat_asset', string='Asset Name', readonly=1)
    meter_type = fields.Selection(related='unit_code.meter_type', readonly=1)
    kmhm_running = fields.Float(related='unit_code.kmhm_running', string="KM/HM Running", readonly=1)
    avg_ewh_ewd = fields.Float('Average EWH/EWD', readonly=1)
    forecast = fields.Char('Forecast 1')
    forecast_2 = fields.Char('Forecast 2')
    forecast_3 = fields.Char('Forecast 3')
    forecast_4 = fields.Char('Forecast 4')

    periodic_calculation_plan_ids = fields.One2many('periodic.calculation.plan', 'period_plan_id')
    # timesheet_unit_plan_ids = fields.One2many('timesheet.unit.plan', 'period_plan_id')
    # forecast_calculation_plan_ids = fields.One2many('forecast.calculation.plan', 'period_plan_id')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.onchange('unit_code')
    def onchange_unit_code(self):
        timesheet_ids = self.env['tbl_mnt_timesheet_equipment'].search([('name', '=', self.unit_code.id), ('tanggal', '>=', fields.Date.today() - relativedelta(days=30))])
        ewh = sum(timesheet_ids.mapped('ewh')) / len(timesheet_ids) if len(timesheet_ids) > 0 else 1
        self.avg_ewh_ewd = ewh

    def periodic_calculation(self):
        for me in self:
            maintenance_activity_ids = self.env['activity.asset.list'].search([('unit_code', '=', me.unit_code.id)]).mapped('maintenance_activity_id.id')
            periodic_service_detail_ids = self.env['periodic.service.detail'].search([('maintenance_activity_id', 'in', maintenance_activity_ids)], order='cycle asc')
            for periodic in periodic_service_detail_ids:
                periodic_calculation = self.env['periodic.calculation.plan'].search([('period_plan_id.unit_code', '=', me.unit_code.id), ('cycle', '=', periodic.cycle)])
                if not periodic_calculation:
                    self.env['periodic.calculation.plan'].create({
                        'maintenance_activity_id': periodic.maintenance_activity_id.id,
                        'cycle': periodic.cycle,
                        'period_plan_id': me.id,
                        'unit_code': me.unit_code.id
                    })

            timesheet = self.env['tbl_mnt_timesheet_equipment'].search([('name', '=', me.unit_code.id)], limit=1, order='id desc')
            if timesheet:
                date = timesheet.tanggal
                timesheet_ids = self.env['tbl_mnt_timesheet_equipment'].search([('name', '=', me.unit_code.id), ('tanggal', '>=', fields.Date.today() - relativedelta(days=30))])
                ewh = sum(timesheet_ids.mapped('ewh')) / len(timesheet_ids) if len(timesheet_ids) > 0 else 1
                me.avg_ewh_ewd = ewh
                periodic_calculate_ids = me.periodic_calculation_plan_ids.filtered(lambda e: e.cycle > me.kmhm_running)
                for line in periodic_calculate_ids:
                    day_calc = math.floor((line.cycle - me.kmhm_running) / ewh) if ewh > 0 else 0
                    if not line.wo_id:
                        line.date = date + relativedelta(days=day_calc)

                me.forecast = periodic_calculate_ids[0].name
                me.forecast_2 = periodic_calculate_ids[1].name
                me.forecast_3 = periodic_calculate_ids[2].name
                me.forecast_4 = periodic_calculate_ids[3].name

class PeriodicCalculationPlan(models.Model):
    _name = "periodic.calculation.plan"

    date = fields.Date()
    maintenance_activity_id = fields.Many2one('maintenance.activity', 'Period Name')
    cycle = fields.Float()
    wo_id = fields.Many2one('work.order', 'WO Number')
    kmhm_actual = fields.Float('HM/KM Actual')
    name = fields.Char(compute='_compute_name')

    period_plan_id = fields.Many2one('timesheet.period.plan')
    unit_code = fields.Many2one('master_asset_maintenance')

    def name_get(self):
        res = []
        for rec in self:
            if self.env.context.get('cycle_name'):
                name = str(int(rec.cycle))
            else:
                name = rec.name
            res.append((rec.id, name))
        return res

    @api.depends('date')
    def _compute_name(self):
        for me in self:
            me.name = '%s - %s' % (me.date.strftime('%m/%d/%Y'), me.maintenance_activity_id.name) if me.date else me.maintenance_activity_id.name


# class TimesheetUnitPlan(models.Model):
#     _name = "timesheet.unit.plan"
#
#     date = fields.Date()
#     shift = fields.Char()
#     start_hm = fields.Float('Start KM/HM')
#     end_hm = fields.Float('End KM/HM')
#     ewh = fields.Float('EWH/EWD')
#
#     period_plan_id = fields.Many2one('timesheet.period.plan')


# class ForecastCalculationPlan(models.Model):
#     _name = "forecast.calculation.plan"
#
#     periodic_category = fields.Char()
#     cycle = fields.Float()
#     date = fields.Date()
#
#     period_plan_id = fields.Many2one('timesheet.period.plan')


