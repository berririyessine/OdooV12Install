# -*- coding: utf-8 -*-
from odoo import http

# class Solve-it-interne(http.Controller):
#     @http.route('/solve-it-interne/solve-it-interne/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/solve-it-interne/solve-it-interne/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('solve-it-interne.listing', {
#             'root': '/solve-it-interne/solve-it-interne',
#             'objects': http.request.env['solve-it-interne.solve-it-interne'].search([]),
#         })

#     @http.route('/solve-it-interne/solve-it-interne/objects/<model("solve-it-interne.solve-it-interne"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('solve-it-interne.object', {
#             'object': obj
#         })