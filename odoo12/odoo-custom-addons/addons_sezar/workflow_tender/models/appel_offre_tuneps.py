# -*- coding: utf-8 -*-
from odoo.exceptions import except_orm,ValidationError,UserError
from datetime import datetime

from odoo import models, fields, api, _

class QcmOffreTechniquetuneps(models.Model):
    _name = "qcm.offre.tuneps"

    prospection_id = fields.Many2one('prospection',required=True)
    qcm_id = fields.Many2one('offre.tuneps')
    user_id = fields.Many2one('res.users', 'Utilisateur Courant', default=lambda self: self.env.user)
    current_date = fields.Date(string='Your string',  default=fields.Date.context_today)
    q1 = fields.Boolean('')
    q2 = fields.Boolean('')
    q3 = fields.Boolean('')
    q4 = fields.Boolean('')
    comment = fields.Text('')

    def Valider(self):
        note = 0.0
        self.prospection_id.purcent_tuneps = 0.0
        for rec in self:
            if rec.q1:
                note += 25.0
            if rec.q2:
                note += 25.0
            if rec.q3:
                note += 25.0
            if rec.q4:
                note += 25.0
        rec.prospection_id.write({'purcent_tuneps':note,'purcent_tuneps_done':True})
        res = ({
            'name': 'Offre TUNEPS',
            'state': 3,
            'prospection_id': self.prospection_id.id,
            'appel_offre': int(note),
        })
        work_id = self.env['workflow.main'].search([('prospection_id', '=', self.prospection_id.id)])
        if len(work_id) == 0:
            # raise ValidationError('in if..')
            result = self.env['workflow.main'].create(res)
            ids = {
                'name': 'Offre TUNEPS',
                'user_id': self.env.user.id,
                'pourcentage': note,
                'comment': self.comment,
                'workflow_id': result.id,
            }
            self.env['workflow.main.line'].create(ids)
        else:
            work_id.write({'appel_offre': int(note),'state': 3})
            ids = {
                'name': 'Offre TUNEPS',
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
            'url': '/web#id=%s&view_type=form&model=prospection' % (id)
        }
class AppelOffreTuneps(models.Model):
    _name = "offre.tuneps"
    name = fields.Char('Référence', required=True)
    date_start = fields.Date('Date Début',  default=fields.Date.context_today, required=True)
    date_end = fields.Date('Date Fin')
    caution = fields.Float('Caution')
    partner_id = fields.Many2one('res.partner', track_visibility='onchange')
    # piece_joint = fields.Binary('Cahier des charges')
    piece_joint = fields.Many2many('ir.attachment', 'offre_tuneps_attachments_rel', 'offre_tuneps', 'attachment_id', 'Piece Joint')
    prospection_id = fields.Many2one('prospection')


    def QCM_tuneps(self):
        doc_id = self.env['qcm.offre.tuneps'].search([])
        return {'type': 'ir.actions.act_window',
                'name': 'QCM Tunpes',
                'res_model': 'qcm.offre.tuneps',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_qcm_id': self.id},}

