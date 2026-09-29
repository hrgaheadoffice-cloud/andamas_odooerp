import json
import logging
from xmlrpc import client

from odoo import http, SUPERUSER_ID, models, fields
from odoo.http import Response, request
from odoo.tools import config, date_utils
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class FuelConsumption(http.Controller):
    model_name = 'fuel.consumption'

    @http.route('/fuel-consumption', auth='public', type='json', methods=['POST'], csrf=False)
    def create(self, **kwargs):
        logging.info(kwargs)
        equipment_id = request.env['master_asset_maintenance'].sudo().search([('equipment_id', '=', kwargs['cn_unit_id'])])
        fuel_source = request.env['fuel.source'].sudo().search([('name', '=', kwargs['source'])])
        company_id = request.env['res.company'].sudo().search([('inisial_pt', '=', kwargs['business_unit_id'])])
        product_id = request.env['product.template'].with_company(company_id).sudo().search([('default_code', '=', 'B-35')])
        date = datetime.strptime(kwargs['date_time'], '%Y-%m-%d %H:%M:%S') - timedelta(hours=7)
        product_price = product_id.standard_price
        if not (not kwargs.get('price')):
            product_price = kwargs['price']
        begin_balance = fuel_source.quantity

        data = {
            'created_by': kwargs['created_by'],
            'date': date,
            'shift': kwargs['shift_name'],
            'equipment_id': equipment_id.id,
            'hm': kwargs['hour_meter'],
            'operation': kwargs['activity'],
            'driver': kwargs['driver'],
            'fuel_source': fuel_source.id,
            'fuel_man': kwargs['fuel_man'],
            'product_id': product_id.id,
            'fuel_qty': kwargs['fuel_consumption'],
            'company_id': company_id.id,
            'no_ticket': kwargs['no_ticket'],
            'product_price': product_price,
            'begin_balance': begin_balance,
            'total_price': product_price * kwargs['fuel_consumption']
        }
        resource = request.env[self.model_name].sudo().create(data)
        resource.with_company(company_id).action_submit()
        # resource.with_company(company_id).fuel_consumption_journal()
        return resource.id

