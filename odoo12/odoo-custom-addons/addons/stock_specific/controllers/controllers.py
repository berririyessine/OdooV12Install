# -*- coding: utf-8 -*-
from odoo import http

# class StockSpecific(http.Controller):
#     @http.route('/stock_specific/stock_specific/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_specific/stock_specific/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_specific.listing', {
#             'root': '/stock_specific/stock_specific',
#             'objects': http.request.env['stock_specific.stock_specific'].search([]),
#         })

#     @http.route('/stock_specific/stock_specific/objects/<model("stock_specific.stock_specific"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_specific.object', {
#             'object': obj
#         })