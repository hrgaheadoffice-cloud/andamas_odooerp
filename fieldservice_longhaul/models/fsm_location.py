
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class FSMLocation(models.Model):
    _inherit = 'fsm.location'

    route_code = fields.Char(string='Route Code')
    location_code = fields.Char(string='Location Code')
    location_name = fields.Char(string='Location Name')
    loading_location = fields.Char(string='Loading Location')
    unloading_location = fields.Char(string='Unloading Location')
    location_category = fields.Many2one('your.category.model', string='Location Category')