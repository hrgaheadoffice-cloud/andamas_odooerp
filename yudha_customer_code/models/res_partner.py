# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################

from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'


    is_supplier = fields.Boolean(compute='_cek_supplier',store=False)
    vendor_code = fields.Char('Vendor Code',index=True)
    customer_code = fields.Char('Customer Code',index=True)
    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Payable",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
        help="This account will be used instead of the default one as the payable account for the current partner",
        required=False)
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Receivable",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
        help="This account will be used instead of the default one as the receivable account for the current partner",
        required=False)


    @api.depends('company_name','name','active_lang_count','is_company')
    def _cek_supplier(self):
        for alldata in self:
            is_supplier = self.env.context.get('res_partner_search_mode')
            print('is supplier ', is_supplier)
            if is_supplier == 'customer':
                alldata.is_supplier = False
            else:
                alldata.is_supplier = True