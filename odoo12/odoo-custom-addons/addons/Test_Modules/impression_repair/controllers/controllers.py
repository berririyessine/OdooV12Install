# -*- coding: utf-8 -*-
from odoo import http

# class ImpressionGmt(http.Controller):
#     @http.route('/impression_gmt/impression_gmt/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/impression_gmt/impression_gmt/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('impression_gmt.listing', {
#             'root': '/impression_gmt/impression_gmt',
#             'objects': http.request.env['impression_gmt.impression_gmt'].search([]),
#         })

#     @http.route('/impression_gmt/impression_gmt/objects/<model("impression_gmt.impression_gmt"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('impression_gmt.object', {
#             'object': obj
#         })