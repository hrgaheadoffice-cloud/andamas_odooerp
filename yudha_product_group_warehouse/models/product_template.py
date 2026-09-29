# -*- coding : utf-8 -*-
#######################################################################################################################
#      Author    => Albertus Restiyanto Pramayudha                                                                    #
#      email     => xabre0010@gmail.com                                                                               #
#      linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/                              #
#      youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA                                          #
#######################################################################################################################
from odoo import _, api, fields, models, SUPERUSER_ID

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_product_warehouse(self):
        for alldata in self:
            myprod = self.env['product.product'].sudo().search([('product_tmpl_id','=',alldata.id)])
            mycari = self.env['stock.picking'].sudo().search([('product_id','=',myprod.id)])
            for allcari in mycari:
                alldata.warehouse_id = allcari.picking_type_id.warehouse_id.id

    warehouse_id = fields.Many2one(
        'stock.warehouse', 'Warehouse', ondelete='cascade', compute='_get_product_warehouse',
        check_company=True,store=True,readonly=False)
