# -*- coding: utf-8 -*-

from math import ceil
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class ConfigTimbre(models.Model):
    _inherit = ['mail.thread']
    _name='config.timbre'
    _description='Fiscal Timbre configuration'

    name =  fields.Char('Nom', required=True)
    valeur = fields.Float('Valeur du timbre', digits=dp.get_precision('Product Price'), required=True, track_visibility='onchange')   
    amount = fields.Float('Amount', digits=dp.get_precision('Product Price'),required=True, track_visibility='onchange')

    account_id = fields.Many2one('account.account',"Compte De Droit d’enregistrement (Timbre)", track_visibility='onchange')
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'name must be unique per Company!'),
    ]

    @api.model
    def _timbre(self, montant):
        res = {}
        timbre_obj = self.env['config.timbre']
        liste_obj  = timbre_obj.search([])
        if not liste_obj :
           raise UserError(_('Pas de configuration du calcul Timbre.'))
        dict = liste_obj[-1]
        montant_avec_timbre = ( dict['amount'] * dict['valeur'])       

        res['timbre'] = montant_avec_timbre
        res['amount_timbre'] = montant + montant_avec_timbre

        return res




