from odoo import http
from odoo.http import request


class Session(http.Controller):

    @http.route('/web/session/get_session_info', type='json', auth="none")
    def get_session_info(self):
        request.session.check_security()
        request.uid = request.session.uid
        session_info = request.env['ir.http'].session_info()
        session_info['session_id'] = request.httprequest.headers.get('Cookie').split('=')[1]
        return session_info

