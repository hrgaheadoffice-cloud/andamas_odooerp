from odoo import models, fields, api

class FSMRouteDayRoute(models.Model):
    _inherit = 'fsm.route.dayroute'

    # Fields on the left side
    created_by = fields.Many2one('res.users', string='Created by', default=lambda self: self.env.user, readonly=True)
    date_time = fields.Datetime(string='Date & Time', default=fields.Datetime.now, readonly=True)
    shift = fields.Selection([('day', 'Day'), ('night', 'Night')], string='Shift')
    driver = fields.Many2one('res.partner', string='Driver')
    unit_code = fields.Many2one('your.unit.model', string='Unit Code', readonly=True)
    unit_spare = fields.Many2one('your.unit.spare.model', string='Unit Spare')

    # Fields on the right side
    freight_contract = fields.Many2one('your.freight.contract.model', string='Freight Contract')
    route_code = fields.Char(string='Route Code')
    loading_location = fields.Char(string='Loading Location')
    unloading_location = fields.Char(string='Unloading Location')
    hauling_cost = fields.Float(string='Hauling Cost')

    # Renamed tabs
    unit_status = fields.Char(string='Unit Status')
    hse_status = fields.Char(string='HSE Status')
    operation_status = fields.Char(string='Operation Status')

    loading_permit = fields.Char(string='Loading Permit', compute='_compute_loading_permit', store=True)

    @api.depends('date_time')
    def _compute_loading_permit(self):
        for record in self:
            if record.date_time:
                date_str = fields.Datetime.from_string(record.date_time).strftime('%Y%m%d')
                sequence = self.env['ir.sequence'].next_by_code('your.sequence.model') or '0001'
                record.loading_permit = f'SIB.{date_str}.{sequence.zfill(4)}'
            else:
                record.loading_permit = False