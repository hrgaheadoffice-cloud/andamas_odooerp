from odoo import _, api, fields, models
from odoo.exceptions import ValidationError,UserError


class MasterAssetMaintenance(models.Model):
    _inherit = "master_asset_maintenance"

    fuel_cons_id = fields.One2many('fuel.consumption', 'equipment_id')

