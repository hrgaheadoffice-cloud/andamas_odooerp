# -*- coding : utf-8 -*-
#######################################################################################################################
#      Author    => Albertus Restiyanto Pramayudha                                                                    #
#      email     => xabre0010@gmail.com                                                                               #
#      linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/                              #
#      youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA                                          #
#######################################################################################################################

from odoo import exceptions,api, fields, models, tools, _




class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    # domain_product = fields.Many2many('product.product','purchase_order_line_rel',string='Domain Product',compute='category_expense',store=False)
    state = fields.Selection(related='order_id.state')
    proc_group_id = fields.Many2one(
        comodel_name="tbl_proc_group",
        string="Procurement Category",
        copy=True,
        related='order_id.proc_group_id',
        index=True,
    )
    # product_id = fields.Many2one(
    #     comodel_name="product.product",
    #     string="Product",
    #     domain="[('id','in',domain_product)]",
    #     track_visibility="onchange",
    #     required=True,
    # )

    @api.onchange('order_id','proc_group_id','state')
    def _onchanges_product(self):
        for alldata in self:
            if alldata.proc_group_id:
                if 'ISSUE REQUISITION' in alldata.proc_group_id.name:
                    print('ini issue')
                    return {'domain': {'product_id': [('categ_id','child_of',9)]}}
                elif 'PURCHASE REQUISITION' in alldata.proc_group_id.name:
                    print('ini purchase')
                    return {'domain': {'product_id': [('categ_id', 'child_of', 13)]}}
