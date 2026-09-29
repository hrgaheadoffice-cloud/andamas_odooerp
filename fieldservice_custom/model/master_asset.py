from odoo import api, fields, models


class MasterAssetMaintenance(models.Model):
    _inherit = "master_asset_maintenance"

    history_transporter_lines = fields.One2many('fsm.delivery.order','equipment_id', 'History Transporter')
