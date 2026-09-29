import json
import logging
from xmlrpc import client

from odoo import http, SUPERUSER_ID, models, fields
from odoo.http import Response, request
from odoo.tools import config, date_utils

_logger = logging.getLogger(__name__)


class FSMDeliveryOrder(http.Controller):
    model_name = 'fsm.delivery.order'

    @http.route('/driver-perform', auth='public', type='json', methods=['POST'], csrf=False)
    def create(self, **kwargs):
        logging.info(kwargs)
        equipment_id = request.env['master_asset_maintenance'].sudo().search([('nama_asset', '=', kwargs['cn_unit'])]).id
        driver_id = request.env['fsm.driver'].sudo().search([('nip', '=', kwargs['operator_nik'])]).id

        data_dp = {
            'created_by': request.env.uid,
            'date': kwargs['timesheet_date'],
            'nip': kwargs['operator_nik'],
            'driver_id': driver_id,
            'shift': kwargs['shift_name'],
            'equipment_id': equipment_id,
            'ready_hour': kwargs['ready_hour'],
            'general_hour': kwargs['general_hour'],
            'delay_hour': kwargs['delay_hour'],
            'idle_hour': kwargs['idle_hour'],
            'breakdown_hours': kwargs['breakdown_hour'],
        }
        resource_dp = request.env[self.model_name].sudo().create(data_dp)

        data_tm = {
            'date': kwargs['timesheet_date'],
            'equipment_id': equipment_id,
            'shift': kwargs['shift_name'],
            'addition_meter': kwargs['hour_end'] - kwargs['hour_start'],
            'kmhm_running': kwargs['hour_end'],
            'hm_begin': kwargs['hour_start'],
            'hm_end': kwargs['hour_end'],
            'meter_type': 'hm'
        }
        resource_tm = request.env['fsm.asset.kmhm.move'].sudo().create(data_tm)
        return resource_dp.id, resource_tm.id

