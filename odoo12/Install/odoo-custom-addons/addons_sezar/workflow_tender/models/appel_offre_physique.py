# -*- coding: utf-8 -*-
from odoo.exceptions import except_orm,ValidationError,UserError
from datetime import datetime

from odoo import models, fields, api, _
class AppelOffrePhysique(models.Model):
    _name = "offre.physique"
    name = fields.Char('Référence',required=True)
    date_start = fields.Date('Date Début',  default=fields.Date.context_today,required=True)
    date_end = fields.Date('Date Fin')
    caution = fields.Float('Caution')
    partner_id = fields.Many2one('res.partner', track_visibility='onchange')
    piece_joint = fields.Many2many('ir.attachment', 'offre_pyhsique_attachments_rel', 'offre_pyhsique', 'attachment_id', 'Piece Joint')
    prospection_id = fields.Many2one('prospection')

    def QCM_pyhsique(self):
        doc_id = self.env['qcm.offre.physique'].search([])
        return {'type': 'ir.actions.act_window',
                'name': 'QCM Physique',
                'res_model': 'qcm.offre.physique',

                'view_type': 'form',
                'view_mode': 'form',
                 'target': 'new',
                'context': {'default_qcm_id': self.id},
                }

class QcmOffreTechnique(models.Model):
    _name = "qcm.offre.physique"

    prospection_id = fields.Many2one('prospection',required=True)
    qcm_id = fields.Many2one('offre.physique')
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
        self.prospection_id.purcent_physique = 0.0
        for rec in self:
            if rec.q1:
                note += 25.0
            if rec.q2:
                note += 25.0
            if rec.q3:
                note += 25.0
            if rec.q4:
                note += 25.0
        rec.prospection_id.write({'purcent_physique':note,'purcent_physique_done':True})
        res = ({
            'name':'Offre Physique',
            'state':3,
            'prospection_id':self.prospection_id.id,
            'appel_offre':int(note),
        })
        work_id = self.env['workflow.main'].search([('prospection_id','=',self.prospection_id.id)])
        if len(work_id) == 0:
            # raise ValidationError('in if..')
            result = self.env['workflow.main'].create(res)
            ids = {
                'name': 'Offre Physique',
                'user_id': self.env.user.id,
                'pourcentage': note,
                'comment': self.comment,
                'workflow_id': result.id,
            }
            self.env['workflow.main.line'].create(ids)
        # raise ValidationError('before else..')
        else:
            # raise /ValidationError('in else..')
            work_id.write({'appel_offre':int(note),'state': 3})
            ids = {
                'name': 'Offre Physique',
                'user_id': self.env.user.id,
                'pourcentage': note,
                'comment': self.comment,
                'workflow_id': work_id.id,

            }
            # raise  ValidationError(str(ids))
            self.env['workflow.main.line'].create(ids)
            # work_main.write({'log_user':[6,0,[ids]]})
        id = str(self.prospection_id.id)
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': '/web#id=%s&view_type=form&model=prospection'%(id)
        }
