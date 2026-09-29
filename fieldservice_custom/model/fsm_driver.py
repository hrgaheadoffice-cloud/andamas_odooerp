from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class FSMDriver(models.Model):
    _name = 'fsm.driver'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Many2one('hr.employee')
    nip = fields.Char('NIP')
    equipment_id = fields.Many2one('master_asset_maintenance', 'Unit Code')
    phone = fields.Char()
    spv_id = fields.Many2one('hr.employee', 'Supervisor')
    status = fields.Char()
    address = fields.Char()
    disc_status = fields.Char('Disciplinary Status')

    extra_info_ids = fields.One2many('extra.info', 'fsm_driver_id')
    disciplinary_history_ids = fields.One2many('disciplinary.action', 'fsm_driver_id')
    transporter_history_ids = fields.One2many('transporter.history', 'fsm_driver_id')
    cost_advance_ids = fields.One2many(
        comodel_name="fsm.cost.advance",
        inverse_name="driver_id",
        string="Cost Advance",
        required=False,
    )
    cost_advance_difference_ids = fields.One2many(
        comodel_name="fsm.cost.advance",
        inverse_name="driver_id",
        string="Cost Advance",
        required=False,
        domain=[
            ('is_difference_claimed', '=', False),
            ('difference_to_be_paid', '>', 0)
        ]
    )
    cost_advance_to_deduct = fields.Float(compute='compute_cost_advance')
    cost_advance_accumulate_payroll = fields.Float(compute='compute_cost_advance')
    cost_advance_all_difference = fields.Float(compute='compute_cost_advance')

    @api.onchange('name')
    def compute_nip(self):
        self.nip = self.name.barcode if self.name.barcode else ""

    def compute_cost_advance(self):
        for me in self:
            cost_advance = me.cost_advance_ids.filtered(lambda x: not x.is_difference_claimed and x.difference_to_be_paid >  0)
            cost_advance_to_deduct = sum([x.difference_to_be_paid for x in cost_advance if x.cost_difference_policy == "deduct_next_advance"])
            cost_advance_accumulate_payroll = sum([x.difference_to_be_paid for x in cost_advance if x.cost_difference_policy == "accumulate_in_payroll"])

            me.update({
                'cost_advance_accumulate_payroll': cost_advance_accumulate_payroll,
                'cost_advance_to_deduct': cost_advance_to_deduct,
                'cost_advance_all_difference': cost_advance_accumulate_payroll + cost_advance_to_deduct
            })
        return


class ExtraInfo(models.Model):
    _name = 'extra.info'

    name = fields.Char()
    expire_date = fields.Datetime()
    status = fields.Char()

    fsm_driver_id = fields.Many2one('fsm.driver')


class DisciplinaryAction(models.Model):
    _inherit = 'disciplinary.action'

    fsm_driver_id = fields.Many2one('fsm.driver')


class TransporterHistory(models.Model):
    _name = 'transporter.history'

    name = fields.Char()
    route_code = fields.Char()
    distance = fields.Char()
    duration = fields.Char()
    netto = fields.Float('Netto Weight')

    fsm_driver_id = fields.Many2one('fsm.driver')
