# -*- coding: utf-8 -*-
from odoo.exceptions import except_orm,ValidationError,UserError
from datetime import datetime

from odoo import models, fields, api, _

class PreparationConfig(models.Model):
    _name = 'preparation.config'
    name = fields.Char('')
    prospection_id = fields.Many2one('prospection')
    state = fields.Selection([(1,'Prepa.Configuration et Calculs'),(2,'Preparation devis'),
                              (3,'Preparation Doc Administratifs'),(4,'Demande de Caution'),
                              (5,'Valider Prix'),(6,'Validation Dossiertechnique'), ] ,default=1)
    partner_id = fields.Many2one('res.partner', track_visibility='onchange', default=lambda self: self.env['res.partner'].search([], limit=1).id)
    date = fields.Date(track_visibility='onchange',  default=fields.Date.context_today)
    valider_devis = fields.Boolean('')
    valider_doc = fields.Boolean('')
    valider_caution = fields.Boolean('')
    valider_prix = fields.Boolean('')
    terminer_proc = fields.Boolean('')
    def devis_add(self):
        self.valider_devis = True
        self.state = 2
        doc_id = self.env['sale.order'].search([('prospection_id','=',self.prospection_id.id)])
        doc_id_find = doc_id.search([],limit=1)
        if len(doc_id)==0:
            return {
                'name': ('Devis'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order',
            }
        else:
            return {
                'name': ('Devis'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': doc_id.id,
                'res_model': 'sale.order',

                }
    def doc_administratif(self):
        self.valider_doc = True
        self.state = 3
    def get_caution(self):
        self.valider_caution = True
        self.state = 4

    def validate_prix(self):
        self.valider_prix = True
        self.state = 5

    def terminate(self):
        self.terminer_proc = True
        self.state = 6
    def QCM_prepa_config(self):
        return {'type': 'ir.actions.act_window',
                'name': 'QCM Préparation et Configuration',
                'res_model': 'qcm.prepa.config',
                'view_type': 'form',
                'view_mode': 'form',
                 'target': 'new',

                }
class QcmPrepaConfig(models.Model):
    _name = "qcm.prepa.config"

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
            'name':'Préparation et Configuration',
            'state':5,
            'prospection_id':self.prospection_id.id,
            'prepa_config':int(note),
        })
        work_id = self.env['workflow.main'].search([('prospection_id','=',self.prospection_id.id)])
        if len(work_id) == 0:
            # raise ValidationError('in if..')
            result = self.env['workflow.main'].create(res)
            ids = {
                'name': 'Préparation et Configuration',
                'user_id': self.env.user.id,
                'pourcentage': note,
                'comment': self.comment,
                'workflow_id': result.id,
            }
            self.env['workflow.main.line'].create(ids)
        else:
            work_id.write({'prepa_config':int(note),'state': 5})
            ids = {
                'name': 'Préparation et Configuration',
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
