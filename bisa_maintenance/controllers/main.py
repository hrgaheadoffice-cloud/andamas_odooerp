# import requests
# import odoo
 
from odoo import http, models, fields, _
from odoo.http import request, Response
import json
import logging


class OdooController1(http.Controller):

    @http.route('/teknisi/tambah', auth='public', methods=['POST'], type = 'json', csrf=False)
    def tambah_data(self,  **kwargs):
        return "Halooo List"
        # http.request.env['tbl_mnt_timesheet_engineer'].sudo().create({'tanggal':kwargs['tanggal']})

        # return kwargs

    @http.route('/teknisi/list_data', auth='public', methods=['GET'], type = 'json', csrf=False)
    def list_data(self,  **kwargs):
        return "Halooo List"
        # data = http.request.env['tbl_mnt_timesheet_engineer'].sudo().search([])

        # technicians = []

        # for record in data:
        #     technicians.append({
        #         'tanggal': record.tanggal,
        #         'shift': record.shift,
        #         'kode_operator': record.kode_operator,
        #     })
        # # print (data)
        # return technicians

    # @http.route('/equipment/tambah', auth='public', methods=['POST'], type = 'json', csrf=False)
    # def tambah_data(self,  **kwargs):
    #     #return "Halooo List"
    #     http.request.env['tbl_mnt_timesheet_equipment'].sudo().create({'tanggal':kwargs['tanggal']})

    #     return kwargs

    # @http.route('/equipment/list', auth='public', methods=['GET'], type = 'json', csrf=False)
    # def list_data(self,  **kwargs):
    #     # return "Halooo List"
    #     data = http.request.env['tbl_mnt_timesheet_equipment'].sudo().search([])

    #     equipments = []

    #     for record in data:
    #         equipments.append({
    #             'tanggal': record.tanggal,
    #             'kode_unit': record.kode_unit,
    #             'shift': record.shift,
    #             'kode_operator': record.kode_operator,
    #         })
    #     # print (data)
    #     return equipments


    # @http.route('/timesheet/list', auth='public', methods=['POST','GET'], type = 'http', csrf=False)
    # def put_data(self,  **kwargs):
    #     return "Halooo"




    # @http.route('/timesheet/list', auth='public', methods=['POST','GET'], type = 'http', csrf=False)
    # def put_data(self,  **kwargs):
    #     return "Halooo"
        # data = http.request.env['tbl_rfid'].search([])
        # teknisi = []
        # for tek in data:
        #     teknisi.append({
        #         'tanggal' : data.tanggal,
        #         'shift' : data.shift,
        #         'kode_operator' : data.kode_operator,
        #         })
#         return http.request.render('bisa_rfid.doc_id', {
#             'isidata':data,
#             })


# import requests

# url = "http://89.116.231.190:8069/api/login"

# payload = ""
# headers = {
#   'login': 'admin',
#   'password': 'Rmb2023!',
#   'db': 'odoo_api',
#   'Content-Type': 'text/plain'
# }

# response = requests.request("GET", url, headers=headers, data=payload)

# print(response.text)

# url = "http://89.116.231.190:8069/api/login/token_api_key"

# payload = ""
# headers = {
#   'api_key': 'a09814fea30ceb798c61e614dc7b24e2941409c9',
#   'db': 'RMB_DEV',
#   'Content-Type': 'text/plain'
# }

# response = requests.request("POST", url, headers=headers, data=payload)

# print(response.text)


# class OdooController(http.Controller):
#     @http.route('/maintenance/time_sheet', auth='public', website=True)
#     def index(self, **kw):
#         times_sheet = http.request.env['tbl_mnt_timesheet_equipment'].search([])
#         for time in times_sheet:
#             print(time['kode_unit'])
#         return "Data Acc"

 
# class ViewDoc(http.Controller):
#     @http.route('/rfid', auth='public', website=True)
#     def view_doc(self, **kwargs):
#         #return "Halooo"
#         data = http.request.env['tbl_rfid'].search([])
#         return http.request.render('bisa_rfid.doc_id', {
#             'isidata':data,
#             })

