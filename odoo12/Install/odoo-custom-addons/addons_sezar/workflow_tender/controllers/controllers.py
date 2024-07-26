# -*- coding: utf-8 -*-
from odoo import http

# class WorkflowTender(http.Controller):
#     @http.route('/workflow_tender/workflow_tender/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/workflow_tender/workflow_tender/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('workflow_tender.listing', {
#             'root': '/workflow_tender/workflow_tender',
#             'objects': http.request.env['workflow_tender.workflow_tender'].search([]),
#         })

#     @http.route('/workflow_tender/workflow_tender/objects/<model("workflow_tender.workflow_tender"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('workflow_tender.object', {
#             'object': obj
#         })