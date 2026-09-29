from datetime import datetime
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    name_transporter_order = fields.Char(
        string='No. Transporter Order',
        copy=False,
        readonly=True,
        default=lambda self: self._generate_transporter_order(),
    )

    @api.model
    def _generate_transporter_order(self):
        date_today = datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT)
        last_order = self.search([], order="name_transporter_order desc", limit=1)
        last_number = (
            int(last_order.name_transporter_order[-4:]) + 1
            if last_order and last_order.name_transporter_order
            else 1
        )
        return f"SPK.{date_today}.{str(last_number).zfill(4)}"

    no_sales_order = fields.Char(
        string='No. Sales Order',
    )
    created_by = fields.Many2one(
        'res.users',
        string='Created by',
    )
    date_time = fields.Datetime(
        string='Date & Time',
        default=fields.Datetime.now,
        readonly=True,
    )
    transporter_type = fields.Selection(
        selection=[('internal', 'Internal Bomba'), ('external', 'External Bomba')],
        string='Transporter Type',
    )
    transporter_cost = fields.Float(
        string='Transporter Cost',
    )
    freight_product = fields.Selection(
        selection=[('coal', 'Coal'), ('palm', 'Palm'), ('soil', 'Soil')],
        string='Freight Product',
    )
    route_code = fields.Many2one(
        'fsm.route',
        string='Route Code',
    )
    loading_location = fields.Many2one(
        'fsm.location',
        string='Loading Location',
    )
    unloading_location = fields.Many2one(
        'fsm.location',
        string='Unloading Location',
    )
    total_quantity = fields.Float(
        string='Total Quantity (MT)',
    )
