# -*- coding: utf-8 -*-
from odoo import http

# class ReportInterne(http.Controller):
#     @http.route('/report_interne/report_interne/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/report_interne/report_interne/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('report_interne.listing', {
#             'root': '/report_interne/report_interne',
#             'objects': http.request.env['report_interne.report_interne'].search([]),
#         })

#     @http.route('/report_interne/report_interne/objects/<model("report_interne.report_interne"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('report_interne.object', {
#             'object': obj
#         })