import json
import logging
from xmlrpc import client

from odoo import http, SUPERUSER_ID, models, fields
from odoo.http import Response, request
from odoo.tools import config, date_utils
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class WIPProject(http.Controller):
    model_name = 'wip.project'

    @http.route('/wip-project', auth='public', type='json', methods=['POST'], csrf=False)
    def create(self, **kwargs):
        logging.info(kwargs)

        partner_id = request.env['res.partner'].sudo().search(['|', ('customer_code', '=', kwargs['Buyer']), ('vendor_code', '=', kwargs['Buyer'])], limit=1).id

        data = {
            'name': kwargs['DespatchOrderNumber'],
            'contract_number': kwargs['SalesContract'],
            'product_calory': kwargs['ContractProduct'],
            'term': kwargs['TermOfShipment'],
            'cargo_nomination': kwargs['Transport'],
            'partner_id': partner_id
        }
        resource = request.env[self.model_name].sudo().create(data)
        return resource.id

