# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import Warning, ValidationError
from datetime import datetime,date

# class AddChatter(models.Model):
# 	_name = 'muk_dms.file'
# 	_inherit = 'mail.thread'

class archive_chatter(models.Model):
    _name = 'muk_dms.file'
    _inherit = ['muk_dms.file', 'mail.thread', 'mail.activity.mixin']


class archive_document(models.Model):
     # _name = 'archive_document.archive_document'
    _inherit = ['muk_dms.file']
    boite_archive = fields.Many2one("boite.archive", string="Boite d'archive", track_visibility='always')
    source = fields.Many2one("source.file", string="Source", track_visibility='always')
    code = fields.Char('Code', track_visibility='always')
    codeS = fields.Integer('Num')
    date_document = fields.Date (string="Date Document", default=lambda self: fields.Date.to_string(date.today()), track_visibility='always')
    date_legal = fields.Date (string="Date Léga/Enreg", default=lambda self: fields.Date.to_string(date.today()), track_visibility='always')
    decharge = fields.Boolean(string='Décharge')
    date_decharge = fields.Date (string="Date Décharge", default=lambda self: fields.Date.to_string(date.today()), track_visibility='always')
    text_decharge = fields.Text (string="Commentaire", track_visibility='always')
    employee = fields.Many2one("hr.employee", string="Employé", track_visibility='always')
    # @api.model
    # def _get_next_seq(self):
    #     sequence = self.env['ir.sequence'].search([('code','=','muk_dms.file')])
    #     next= str(self.boite_archive.name)+sequence.get_next_char(sequence.number_next_actual)
    #     return next

    @api.onchange('boite_archive')
    def _get_next_seq(self):
        if self.boite_archive.name:
            self.codeS = self.boite_archive.arch_seq+1
            self.code = self.boite_archive.abrv + "/000" + str(self.codeS)
    @api.onchange('codeS')
    def _next_seq(self):

        if self.boite_archive.name:
            self.code = self.boite_archive.abrv + "/000" + str(self.codeS)

    @api.model
    def create(self, vals):
        if vals.get('boite_archive'):
            # raise  ValidationError ('create')
            if vals['codeS']>self.env['boite.archive'].browse(vals.get('boite_archive')).arch_seq:
                self.env['boite.archive'].browse(vals.get('boite_archive')).write({'arch_seq':vals['codeS']})
        result = super(archive_document, self).create(vals)
        return result

    @api.multi
    def write(self, vals):
        if vals.get('boite_archive'):
            # raise  ValidationError (vals.get('codeS'))
            if (vals.get('codeS')):
                if (int(vals['codeS'])>int(self.env['boite.archive'].browse(vals.get('boite_archive')).arch_seq)):
                    self.env['boite.archive'].browse(vals.get('boite_archive')).write({'arch_seq':vals['codeS']})
            else:
                if (self.codeS>int(self.env['boite.archive'].browse(vals.get('boite_archive')).arch_seq)):
                    self.env['boite.archive'].browse(vals.get('boite_archive')).write({'arch_seq':self.codeS})
        result = super(archive_document, self).write(vals)
        return result


class boite_archive(models.Model):
    _name = 'boite.archive'
    name = fields.Char('Référence Boite', default=lambda self: self._get_next_seq(), required=True)
    abrv = fields.Char('Abréviation', required=True)
    arch_seq = fields.Integer('Séquence')
    @api.model
    def _get_next_seq(self):
        sequence = self.env['ir.sequence'].search([('code','=','boite.archive')])
        next= sequence.get_next_char(sequence.number_next_actual)
        return next

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('boite.archive') or 'New'
        result = super(boite_archive, self).create(vals)
        return result

class source_file(models.Model):
    _name = 'source.file'
    name = fields.Char('Source')
