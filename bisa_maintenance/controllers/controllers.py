# import requests
# import odoo
 
from odoo import http, models, fields, _
from odoo.http import request
import json


class OdooController(http.Controller):

    @http.route('/api/v1/tbl_mnt_timesheet_equipment', type='json', auth='public')
    def index(self):
        # Kode untuk menangani permintaan API Anda
        return {"message": "Hello, API!"}

class InsertDoc(http.Controller):
    @http.route('/timesheet/put', auth='public', website=True, methods=['POST'], type = 'http', csrf=False)
    def put_data(self,  **kwargs):
        return "Halooo"
        #db = http.request.env['tbl_rfid']
        # try:
        #     return request.env['tbl_mnt_timesheet_engineer'].sudo().create({
        #                'tanggal': kwargs['tanggal'],
        #                'shift': kwargs['shift'],
        #                'kode_operator': kwargs['kode_operator'],
        #                })


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