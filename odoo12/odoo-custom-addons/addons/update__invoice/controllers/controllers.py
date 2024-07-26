# -*- coding: utf-8 -*-
from odoo import http

# class UpdateInvoiceSmart2DoTech(http.Controller):
#     @http.route('/update__invoice__smart2_do_tech/update__invoice__smart2_do_tech/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/update__invoice__smart2_do_tech/update__invoice__smart2_do_tech/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('update__invoice__smart2_do_tech.listing', {
#             'root': '/update__invoice__smart2_do_tech/update__invoice__smart2_do_tech',
#             'objects': http.request.env['update__invoice__smart2_do_tech.update__invoice__smart2_do_tech'].search([]),
#         })

#     @http.route('/update__invoice__smart2_do_tech/update__invoice__smart2_do_tech/objects/<model("update__invoice__smart2_do_tech.update__invoice__smart2_do_tech"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('update__invoice__smart2_do_tech.object', {
#             'object': obj
#         })