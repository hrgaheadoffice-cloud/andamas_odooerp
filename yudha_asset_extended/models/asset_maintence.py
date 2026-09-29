# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import api, fields, models, _

class MasterAssetMaintenance(models.Model):
    _inherit = 'master_asset_maintenance'

    nomor_asset = fields.Char('Asset Number',index=True,default='New')
    accassets_id = fields.Many2one('account.asset',string='Assets ID',index=True)

    @api.model
    def default_get(self, fields):
        defaults = super(MasterAssetMaintenance, self).default_get(fields)
        activesid = self._context.get('active_id')
        if activesid:
            myasset = self.env['account.asset'].sudo().browse(activesid)
            if myasset:
                defaults['nama_asset'] = myasset.name
                defaults['nomor_asset'] = myasset.nomor_asset
                defaults['harga_beli']= myasset.original_value
                defaults['kat_asset'] = myasset.kat_asset.id
                defaults['accassets_id'] = myasset.id
                defaults['tgl_beli'] = myasset.purchase_date
        return defaults


