from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class FSMLocations(models.Model):
    _name = 'fsm.locations'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    code = fields.Char("Location Code")
    name = fields.Char("Location Name")
    category = fields.Selection([('loading', 'Loading Location'), ('unloading', 'Unloading Location'), ('both', 'Both')], 'Location Category')
