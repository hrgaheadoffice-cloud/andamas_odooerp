# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"


    comodity_id = fields.Many2one('product.comodity',string='Comodity',index=True,ondelete='cascade')