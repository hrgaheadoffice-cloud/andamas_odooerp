# -*- coding : utf-8 -*-
#######################################################################################################################
#      Author    => Albertus Restiyanto Pramayudha                                                                    #
#      email     => xabre0010@gmail.com                                                                               #
#      linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/                              #
#      youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA                                          #
#######################################################################################################################

from odoo import exceptions,api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError, ValidationError

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.model
    def _department_get(self):
        myhr = self.env['hr.employee'].search([('user_id','=',self.env.user.id)],limit=1)
        if myhr:
            return myhr.department_id.id
        else:
            raise UserError(_("Anda belum terdaftar di department. Hubungi Administrator"))

    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department",
        track_visibility="onchange",
        default=_department_get,
    )


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    # def category_expense(self):
    #     myctx = self._context.get('proc_group_id')
    #     print('ctxt ', myctx)
    #     return [('categ_id','child_of',9)]

    # domain_product = fields.Many2many('product.product','settelment_line_rel',string='Domain Product',compute='category_expense',store=False)
    state = fields.Selection(related='request_id.state')
    proc_group_id = fields.Many2one(
        comodel_name="tbl_proc_group",
        string="Procurement Category",
        copy=True,
        related='request_id.proc_group_id',
        index=True,
    )
    # product_id = fields.Many2one(
    #     comodel_name="product.product",
    #     string="Product",
    #     domain=category_expense,
    #     track_visibility="onchange",
    #     required=True,
    # )

    @api.onchange('request_id','proc_group_id','state')
    def _onchanges_product(self):
        for alldata in self:
            if alldata.proc_group_id:
                if 'ISSUE REQUISITION' in alldata.proc_group_id.name:
                    print('ini issue')
                    # product_category = self.env['product.category'].search([('name', 'ilike', 'ISSUE REQUESITION')])
                    return {'domain': {'product_id': [('categ_id','child_of',9)]}}
                elif 'PURCHASE REQUISITION' in alldata.proc_group_id.name:
                    print('ini purchase')
#                     product_category = self.env['product.category'].search([('name', 'ilike', 'PURCHASE REQUESITION')])
                    return {'domain': {'product_id': [('categ_id','child_of',13)]}}
    # @api.depends('request_id','proc_group_id','state')
    # def category_expense1(self):
    #     for alldata in self:
    #         pids = []
    #         # if alldata.proc_group_id:
    #         if alldata.proc_group_id.name =='ISSUE REQUISITION':
    #             pcateg = self.env['product.category'].sudo().search([('name','=','ISSUE REQUISITION'),('parent_id','=',False)],limit=1)
    #             mycateg = self.env['product.category'].sudo().search(['|',('name','=','ISSUE REQUISITION'),('parent_id','=',pcateg.id)])
    #             for allcateg in mycateg:
    #                 myprod = self.env['product.product'].sudo().search([('categ_id','=',allcateg.id)])
    #                 for allprod in myprod:
    #                     pids.append(allprod.id)
    #         elif alldata.proc_group_id.name =='PURCHASE REQUEST':
    #             pcateg = self.env['product.category'].sudo().search(
    #                 [('name', '=', 'PURCHASE REQUEST'), ('parent_id', '=', False)], limit=1)
    #             mycateg = self.env['product.category'].sudo().search(['|',('name','=','PURCHASE REQUEST'),('parent_id', '=', pcateg.id)])
    #             for allcateg in mycateg:
    #                 myprod = self.env['product.product'].sudo().search([('categ_id', '=', allcateg.id)])
    #                 for allprod in myprod:
    #                     pids.append(allprod.id)
    #         myprods = self.env['product.product'].sudo().search([('id','in',pids)])
    #         alldata.domain_product =[(6,0,myprods.ids)]