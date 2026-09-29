# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo import api, fields, models

import math


class msi_sales_quotations(models.Model):
    _inherit = 'sale.order.line'


    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="The analytic account related to a sales order.", copy=False, oldname='project_id')




class msi_sales_order(models.Model):
    _inherit = 'sale.order'

    nomer_sso = fields.Char('SSO', readonly=True)
    desc_sso = fields.Char('SSO Description')

    nomer_sso_temp = fields.Char(string='sso temp')


    @api.onchange('name','order_line','partner_id')
    def onchange_name1(self):
        if self.name:
          partner=''
          baris1=''
          for rec in self:
            if rec.partner_id.ref:
               partner = str(rec.partner_id.ref).upper()
            else:
               partner = 'PART'
           
            if rec.order_line:
               for kode in rec.order_line:
                  if kode.product_id.default_code:
                     baris1 = str(kode.product_id.default_code).upper()
                  else:
                     baris1 = 'NOA'
            else:               
               baris1 = 'NOA'
                      
            rec.nomer_sso_temp = partner + '-' + baris1 + '-'




    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'confirmation_date': fields.Datetime.now()
        })
        self._action_confirm()
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()


        if self.analytic_account_id:
           self.analytic_account_id.unlink()
        analytic_id = self.env['account.analytic.account'].create({
                'name': str(self.nomer_sso),
                'code': str(self.nomer_sso),
                'company_id': self.company_id.id,
                'partner_id': self.partner_id.id,
        })


        #analitik = self.env['account.analytic.account'].search([['name','=',self.nomer_sso]], limit=1)
        for list in self.order_line:
            if not list.analytic_account_id:
               if list.product_id.product_analytic:
                  analytic = self.env['account.analytic.account'].create({
                      'name': str(self.nomer_sso) + ' / ' + str(list.product_id.product_analytic),
                      'code': str(self.nomer_sso),
                      'company_id': self.company_id.id,
                      'partner_id': self.partner_id.id,
                  })
                  list.analytic_account_id = analytic
               else:
                  analytic = self.env['account.analytic.account'].create({
                      'name': str(self.nomer_sso) + ' / NOA',
                      'code': str(self.nomer_sso),
                      'company_id': self.company_id.id,
                      'partner_id': self.partner_id.id,
                  })
                  list.analytic_account_id = analytic            
        return True



    @api.model
    def create(self, vals):


        #vals['nomer_sso'] = self.env['ir.sequence'].next_by_code('sale.order') or _('New')

        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('sale.order') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or _('New')

        vals['nomer_sso'] = vals.get('nomer_sso_temp') + vals.get('name')

        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
        result = super(msi_sales_order, self).create(vals)
        return result