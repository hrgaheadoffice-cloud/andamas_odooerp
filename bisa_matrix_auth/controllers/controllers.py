import odoo
 
from odoo import http, models, fields, _
from odoo.http import request
import json
 
class ViewDoc(http.Controller):
    @http.route('/rfid', auth='public', website=True)
    def view_doc(self, **kwargs):
        #return "Halooo"
        data = http.request.env['tbl_rfid'].search([])
        return http.request.render('bisa_rfid.doc_id', {
            'isidata':data,
            })

    @http.route('/view_rfid/<int:view_id>', auth='public', website=True)
    def view_doc_detail(self, view_id, **kwargs):
        #return "Halooo"
        data = http.request.env['tabel_rfid'].search([])
        return http.request.render('bisa_rfid.doc_id', {
            'isidata':data,
            })

class InsertDoc(http.Controller):
    @http.route('/insert_rfid/', auth='public', website=True, methods=['POST'], type = 'http', csrf=False)
    def view_doc_detail(self,  **kwargs):
        #return "Halooo"
        #db = http.request.env['tbl_rfid']
        try:
            return request.env['tbl_rfid'].sudo().create({
                       'name': kwargs['lot'],
                       'lokasi': kwargs['gudang'],
                       })
        except:
            a=1