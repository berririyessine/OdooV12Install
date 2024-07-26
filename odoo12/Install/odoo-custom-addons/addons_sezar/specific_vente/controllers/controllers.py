# -*- coding: utf-8 -*-
from odoo import http

# class SpecificVente(http.Controller):
#     @http.route('/specific_vente/specific_vente/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/specific_vente/specific_vente/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('specific_vente.listing', {
#             'root': '/specific_vente/specific_vente',
#             'objects': http.request.env['specific_vente.specific_vente'].search([]),
#         })

#     @http.route('/specific_vente/specific_vente/objects/<model("specific_vente.specific_vente"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('specific_vente.object', {
#             'object': obj
#         })