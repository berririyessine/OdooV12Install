# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Stock_Model(models.TransientModel):
    # _name = 'declaration.cnss'
    _name = 'stock.model'

    location_3d_id= fields.Many2one('stock.location')

    company_id= fields.Many2one('res.company', default=lambda self: self.env['res.company'].browse(self.env['res.company']._company_default_get('stock.model')).id)

    
    def GenerateLocationState(self):
        for rec in self:
            list =[]
            location_ids = self.env['stock.move.line'].search([('location_dest_id','=',rec.location_3d_id.id),('state','=','done')])
            for res in location_ids:
                ref_wh_in = self.env['stock.picking'].search([('name','=',res.reference),('state','=','done')])
                for ref_wh in ref_wh_in:
                    product_ids_location = self.env['stock.loc.line'].create({ 
                        'product_id':res.product_id.id,
                        'qty':res.qty_done,
                        'date':res.date,
                        'calibre':ref_wh.calibre,
                        'partner_id':ref_wh.partner_id.id,
                        })
                    list.append(product_ids_location.id)
            product_ids = self.env['stock.location.model'].create({ 
                'name': rec.location_3d_id.name,
                "saisie_ids":[ (6, 0, list)],
                })  
            
            return self.env.ref('stock_specific.etat_stock_emplacement').report_action(product_ids)
            # raise ValidationError(str(report))
            
   
class StockLocationModel(models.Model):
    _name = 'stock.location.model'
    name = fields.Char('')
    saisie_ids = fields.One2many('stock.loc.line','stock_loc_model')
class StockLocationModelLine(models.Model):
    _name = 'stock.loc.line'
    stock_loc_model = fields.Many2one('stock.location.model')
    product_id = fields.Many2one('product.product')
    qty = fields.Float('')
    date = fields.Datetime('')
    calibre = fields.Char('')
    partner_id = fields.Many2one('res.partner')


    
