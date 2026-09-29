from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    service_periodic_schedule = fields.Char(default="5000")
    km_min_warning = fields.Char(default="500")
    km_max_warning = fields.Char(default="300")
    hm_min_warning = fields.Char(default="25")
    hm_max_warning = fields.Char(default="15")

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('service_periodic_schedule', self.service_periodic_schedule)
        param.set_param('km_min_warning', self.km_min_warning)
        param.set_param('km_max_warning', self.km_max_warning)
        param.set_param('hm_min_warning', self.hm_min_warning)
        param.set_param('hm_max_warning', self.hm_max_warning)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        service_periodic_schedule = params.get_param('service_periodic_schedule', "5000")
        km_min_warning = params.get_param('km_min_warning', "500")
        km_max_warning = params.get_param('km_max_warning', "300")
        hm_min_warning = params.get_param('hm_min_warning', "25")
        hm_max_warning = params.get_param('hm_max_warning', "15")
        res.update({
            'service_periodic_schedule': service_periodic_schedule,
            'km_min_warning': km_min_warning,
            'km_max_warning': km_max_warning,
            'hm_min_warning': hm_min_warning,
            'hm_max_warning': hm_max_warning,
        })
        return res
