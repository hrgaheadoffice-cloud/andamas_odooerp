from odoo import api, fields, models, _
import requests
from odoo.http import request
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    project_code = fields.Many2one('wip.project')
    sales_type = fields.Char()
    product_line_ids = fields.One2many('product.line', 'invoice_id')
    sm_integration = fields.Boolean()
    volume = fields.Float()


class ProductLine(models.Model):
    _name = 'product.line'

    product_id = fields.Many2one('product.product')
    quantity = fields.Float()
    price_unit = fields.Float()
    invoice_id = fields.Many2one('account.move')

