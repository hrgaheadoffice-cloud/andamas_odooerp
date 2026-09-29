# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import api, fields, models, _

class AccountAsset(models.Model):
    _inherit  = 'account.asset'


    nomor_asset = fields.Char('Asset Number',index=True,default='New',readonly=True)

    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        self_comp = self.with_context(company_id=company_id)
        if vals.get('nomor_asset', 'New') == 'New':
            vals['nomor_asset'] = self_comp.env['ir.sequence'].next_by_code('account.asset.number') or '/'
        res = super(AccountAsset, self_comp).create(vals)
        return res

