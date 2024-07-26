# -*- coding: utf-8 -*-
from odoo.exceptions import except_orm,ValidationError,UserError
from datetime import datetime

from odoo import models, fields, api, _

class Prospection(models.Model):
    _name = 'prospection'
    _inherit = ['mail.thread']

    name = fields.Char('Titre', track_visibility='onchange',required=True)
    date = fields.Date(track_visibility='onchange',  default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', track_visibility='onchange', default=lambda self: self.env['res.partner'].search([], limit=1).id)
    stage_id = fields.Many2one('prospection.stage', string='Stage', track_visibility='onchange', index=True,  group_expand='_expand_states',default=lambda self: self._get_default_stage_id())
    stage_code = fields.Char(related="stage_id.code")
    color = fields.Integer('Color Index', default=0)
    planned_revenue = fields.Float('Expected Revenue')
    etude_ids = fields.One2many('etude.specifique','prospection_id')
    parution_validate = fields.Boolean('',compute="get_result_validate")
    purcent_physique = fields.Float('')
    purcent_tuneps = fields.Float('')
    purcent_physique_done = fields.Boolean('')
    purcent_tuneps_done = fields.Boolean('')
    validate_done = fields.Boolean('')
    note = fields.Text('',readonly=True)

    def get_result_validate(self):
        for rec in self:
            if (len(rec.etude_ids) != 0) and (rec.stage_id.id not in (self.env.ref('workflow_tender.stage_pros4').id,self.env.ref('workflow_tender.stage_pros5').id)):
                rec.parution_validate = True

    @api.multi
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def edit_dialog(self):
        form_view = self.env.ref('workflow_tender.prospection_form_view')
        return {
            'name': _('Prospection'),
            'res_model': 'prospection',
            'res_id': self.id,
            'views': [(form_view.id, 'form'),],
            'type': 'ir.actions.act_window',
            'target': 'inline',
        }

    def _get_default_stage_id(self):
        try:
            stage_id = self.env.ref('workflow_tender.stage_pros1').id
        except Exception as e:
            pass
        return stage_id
    def _expand_states(self, states, domain, order):
        stage_ids = self.env['prospection.stage'].search([])
        return stage_ids
    def etude_spec_technique(self):
        return {
            'name': ('Ajouter Etude'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'etude.specifique',
            'target': 'new'}

    @api.multi
    def paru_state(self):
        for rec in self:
            rec.write({'stage_id': self.env.ref('workflow_tender.stage_pros3').id})
            return {
                'name': ('Type'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'prospection.appel.offre',
                'target': 'new',
                'context': {'default_prospection_id': self.id},
            }
    def offre_physique(self):
       return {
           'name': ('Appel D offre Physique'),
           'type': 'ir.actions.act_window',
           'view_mode': 'form',
           'res_model': 'offre.physique',
           'context': {'search_default_prospection_id': self.id},
       }
    def offre_tuneps(self):
       return {
           'name': ('prospection_id'),
           'type': 'ir.actions.act_window',
           'view_mode': 'form',
           'res_model': 'offre.tuneps',
           'target': 'self',
            }

    def act_show_offre_tuneps(self):
        # raise ValidationError('heello')
        doc_id = self.env['offre.tuneps'].search([('prospection_id', '=', self.id)], limit=1)
        # raise ValidationError(str(doc_id.id))
        return {'type': 'ir.actions.act_window',
                'name': 'Offre Tuneps',
                'res_model': 'offre.tuneps',
                'res_id': doc_id.id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'self', }
    def act_show_offre_pysique(self):
        # raise ValidationError('heello')
        doc_id = self.env['offre.physique'].search([('prospection_id', '=', self.id)], limit=1)
        # raise ValidationError(str(doc_id.id))
        return {'type': 'ir.actions.act_window',
                'name': 'Offre Physique',
                'res_model': 'offre.physique',
                'res_id': doc_id.id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'self', }
    def technique_Qcm(self):
        return {
           'name': ('Questionnaire Technique'),
           'type': 'ir.actions.act_window',
           'view_mode': 'form',
           'res_model': 'qcm.technique',
           'target': 'new'}
    def conf_preparate(self):
        doc_id = self.env['preparation.config'].search([('prospection_id', '=', self.id)], limit=1)
        # raise ValidationError(str(doc_id.id))
        return {'name': ('Preparation Configuration et Calculs'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'preparation.config',
                'res_id': doc_id.id,
                'view_type': 'form',
                'target': 'self',
                'context': {'default_prospection_id': self.id},}
    def QCM_prospection(self):
        return {'type': 'ir.actions.act_window',
                'name': 'QCM Prospection',
                'res_model': 'qcm.prospection',
                'view_type': 'form',
                'view_mode': 'form',
                 'target': 'new',

                }
    def QCM_prospection_etude(self):
        return {'type': 'ir.actions.act_window',
                'name': 'QCM Etude',
                'res_model': 'qcm.prospection.etude',
                'view_type': 'form',
                'view_mode': 'form',
                 'target': 'new',

                }
class ProspectionAppelOffre(models.Model):
    _name = 'prospection.appel.offre'
    type = fields.Many2one('prospection.type' ,required=True)
    partner_id = fields.Many2one('res.partner', track_visibility='onchange')
    prospection_id = fields.Many2one('prospection')


    def generer_appel(self):
        for rec in self:
            if rec.type.id == self.env.ref('workflow_tender.stage_prosphysique').id:
                offre_physique = self.env['offre.physique'].search([('prospection_id', '=', self.prospection_id.id)])
                res = {}

                if len(offre_physique)<1:
                    # raise ValidationError(str(len(offre_physique)))
                    return {
                        'name': ('Appel D offre Physique'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'offre.physique',
                        'target': 'target',
                        'context': {'default_prospection_id': self.prospection_id.id},}
                else:
                    res = {
                        'type': 'ir.action.client',
                        'name': 'ERROR',

                    }
                    if res:
                        return res
            if  rec.type.id == self.env.ref('workflow_tender.stage_tuneps').id:
                offre_TUNEPS = self.env['offre.tuneps'].search([('prospection_id', '=',  self.prospection_id.id)])
                res = {}

                if len(offre_TUNEPS) < 1:
                    # raise ValidationError(str(len(offre_TUNEPS)))

                    return {
                        'name': ('Appel D offre tuneps'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'offre.tuneps',
                        'target': 'target',
                        'context': {'default_prospection_id': self.prospection_id.id},}
                else:
                    res = {
                                'type': 'ir.action.client',
                                'name':'ERROR',

                            }
                    if res:
                        return res

class EtudeSpecifique(models.Model):
    _name = "etude.specifique"
    name = fields.Char('Titre',required=True)
    description = fields.Html('description')
    prospection_id = fields.Many2one('prospection')

    @api.multi
    def generer(self):
        return {'type': 'ir.actions.act_window_close'}


class QcmTechnique(models.Model):
    _name = 'qcm.technique'
    prospection_id = fields.Many2one('prospection',required=True)
    user_id = fields.Many2one('res.users', 'Utilisateur Courant', default=lambda self: self.env.user)
    current_date = fields.Date(string='Your string',  default=fields.Date.context_today)
    q1 = fields.Char('')
    q2 = fields.Char('')
    q3 = fields.Float('')
    q4 = fields.Selection([('r1','R1'),('r2','R2'),('r3','R3')])
    q5 = fields.Selection([('r1', 'R1'), ('r2', 'R2'), ('r3', 'R3')])
    q6 = fields.Selection([('r1', 'R1'), ('r2', 'R2'), ('r3', 'R3')])
    notes_qcm = fields.Char('')

    def validate(self):
        notes = ''
        note = 0.0
        for rec in self:
            if rec.user_id:
                notes += 'Questionnaire fait par l\'Utilisateur : ' +str(rec.user_id.name)+ "\n"
            if rec.current_date:
                notes += 'le  : ' +str(rec.current_date)+ "\n"
            notes += "Contenue du Questionnaire" + "\n"
            if rec.q1:
                notes +=  "Q1: " + str(rec.q1) + "\n"
                note += 16.67
            if rec.q2:
                notes +=  "Q2: " + str(rec.q2) + "\n"
                note += 16.67
            if rec.q3 != 0.0:
                notes +=  "Q3: " + str(rec.q3) + "\n"
                note += 16.67
            if rec.q4:
                notes +=  "Q4: " + str(rec.q4) + "\n"
                note += 16.67
            if rec.q5:
                notes +=  "Q5: " + str(rec.q5) + "\n"
                note += 16.67
            if rec.q6 != '':
                notes +=  "Q6: " + str(rec.q6) + "\n"
                note += 16.67
            if rec.notes_qcm:
                notes +=  "Notes interne: " + str(rec.notes_qcm) + "\n"
            rec.prospection_id.write({'note':notes,'validate_done':True,'stage_id': self.env.ref('workflow_tender.stage_pros4').id})
            # self.write({'stage_id': self.env.ref('workflow_tender.stage_pros4').id})
            res = ({
                'name': 'Questionnaire Technique',
                'state': 4,
                'prospection_id': self.prospection_id.id,
                'questionnaire_techn': int(note),
            })
            work_id = self.env['workflow.main'].search([('prospection_id', '=', self.prospection_id.id)])
            if len(work_id) == 0:
                # raise ValidationError('in if..')
                result = self.env['workflow.main'].create(res)
                ids = {
                    'name': 'Questionnaire Technique',
                    'user_id': self.env.user.id,
                    'pourcentage': note,
                    'comment': self.notes_qcm,
                    'workflow_id': result.id,
                }
                self.env['workflow.main.line'].create(ids)
            else:
                work_id.write({'questionnaire_techn': int(note),'state': 4})
                ids = {
                    'name': 'Questionnaire Technique',
                    'user_id': self.env.user.id,
                    'pourcentage': note,
                    'comment': self.notes_qcm,
                    'workflow_id': work_id.id,
                }
                self.env['workflow.main.line'].create(ids)

class QcmProspection(models.Model):
    _name = "qcm.prospection"

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
            'name':'Prospection',
            'state':1,
            'prospection_id':self.prospection_id.id,
            'prospection':int(note),
        })
        work_id = self.env['workflow.main'].search([('prospection_id','=',self.prospection_id.id)])
        if len(work_id) == 0:
            # raise ValidationError('in if..')
            result = self.env['workflow.main'].create(res)
            ids = {
                'name': 'Prospection',
                'user_id': self.env.user.id,
                'pourcentage': note,
                'comment': self.comment,
                'workflow_id': result.id,
            }
            self.env['workflow.main.line'].create(ids)
        else:
            work_id.write({'prospection':int(note),'state': 1})
            ids = {
                'name': 'Prospection',
                'user_id': self.env.user.id,
                'pourcentage': note,
                'comment': self.comment,
                'workflow_id': work_id.id,
            }
            self.env['workflow.main.line'].create(ids)
        return {'type': 'ir.actions.act_window_close'}
class QcmProspectionEtude(models.Model):
    _name = "qcm.prospection.etude"

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
            'name':'Etude',
            'state':2,
            'prospection_id':self.prospection_id.id,
            'etude':int(note),
        })
        work_id = self.env['workflow.main'].search([('prospection_id','=',self.prospection_id.id)])
        if len(work_id) == 0:
            # raise ValidationError('in if..')
            result = self.env['workflow.main'].create(res)
            ids = {
                'name': 'Etude',
                'user_id': self.env.user.id,
                'pourcentage': note,
                'comment': self.comment,
                'workflow_id': result.id,
            }
            self.env['workflow.main.line'].create(ids)
        else:
            work_id.write({'etude':int(note),'state': 2})
            ids = {
                'name': 'Etude',
                'user_id': self.env.user.id,
                'pourcentage': note,
                'comment': self.comment,
                'workflow_id': work_id.id,
            }
            self.env['workflow.main.line'].create(ids)
        return {'type': 'ir.actions.act_window_close'}
