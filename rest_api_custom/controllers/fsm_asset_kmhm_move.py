import json
import logging
from xmlrpc import client

from odoo import http, SUPERUSER_ID, models, fields
from odoo.http import Response, request
from odoo.tools import config, date_utils

_logger = logging.getLogger(__name__)


class AssetKMHMMove(http.Controller):
    model_name = 'fsm.asset.kmhm.move'

    @http.route('/asset-kmhm-move', auth='public', type='json', methods=['POST'], csrf=False)
    def create(self, **kwargs):
        equipment_id = request.env['master_asset_maintenance'].sudo().search([('nama_asset', '=', kwargs['cn_unit'])]).id

        data = {
            'date': kwargs['timesheet_date'],
            'equipment_id': equipment_id,
            'shift': kwargs['shift_name'],
            'addition_meter': kwargs['hour_end'] + kwargs['hour_start'],
            'kmhm_running': kwargs['hour_end'],
            'hm_begin': kwargs['hour_start'],
            'hm_end': kwargs['hour_end'],
        }
        resource = request.env[self.model_name].sudo().create(data)
        return resource.id

