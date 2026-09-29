from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from datetime import datetime, timedelta


class Brand(models.Model):
    _name = "brand"

    name = fields.Char()
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)


class Model(models.Model):
    _name = "model"

    name = fields.Char()
    brand = fields.Many2one('brand')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)



