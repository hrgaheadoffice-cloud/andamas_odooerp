from odoo import api, fields, models
from odoo.addons.bisa_maintenance_print.utils.number_utils import terbilang


class NewModule(models.Model):
    _inherit = 'work.order'

    def get_legend(self, res_id):
        # Search for the attachment
        attachment = self.env['ir.attachment'].search([('name', 'like', 'dt-legend')], limit=1)

        # Return the image data if found, else return None
        return attachment.datas if attachment else None

    def get_legend2(self, res_id):
        # Search for the attachment
        attachment = self.env['ir.attachment'].search([('name', 'like', 'legend-detail')], limit=1)

        # Return the image data if found, else return None
        return attachment.datas if attachment else None