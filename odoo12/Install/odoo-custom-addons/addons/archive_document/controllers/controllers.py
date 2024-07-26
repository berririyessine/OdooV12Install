# -*- coding: utf-8 -*-
from odoo import http

# class ArchiveDocument(http.Controller):
#     @http.route('/archive_document/archive_document/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/archive_document/archive_document/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('archive_document.listing', {
#             'root': '/archive_document/archive_document',
#             'objects': http.request.env['archive_document.archive_document'].search([]),
#         })

#     @http.route('/archive_document/archive_document/objects/<model("archive_document.archive_document"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('archive_document.object', {
#             'object': obj
#         })