# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, ValidationError

class CashRequestConfig(models.Model):
    _name = "cr.config"
    _description = 'Cash Request Config'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    approved_finance1 = fields.Many2one('res.users', string='Verified By', tracking=3, ondelete="restrict", )
    approved_finance2 = fields.Many2one('res.users', string='Verified By', tracking=3, ondelete="restrict", )
    approved_finance3 = fields.Many2one('res.users', string='Verified By', tracking=3, ondelete="restrict", )
    approved_finance4 = fields.Many2one('res.users', string='Verified By', tracking=3, ondelete="restrict", )
    approved_finance5 = fields.Many2one('res.users', string='Verified By', tracking=3, ondelete="restrict", )
    approved_finance6 = fields.Many2one('res.users', string='Verified By', tracking=3, ondelete="restrict", )
    is_default = fields.Boolean('Set Default',default=False)