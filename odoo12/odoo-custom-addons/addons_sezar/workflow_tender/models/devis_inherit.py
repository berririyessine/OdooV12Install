# -*- coding: utf-8 -*-
from odoo.exceptions import except_orm,ValidationError,UserError
from datetime import datetime

from odoo import models, fields, api, _

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    prospection_id = fields.Many2one('prospection')

    def QCM_devis(self):
        return {'type': 'ir.actions.act_window',
                'name': 'QCM Devis',
                'res_model': 'sale.order.draft.qcm',
                'view_type': 'form',
                'view_mode': 'form',
                 'target': 'new',

                }
    def QCM_devis_send(self):
        return {'type': 'ir.actions.act_window',
                'name': 'QCM Devis Envoyé',
                'res_model': 'sale.order.send.qcm',
                'view_type': 'form',
                'view_mode': 'form',
                 'target': 'new',

                }
    def QCM_BnCommande(self):
        return {'type': 'ir.actions.act_window',
                'name': 'QCM Bn Commande',
                'res_model': 'sale.order.bn.cm.qcm',
                'view_type': 'form',
                'view_mode': 'form',
                 'target': 'new',

                }
class SaleOrderQCMDevis(models.Model):
    _name = 'sale.order.draft.qcm'
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
            'name':'Devis',
            'state':6,
            'prospection_id':self.prospection_id.id,
            'devis':int(note),
        })
        work_id = self.env['workflow.main'].search([('prospection_id','=',self.prospection_id.id)])
        if len(work_id) == 0:
            # raise ValidationError('in if..')
            result = self.env['workflow.main'].create(res)
            ids = {
                'name': 'Devis',
                'user_id': self.env.user.id,
                'pourcentage': note,
                'comment': self.comment,
                'workflow_id': result.id,
            }
            self.env['workflow.main.line'].create(ids)
        else:
            work_id.write({'devis':int(note),'state': 6})
            ids = {
                'name': 'Devis',
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
class SaleOrderQCMDevisSent(models.Model):
    _name = 'sale.order.send.qcm'
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
            'name':'Devis Envoyé',
            'state':7,
            'prospection_id':self.prospection_id.id,
            'devis_envoye':int(note),
        })
        work_id = self.env['workflow.main'].search([('prospection_id','=',self.prospection_id.id)])
        if len(work_id) == 0:
            # raise ValidationError('in if..')
            result = self.env['workflow.main'].create(res)
            ids = {
                'name': 'Devis Envoyé',
                'user_id': self.env.user.id,
                'pourcentage': note,
                'comment': self.comment,
                'workflow_id': result.id,
            }
            self.env['workflow.main.line'].create(ids)
        else:
            work_id.write({'devis_envoye':int(note),'state': 7})
            ids = {
                'name': 'Devis Envoyé',
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
class SaleOrderQCMBnCommande(models.Model):
    _name = 'sale.order.bn.cm.qcm'
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
            'name':'Bon Commande',
            'state':8,
            'prospection_id':self.prospection_id.id,
            'commande':int(note),
        })
        work_id = self.env['workflow.main'].search([('prospection_id','=',self.prospection_id.id)])
        if len(work_id) == 0:
            # raise ValidationError('in if..')
            result = self.env['workflow.main'].create(res)
            ids = {
                'name': 'Bon Commande',
                'user_id': self.env.user.id,
                'pourcentage': note,
                'comment': self.comment,
                'workflow_id': result.id,
            }
            self.env['workflow.main.line'].create(ids)
        else:
            work_id.write({'commande':int(note),'state': 8})
            ids = {
                'name': 'Bon Commande',
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
