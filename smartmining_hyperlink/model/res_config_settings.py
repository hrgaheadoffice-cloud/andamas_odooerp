from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    smartmining_link = fields.Char()

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('smartmining_link', self.smartmining_link)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        smartmining_link = params.get_param('smartmining_link')
        res.update({
            'smartmining_link': smartmining_link
        })
        return res
