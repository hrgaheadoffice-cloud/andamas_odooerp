# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    partner_id = fields.Many2one('res.partner', readonly=True, tracking=True,
        states={'draft': [('readonly', False)]},
        check_company=True,
        string='Partner', change_default=True, ondelete='restrict',
        domain=lambda self: self.compute_partner_id(),
        store=True)

    @api.model
    def compute_partner_id(self):
        domain = []
        ctx = self.env.context
        if ctx.get('default_move_type'):
            if ctx['default_move_type'] in ('out_invoice', 'out_refund', 'out_receipt'):
                domain = [('customer_rank', '>', 0)]
            elif ctx['default_move_type'] in ('in_invoice', 'in_refund', 'in_receipt'):
                domain = [('supplier_rank', '>', 0)]
        return domain
