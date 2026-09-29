# -*- coding: utf-8 -*-
# from odoo import http


# class Wip(http.Controller):
#     @http.route('/wip/wip/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wip/wip/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wip.listing', {
#             'root': '/wip/wip',
#             'objects': http.request.env['wip.wip'].search([]),
#         })

#     @http.route('/wip/wip/objects/<model("wip.wip"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wip.object', {
#             'object': obj
#         })
