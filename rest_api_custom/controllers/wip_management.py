import json
import logging
from xmlrpc import client

from odoo import http, SUPERUSER_ID, models, fields
from odoo.http import Response, request
from odoo.tools import config, date_utils
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class WIPManagement(http.Controller):
    model_name = 'wip.management'

    @http.route('/wip-management', auth='public', type='json', methods=['POST'], csrf=False)
    def create(self, **kwargs):
        logging.info(kwargs)

        partner_id = request.env['res.partner'].sudo().search(['|', ('customer_code', '=', kwargs['ContractorCode']), ('vendor_code', '=', kwargs['ContractorCode'])], limit=1).id
        project_id = request.env['wip.project'].sudo().search([('name', '=', kwargs['ProjectCode'])], limit=1).id
        do_category_id = request.env['do.category'].sudo().search([('name', '=', kwargs['KategoriWIP'])], limit=1).id
        # product_tmpl_id = request.env['product.template'].sudo().search([('name', 'like', kwargs['ProductCode'])], limit=1).id
        # product_id = request.env['product.product'].sudo().search([('product_tmpl_id', '=', product_tmpl_id)], limit=1).id
        company_id = request.env['res.company'].sudo().search([('inisial_pt', '=', 'AGE')], limit=1).id

        data = {
            'document_date': kwargs['DateTimeOut'],
            'do_category_id': do_category_id,
            'do_code': kwargs['NoTransaksi'],
            'vendor_id': partner_id,
            'project_code': project_id,
            'product_id': kwargs['ProductCode'],
            'wip_amount': kwargs['Price'],
            'qty': kwargs['Quantity'],
            'company_id': company_id
        }
        resource = request.env[self.model_name].sudo().create(data)
        resource.with_company(company_id).action_post()
        return resource.id

