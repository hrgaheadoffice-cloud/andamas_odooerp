from odoo import api, fields, models
from odoo.addons.bisa_maintenance_print.utils.number_utils import terbilang


class NewModule(models.Model):
    _inherit = 'sale.order'

    amount_terbilang = fields.Char(compute='compute_amount_terbilang')

    def compute_amount_terbilang(self):
        for me in self:
            text = terbilang(me.amount_total, me.currency_id.name, 'id')
            me.amount_terbilang = text
        return
