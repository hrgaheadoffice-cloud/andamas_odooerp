# -*- coding : utf-8 -*-
#################################################################################
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
#################################################################################


from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero, float_round

class AccountAsset(models.Model):
    _inherit  = 'account.asset'


    @api.depends('state', 'maintenance_ids')
    def hitung_total_asset(self):
        for alldata in self:
            mymaintenannce = self.env['master_asset_maintenance'].sudo().search([('accassets_id','=', alldata.id or alldata._origin.id)])
            alldata.assetmain_count = len(mymaintenannce) or 0

    purchase_date = fields.Date('Purchase Date', index=True)
    kat_asset = fields.Many2one('asset_maintenance_kategori', string="Asset Type")
    assetmain_count = fields.Integer('Asset Maintenance Count',compute='hitung_total_asset',store=False)
    maintenance_ids = fields.One2many('master_asset_maintenance', 'accassets_id', string='Asset Maintence Count', copy=True)
    journal_asset_id = fields.Many2one('account.move', string="Journal Asset")

    @api.model
    def create(self, vals):
        return super(AccountAsset, self).create(vals)

    def create_move_line(self):
        line_ids = []
        amount = 0.0
        amount_currency = 0.0
        account_in_id = False
        for allrec in self:
            for i in allrec.original_move_line_ids:
                account_in_id = i.account_id.id
            company_currency = allrec.company_id.currency_id
            prec = company_currency.decimal_places
            move_line_src = {
                'name': allrec.nomor_asset,
                'account_id':  account_in_id,
                'credit': 0.0,
                'debit': allrec.original_value if float_compare(allrec.original_value, 0.0, precision_digits=prec) > 0 else 0.0,
                'amount_currency': allrec.original_value,
                'currency_id': allrec.currency_id.id,
               
            }
            move_line_dst = {
                'name': allrec.nomor_asset,
                'debit': 0.0,
                'credit': allrec.original_value if float_compare(allrec.original_value, 0.0, precision_digits=prec) > 0 else 0.0,
                'account_id':  allrec.model_id.account_asset_id.id,
                'date_maturity': allrec.acquisition_date,
                'amount_currency': allrec.original_value,
                'currency_id':  allrec.currency_id.id,
               
            }
            line_ids.append((0, 0, move_line_dst))
            line_ids.append((0,0,move_line_src))
        return line_ids

    def create_journal_asset(self):
        myline = self.create_move_line()
        move_vals = {
            'ref': self.nomor_asset,
            'date': fields.Datetime.now(),
            'journal_id': self.journal_id.id,
            'line_ids': myline,
            'is_noi_ho': False,
            'is_sundry': False,
            'name': '/',
            'move_type': 'entry',
            'invoice_date': self.acquisition_date,
            'currency_id': self.currency_id.id,
        }
        mybill = self.env['account.move'].with_context(default_is_noi_ho=False,default_is_sundry_site=False).create(move_vals)
        mybill.action_post()
        self.journal_asset_id = mybill.id

    def validate(self):
        res = super(AccountAsset, self).validate()
        for rec in self:
            rec.create_journal_asset()

    def action_view_assets_maintenance(self, invoices=False):
        if not invoices:
            self.sudo()._read(['maintenance_ids'])
            invoices = self.maintenance_ids

        result = self.env['ir.actions.act_window']._for_xml_id('yudha_asset_extended.action_master_account_asset_maintenance')
        if len(invoices) >= 1:
            result['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 0:
            res = self.env.ref('bisa_maintenance.master_asset_mt_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = invoices.id
        else:
            result = {'type': 'ir.actions.act_window_close'}

        return result

    def buat_asset_maintenance(self):
        ctx = {
            'default_asset': self.id or self._origin.id,
            'default_aset_type': 'res_branch',
            'default_nama_asset': self.name,
            'default_asset_number': self.nomor_asset,
            'default_original_value': self.original_value,
            'default_route': False,
        }
        return {
            'type': 'ir.actions.act_window',
            'name': _('Register Maintenance'),
            'res_model': 'master_asset_maintenance',
            'view_id': self.env.ref('bisa_maintenance.master_asset_mt_form').id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
            'views': [[False, 'form']]
        }

