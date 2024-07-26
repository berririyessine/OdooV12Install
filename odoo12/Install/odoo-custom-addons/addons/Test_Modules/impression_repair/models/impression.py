# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from datetime import datetime,date
from odoo import models, fields, api

class PartnerAttestDetails(models.TransientModel):
    _name = 'rep.list'

    partner_id= fields.Many2one('res.partner')
    orders= fields.Text(string="Ordres")


    def GenererDetails(self):
        for rec in self:
            list =[]
            detail_ids = self.env['rep.list.line'].create({
                "partner_id":rec.partner_id.id,
                "orders":rec.orders,
            })
            return self.env.ref('impression_repair.repair_list').report_action(detail_ids)




class PartnerAttestDetailsLines(models.Model):
    _name = 'rep.list.line'

    partner_id= fields.Many2one('res.partner')
    orders= fields.Text(string="Ordres")
