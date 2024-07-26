# -*- coding: utf-8 -*-
from odoo.exceptions import except_orm,ValidationError,UserError
from datetime import datetime

from odoo import models, fields, api, _

class WokflowMain(models.Model):
    _name = 'workflow.main'
    name = fields.Char('',default='WorkFLow pour ...')
    state = fields.Selection([(1,'Prospection'),(2,'Etude'),(3,'Appel D\'offre physique/Tuneps'), (4,'Q.Technique'),(5,'Prepa et Config'),(6,'Devis'),(7,'D.Envoyé'),(8,'Bn.Commande'),(9,'Facture')],default=1)
    prospection = fields.Float('')
    etude = fields.Float('')
    appel_offre = fields.Float('')
    questionnaire_techn = fields.Float('')
    prepa_config = fields.Float('')
    devis = fields.Float('')
    devis_envoye = fields.Float('')
    commande = fields.Float('')
    facture = fields.Float('',help='facture help you to know many things')
    log_user = fields.One2many('workflow.main.line','workflow_id')
    prospection_id = fields.Many2one('prospection')

    def prosp_show(self):
        doc_id = self.env['prospection'].search([('id','=',self.prospection_id.id)])
        return {
            'name': ('Devis'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': doc_id.id,
            'res_model': 'prospection',
            }

    def devis_show(self):
        doc_id = self.env['sale.order'].search([('prospection_id','=',self.prospection_id.id)])
        return {
            'name': ('Devis'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': doc_id.id,
            'res_model': 'sale.order',
            }
    def invoice_show(self):
        doc_id = self.env['account.invoice'].search([('prospection_id','=',self.prospection_id.id)])
        return {
            'name': ('Facture'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': doc_id.id,
            'res_model': 'account.invoice',
            }
class WokflowMainLine(models.Model):
    _name = 'workflow.main.line'
    name = fields.Char('')
    user_id = fields.Many2one('res.users')
    pourcentage = fields.Float('')
    comment = fields.Text('')
    workflow_id = fields.Many2one('workflow.main')


