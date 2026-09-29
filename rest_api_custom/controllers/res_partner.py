import json
import logging
from xmlrpc import client

from odoo import http, SUPERUSER_ID, models, fields
from odoo.http import Response, request
from odoo.tools import config, date_utils

_logger = logging.getLogger(__name__)


class ResPartner(http.Controller):
    model_name = 'res.partner'

    @http.route('/partner', type='http', auth='none', methods=["GET"], csrf=False)
    def get_all(self, *args, **post):
        cr = request.cr
        fields = [
            "code",
            "name",
            "street",
            "street2"
        ]
        data = request.env(cr, SUPERUSER_ID)[self.model_name].search_read([('customer_rank', '>', '0')], fields)
        headers = {'content-type': 'application/json'}
        return Response(json.dumps(data, default=date_utils.json_default), headers=headers)

