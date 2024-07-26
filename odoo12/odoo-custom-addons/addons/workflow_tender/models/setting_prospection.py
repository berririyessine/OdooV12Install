# -*- coding: utf-8 -*-
from odoo.exceptions import except_orm,ValidationError,UserError
from datetime import datetime

from odoo import models, fields, api, _
class ProspectionType(models.Model):
    _name = 'prospection.type'
    name = fields.Char('')
class ProspectionStage(models.Model):

    _name = "prospection.stage"
    _description = "Stage of case"

    name = fields.Char('Stage Name', required=True)
    sequence = fields.Integer('Sequence', default=1)
    code = fields.Char('')
    on_change = fields.Boolean('Change Probability Automatically')
    requirements = fields.Text('Requirements')
    legend_priority = fields.Text('Priority Management Explanation')

