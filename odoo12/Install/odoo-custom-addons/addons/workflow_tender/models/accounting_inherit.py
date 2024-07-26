# -*- coding: utf-8 -*-
from odoo.exceptions import except_orm,ValidationError,UserError
from datetime import datetime

from odoo import models, fields, api, _

class AccountInherit(models.Model):
    _inherit = 'account.invoice'
    prospection_id = fields.Many2one('prospection')

    def QCM_facture(self):
        return {'type': 'ir.actions.act_window',
                'name': 'QCM Facture',
                'res_model': 'account.invoice.draft.qcm',
                'view_type': 'form',
                'view_mode': 'form',
                 'target': 'new',

                }
class AccountInvoiceQCM(models.Model):
    _name = 'account.invoice.draft.qcm'
    prospection_id = fields.Many2one('prospection',required=True)
    user_id = fields.Many2one('res.users', 'Utilisateur Courant', default=lambda self: self.env.user)
    current_date = fields.Date(string='Your string',  default=fields.Date.context_today)
    q1 = fields.Boolean('')
    q2 = fields.Boolean('')
    q3 = fields.Boolean('')
    q4 = fields.Boolean('')
    comment = fields.Text('')

    def Valider(self):
        note = 0.0
        workflow_main = {}
        ids = {}
        for rec in self:
            if rec.q1:
                note += 25.0
            if rec.q2:
                note += 25.0
            if rec.q3:
                note += 25.0
            if rec.q4:
                note += 25.0
        res = ({
            'name':'Facture',
            'state':9,
            'prospection_id':self.prospection_id.id,
            'facture':int(note),
        })
        work_id = self.env['workflow.main'].search([('prospection_id','=',self.prospection_id.id)])
        if len(work_id) == 0:
            # raise ValidationError('in if..')
            result = self.env['workflow.main'].create(res)
            ids = {
                'name': 'Facture',
                'user_id': self.env.user.id,
                'pourcentage': note,
                'comment': self.comment,
                'workflow_id': result.id,
            }
            self.env['workflow.main.line'].create(ids)
        else:
            work_id.write({'facture':int(note),'state': 6})
            ids = {
                'name': 'Facture',
                'user_id': self.env.user.id,
                'pourcentage': note,
                'comment': self.comment,
                'workflow_id': work_id.id,
            }
            self.env['workflow.main.line'].create(ids)
        id = str(self.prospection_id.id)
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': '/web#id=%s&view_type=form&model=prospection'%(id)
        }