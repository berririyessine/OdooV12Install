# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleOrdreInherit(models.Model):
    _inherit = 'sale.order'

    location_id = fields.Many2one('stock.location',
        readonly=True, required=True,
        states={'draft': [('readonly', False)]})


    @api.multi
    def action_confirm(self):
        res= super(SaleOrdreInherit,self).action_confirm()
        bc = self.env['stock.picking'].search([('origin','=',self.name)])
        bc.write({
            "location_id":self.location_id.id,
            
            })

