from odoo import api, fields, models, _
from odoo.api import depends
from odoo.exceptions import UserError, AccessError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo.service.server import start


class GenerateBudgetPlanAsset(models.Model):
    _name = "generate.budget.plan.asset"

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    month = fields.Selection([
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ], required=1)
    year = fields.Char(required=1)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('generate', 'Generated'),
    ], default='draft')
    name = fields.Char(compute='compute_name')

    budget_plan_asset_ids = fields.One2many('budget.plan.asset', 'generate_budget_plan_id')

    def compute_name(self):
        self.name = '%s %s' % (dict(self._fields['month'].selection).get(self.month), self.year)

    def action_generate(self):
        for me in self:
            str_date = '%s%s%s' % ('1', me.month, me.year)
            start_date = datetime.strptime(str_date, '%d%m%Y').date()
            end_date = (start_date + relativedelta(months=1)) - relativedelta(days=1)
            periodic_calculation_plan_ids = self.env['periodic.calculation.plan'].search([('date', '>=', start_date), ('date', '<=', end_date)])
            for plan in periodic_calculation_plan_ids:
                part_service_line = []
                oil_service_line = []

                for sparepart in plan.maintenance_activity_id.sparepart_ids:
                    if 'LUBRICAN' in sparepart.product_id.categ_id.display_name:
                        oil_service_line.append((0, 0, {
                            'product_id': sparepart.product_id.id,
                            'qty': sparepart.product_uom_qty,
                            'uom': sparepart.product_uom.id,
                        }))
                    else:
                        part_service_line.append((0, 0, {
                            'product_id': sparepart.product_id.id,
                            'qty': sparepart.product_uom_qty,
                            'uom': sparepart.product_uom.id,
                        }))

                vals = {
                    'generate_budget_plan_id': me.id,
                    'periodic_calculation_plan_id': plan.id,
                    'part_service_ids': part_service_line,
                    'oil_service_ids': oil_service_line,
                }
                budget_plan_asset_id = self.env['budget.plan.asset'].create(vals)

            me.state = 'generate'

    def action_update(self):
        for me in self:
            me.budget_plan_asset_ids = [(5,)]
            str_date = '%s%s%s' % ('1', me.month, me.year)
            start_date = datetime.strptime(str_date, '%d%m%Y').date()
            end_date = (start_date + relativedelta(months=1)) - relativedelta(days=1)
            periodic_calculation_plan_ids = self.env['periodic.calculation.plan'].search([('date', '>=', start_date), ('date', '<=', end_date)])
            for plan in periodic_calculation_plan_ids:
                part_service_line = []
                oil_service_line = []

                for sparepart in plan.maintenance_activity_id.sparepart_ids:
                    if 'LUBRICAN' in sparepart.product_id.categ_id.display_name:
                        oil_service_line.append((0, 0, {
                            'product_id': sparepart.product_id.id,
                            'qty': sparepart.product_uom_qty,
                            'uom': sparepart.product_uom.id,
                        }))
                    else:
                        part_service_line.append((0, 0, {
                            'product_id': sparepart.product_id.id,
                            'qty': sparepart.product_uom_qty,
                            'uom': sparepart.product_uom.id,
                        }))

                vals = {
                    'generate_budget_plan_id': me.id,
                    'periodic_calculation_plan_id': plan.id,
                    'part_service_ids': part_service_line,
                    'oil_service_ids': oil_service_line,
                }
                budget_plan_asset_id = self.env['budget.plan.asset'].create(vals)

            me.state = 'generate'


class BudgetPlanAsset(models.Model):
    _name = "budget.plan.asset"
    _rec_name = 'periodic_calculation_plan_id'

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    generate_budget_plan_id = fields.Many2one('generate.budget.plan.asset')
    periodic_calculation_plan_id = fields.Many2one('periodic.calculation.plan')
    period_plan_id = fields.Many2one(related='periodic_calculation_plan_id.period_plan_id')
    unit_code = fields.Many2one(related='periodic_calculation_plan_id.unit_code', store=1)
    brand = fields.Many2one(related='periodic_calculation_plan_id.unit_code.brand')
    model = fields.Many2one(related='periodic_calculation_plan_id.unit_code.model', store=1)
    part_service_cost = fields.Float(compute='hitung_total')
    oil_cost = fields.Float(compute='hitung_total')
    total_cost = fields.Float(compute='hitung_total')

    part_service_ids = fields.One2many('budget.plan.part.service', 'budget_plan_asset_id')
    oil_service_ids = fields.One2many('budget.plan.oil.service', 'budget_plan_asset_id')

    @api.depends('part_service_ids','oil_service_ids')
    def hitung_total(self):
        for me in self:
            part_service_cost = oil_cost = 0.0
            for line in me.part_service_ids:
                part_service_cost += line.total_price
            for line in me.oil_service_ids:
                oil_cost += line.total_price
            total_cost = part_service_cost + oil_cost
            me.update({
                'part_service_cost': part_service_cost,
                'oil_cost': oil_cost,
                'total_cost': total_cost,
            })


class BudgetPlanPartService(models.Model):
    _name = "budget.plan.part.service"

    budget_plan_asset_id = fields.Many2one('budget.plan.asset')
    product_id = fields.Many2one('product.product')
    product_name = fields.Char(related='product_id.name')
    qty = fields.Float()
    uom = fields.Many2one('uom.uom', 'UOM')
    price = fields.Float(related='product_id.standard_price')
    total_price = fields.Float(compute='compute_total_price')

    def compute_total_price(self):
        for me in self:
            me.total_price = me.price * me.qty


class BudgetPlanOilService(models.Model):
    _name = "budget.plan.oil.service"

    budget_plan_asset_id = fields.Many2one('budget.plan.asset')
    product_id = fields.Many2one('product.product')
    product_name = fields.Char(related='product_id.name')
    qty = fields.Float()
    uom = fields.Many2one('uom.uom', 'UOM')
    price = fields.Float(related='product_id.standard_price')
    total_price = fields.Float(compute='compute_total_price')

    def compute_total_price(self):
        for me in self:
            me.total_price = me.price * me.qty





