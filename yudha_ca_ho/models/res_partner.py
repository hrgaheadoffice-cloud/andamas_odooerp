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

    company_type = fields.Selection(string='Company Type',
        selection=[('person', 'Individual'), ('company', 'Company')],
        compute='_compute_company_type', inverse='_write_company_type',store=True)
    bank_tujuan = fields.Char('Bank Tujuan')
    bank_rekening = fields.Char('Bank Rekening')
    coa_tujuan = fields.Many2one('account.account',string='Account Destination')

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        for allres in res:
            isca = self._context.get('is_ca')
            if isca:
                allres.company_type = 'person'
        return res