#     @http.route('/view_rfid/<int:view_id>', auth='public', website=True)
#     def view_doc_detail(self, view_id, **kwargs):
#         #return "Halooo"
#         data = http.request.env['tabel_rfid'].search([])
#         return http.request.render('bisa_rfid.doc_id', {
#             'isidata':data,
#             })

# class InsertDoc(http.Controller):
#     @http.route('/insert_rfid/', auth='public', website=True, methods=['POST'], type = 'http', csrf=False)
#     def view_doc_detail(self,  **kwargs):
#         #return "Halooo"
#         #db = http.request.env['tbl_rfid']
#         try:
#             return request.env['tbl_rfid'].sudo().create({
#                        'name': kwargs['lot'],
#                        'lokasi': kwargs['gudang'],
#                        })
#         except:
            # a=1


class tbl_mnt_timesheet_equipment(http.Controller):
    model_name = 'tbl_mnt_timesheet_equipment'

    @http.route('/equipment/tambah_data', auth='public', methods=['POST'], type='json', csrf=False)
    def tambah_data(self, **kwargs):
        logging.info(kwargs)

        equipment = http.request.env['master_asset_maintenance'].search([('equipment_id', '=', kwargs['cn_unit'])])

        obj = http.request.env['tbl_mnt_timesheet_equipment'].search([('sm_id', '=', kwargs['id'])])

        company_id = request.env['res.company'].sudo().search([('inisial_pt', '=', kwargs['business_unit_id'])])

        if obj:
            obj.sudo().update({
                'tanggal': kwargs['timesheet_date'],
                'name': equipment.id,
                'meter_type': equipment.meter_type,
                'shift': kwargs['shift_code'].upper(),
                'hm_awal': kwargs['hour_meter_awal'],
                'hm_akhir': kwargs['hour_meter_akhir'],
                'stndby_hr': kwargs['standby'],
                'activity_hour': kwargs['aktifitas'],
                'general_hour': kwargs['general_hour'],
                'idle_hour': kwargs['idle'],
                'breakdown_hour': kwargs['breakdown'],
                'ewh': kwargs['aktifitas'] + kwargs['general_hour'],
                'mohh': kwargs['mohh'],
            })
        else:
            http.request.env['tbl_mnt_timesheet_equipment'].sudo().create({
                'tanggal': kwargs['timesheet_date'],
                'name': equipment.id,
                'meter_type': equipment.meter_type,
                'shift': kwargs['shift_code'].upper(),
                'hm_awal': kwargs['hour_meter_awal'],
                'hm_akhir': kwargs['hour_meter_akhir'],
                'stndby_hr': kwargs['standby'],
                'activity_hour': kwargs['aktifitas'],
                'general_hour': kwargs['general_hour'],
                'idle_hour': kwargs['idle'],
                'breakdown_hour': kwargs['breakdown'],
                'ewh': kwargs['aktifitas'] + kwargs['general_hour'],
                'mohh': kwargs['mohh'],
                'sm_id': kwargs['id'],
                'company_id': company_id.id
            })

        return kwargs

    @http.route('/equipment/<resource_id>', auth='public', type='json', methods=['PATCH'], csrf=False)
    def update(self, resource_id, **kwargs):
        logging.info(kwargs)
        timesheet_id = http.request.env['tbl_mnt_timesheet_equipment'].sudo().search([('sm_id', '=', resource_id)]).id
        resource = request.env[self.model_name].browse(timesheet_id)
        resource.update(kwargs)
        return resource.id

    @http.route('/equipment/<resource_id>', auth='public', type='http', methods=['DELETE'], csrf=False)
    def remove(self, resource_id):
        timesheet_id = http.request.env['tbl_mnt_timesheet_equipment'].sudo().search([('sm_id', '=', resource_id)]).id
        resource = request.env[self.model_name].browse(timesheet_id)
        resource.unlink()
        headers = {'content-type': 'application/json'}
        return Response(json.dumps({'result': resource_id}), headers=headers)
