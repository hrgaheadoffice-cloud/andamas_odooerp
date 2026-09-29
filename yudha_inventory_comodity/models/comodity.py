# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import fields, models, api

class InventoryComodity(models.Model):
    _name = "product.comodity"
    _description = 'Product Comodity'


    name = fields.Char('Name',index=True,required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
