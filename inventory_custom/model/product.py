from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
