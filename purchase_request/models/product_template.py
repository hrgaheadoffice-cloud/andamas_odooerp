# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models, exceptions, _
from odoo.http import request, route
from odoo.addons import decimal_precision as dp
from lxml import etree
from odoo.exceptions import ValidationError, UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_request = fields.Boolean(
        help="Check this box to generate Purchase Request instead of "
        "generating Requests For Quotation from procurement.",
        company_dependent=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProductTemplate, self).create(vals_list)
        res._check_default_code()
        return res

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        for item in self:
            item._check_default_code()
        return res

    def _check_default_code(self):
        for item in self:
            check_default_code = self.env['product.template'].search([('default_code','=',item.default_code),('company_id','=',item.company_id.id)])
            if len(check_default_code) > 1:
                raise ValidationError('A Code Part Number exists with this Code . Code Part Number must be unique!')