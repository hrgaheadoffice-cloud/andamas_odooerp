import json
import logging
from xmlrpc import client

from odoo import http, SUPERUSER_ID, models, fields
from odoo.http import Response, request
from odoo.tools import config, date_utils

_logger = logging.getLogger(__name__)


class AccountTax(http.Controller):
    model_name = 'account.tax'

    @http.route('/tax', type='http', auth='none', methods=["GET"], csrf=False)
    def get_all(self, *args, **post):
        cr = request.cr
        fields = [
            "name",
            "amount"
        ]
        data = request.env(cr, SUPERUSER_ID)[self.model_name].search_read([('type_tax_use', '=', 'sale')], fields)
        headers = {'content-type': 'application/json'}
        return Response(json.dumps(data, default=date_utils.json_default), headers=headers)

