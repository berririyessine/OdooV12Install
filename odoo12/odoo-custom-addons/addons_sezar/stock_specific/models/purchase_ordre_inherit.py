# -*- coding: utf-8 -*-
import time
import datetime
from datetime import datetime, timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PurchaseOrdreInherit(models.Model):
    _inherit = 'purchase.order'

    calibre = fields.Char('')
    debit = fields.Integer('')
    credit = fields.Integer('')
    taux = fields.Integer('',compute='get_diff')
    # location_dest_id = fields.Many2one('stock.location',
    #     readonly=True, required=True,
    #     states={'draft': [('readonly', False)]})
    # tag_ids = fields.Many2many('stock.location.tag',string='Tags',
    #     readonly=True, required=True,
    #     states={'draft': [('readonly', False)]})
    # barcode = fields.Char('Barcode', copy=False,
    #     readonly=True, required=True,
    #     states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Purchase Order'),
        ('sent', 'Commande envoyé'),
        ('to approve', 'To Approve'),
        ('purchase', 'Bon D\'entré'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    select_all = fields.Boolean('')

    @api.onchange('select_all')
    def onchange_slip_line(self):
        for rec in self:
            for res in rec.order_line:
                if rec.select_all == True:
                    res.selected_location = True
                else :
                    res.selected_location = False

    @api.onchange('tag_ids','barcode')
    def onchange_location_infos(self):
        list = []
        for rec in self.tag_ids:
            list.append(rec.id)
        self.location_dest_id.write({
                'tag_ids':[ (6, 0, list)],
                'barcode':self.barcode,
            })
    @api.onchange('debit','credit')
    def get_diff(self):
        for rec in self:
            rec.taux  = rec.debit - rec.credit
    @api.multi
    def button_confirm(self):
        res= super(PurchaseOrdreInherit,self).button_confirm()
        bc = self.env['stock.picking'].search([('origin','=',self.name)])
        bc.write({
            "calibre":self.calibre,
            "debit":self.debit,
            "credit":self.credit,
            "taux":self.taux,
            })
        for r in self:
            for line in r.order_line:
                for insert_location in bc:
                    for i in insert_location.move_lines:
                        if line.product_id.id == i.product_id.id:
                            i.write({'location_dest_id' : line.location_desti_id.id})
                    for i in insert_location.move_line_ids:
                        if line.product_id.id == i.product_id.id:
                            i.write({'location_dest_id' : line.location_desti_id.id})
    # @api.multi
    # def _get_destination_location(self):
    #     self.ensure_one()
    #     if self.dest_address_id:
    #         return self.dest_address_id.property_stock_customer.id
    #     return self.location_dest_id.id or self.location_id.id

    def get_barcodes(self):
        for r in self:
            date = str(r.date_order)
            date_convert = date.split()
            y= str((date_convert)[0])
            fourni_rf = r.partner_ref
            i=0
            for rec in r.order_line:
                
                product_ref=' '
                product_id = str(rec.product_id.name) 
                if len(rec.product_id.name)> 2:
                    product_ref = product_id[:3].upper()
                clb = rec.calibre
                date = str(y)
                i +=1
                increment =  str(i).zfill(4)
                generate_code = str(product_ref) +"-" + str(clb) +"-" +str(fourni_rf) +"-"+ str(date) +"-" +str(increment) 
                # raise ValidationError(str(generate_code))
                rec.barcode = generate_code
                rec.product_id.sudo().write({'barcode':rec.barcode})
    def get_location(self):
        return {'type': 'ir.actions.act_window',
                'name': 'Emplacement',
                'res_model': 'move.location',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context' : {'default_bn_commande_ref':self.id}

                }
class MoveLocation(models.TransientModel):
    _name = 'move.location'

    location_dest_id = fields.Many2one('stock.location',required=True)
    tag_ids = fields.Many2many('stock.location.tag',string='Tags')
    barcode = fields.Char('Barcode') 
    bn_commande_ref = fields.Many2one('purchase.order')  
    

    @api.onchange('tag_ids','barcode')
    def onchange_location_infos(self):
        list = []
        for rec in self.tag_ids:
            list.append(rec.id)
        self.location_dest_id.write({
                'tag_ids':[ (6, 0, list)],
                'barcode':self.barcode,
            })
    def validerS(self):
        for rec in self:
            for re in rec.bn_commande_ref.order_line:
                if re.selected_location == True:
                    re.location_desti_id = rec.location_dest_id.id
    
class PurchaseOrdreInheritLine(models.Model):
    _inherit = 'purchase.order.line'
    calibre = fields.Integer('')
    barcode = fields.Char('')
    selected_location = fields.Boolean('')
    location_desti_id = fields.Many2one('stock.location')
    
    def get_melange(self):
        return {'type': 'ir.actions.act_window',
                'name': 'Transfer Mélange',
                'res_model': 'move.stock.line',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context' : {'default_bn_commande_ref':self.order_id.id,'default_article_selected':self.product_id.id}
                # 'domain':[('location_dest_id','=',loc_intern_id)],
                }

class MoveStockLine(models.TransientModel):
    _name = 'move.stock.line'   
    @api.model
    def _melange_filter(self):

        return [('location_dest_id','like','Mélange'),('state','=','done')]
    name=fields.Char('')
    stock_move_ids = fields.Many2many('stock.move', domain=_melange_filter)

    total = fields.Float('')
    bn_commande_ref = fields.Many2one('purchase.order')
    article_selected = fields.Many2one('product.product')


    @api.onchange('stock_move_ids')
    def total_qty(self):
        for r in self:
            for rec in r.stock_move_ids:
                r.total += rec.quantity_done
    def valider(self):
        for r in self:
            for rec in r.stock_move_ids:
                exist_move = self.env['stock.move'].search([('id','=',rec.id)])
                for unl in exist_move:
                    unl.write({'state':'draft'})
                    unl._action_cancel()
                    # raise ValidationError(str(rec.product_id))
                    rec.product_id.active =False #a verifier encore une fois 
            product_update = self.env['purchase.order.line'].search([('order_id','=',r.bn_commande_ref.id),('product_id','=',r.article_selected.id)])
            product_update.write({'product_qty':product_update.product_qty + r.total})


            



class inheritBL(models.Model):
    _inherit = 'stock.picking'
    calibre = fields.Char('',readonly=True)
    debit = fields.Integer('',readonly=True)
    credit = fields.Integer('',readonly=True)
    taux = fields.Integer('',readonly=True)
