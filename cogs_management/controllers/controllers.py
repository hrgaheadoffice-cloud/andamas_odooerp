# -*- coding: utf-8 -*-
# from odoo import http


# class CogsManagement(http.Controller):
#     @http.route('/cogs_management/cogs_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cogs_management/cogs_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('cogs_management.listing', {
#             'root': '/cogs_management/cogs_management',
#             'objects': http.request.env['cogs_management.cogs_management'].search([]),
#         })

#     @http.route('/cogs_management/cogs_management/objects/<model("cogs_management.cogs_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cogs_management.object', {
#             'object': obj
#         })
