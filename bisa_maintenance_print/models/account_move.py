from odoo import api, fields, models
from odoo.addons.bisa_maintenance_print.utils.number_utils import terbilang


class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_terbilang = fields.Char(compute='compute_amount_terbilang')

    def compute_amount_terbilang(self):
        for me in self:
            text = terbilang(me.amount_total, me.currency_id.name, 'id')
            me.amount_terbilang = text
        return
