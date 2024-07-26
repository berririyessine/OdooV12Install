# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo import models, fields, api
#
class AdvancedSearchProducts(models.Model):
    _name= "advanced.product.search.purchase"
    product_ids= fields.Many2many('product.product')

    purchase_order_id = fields.Many2one('purchase.order')

    def Valider(self):
        list = []
        # for rec
        for add in self.product_ids:
            # list.append(add.id)
            self.purchase_order_id.order_line.create({
                    'order_id':self.purchase_order_id.id,
                    'product_id':add.id,
                    'name':add.name,
                    'product_qty':1.0,
                    'date_planned':self.purchase_order_id.date_order,
                    'product_uom':add.uom_id.id,
                    'price_unit':0.0
            })

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    total_qty_product = fields.Float('', compute="get_total_qty_product")

    @api.onchange('product_id')
    def get_total_qty_product(self):
        for rec in self:
            if rec.product_id :
                stock_ids = self.env['stock.quant'].search([('product_id','=',rec.product_id.id), ('location_id.usage','=','internal') ])
                for stock in stock_ids:
                    rec.total_qty_product += stock.quantity
                # sale_line_id= self.env['sale.order.line'].search([('order_id','=',rec.order_id.id), ('product_id','=', rec.product_id.id)])
                # if len(sale_line_id)> 1:
                #     raise ValidationError(('Produit %s Trouvé déjà dans Ligne de la commande %s '%(rec.product_id.name ,rec.order_id.name)))



class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    resteApayer = fields.Monetary("reste à payer",compute='calculReste', store=False)
    encaissement_ids = fields.Many2many('purchase.order.order.payment','purchase.order_order_id',compute="calculReste" ,store=False)
    payment_ids = fields.Many2many('account.payment',compute="get_payment_ref" ,store=False)
    date_order_copy = fields.Date('Order Date', required=True, states=READONLY_STATES, index=True, copy=False, default=fields.Date.today())
    date_order = fields.Datetime('Order Date', states=READONLY_STATES, index=True, copy=False, compute="related_date_order")

    def related_date_order(self):
        for rec in self:
            rec.date_order= rec.date_order_copy.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    def find_product(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'advanced.product.search.purchase',
            'view_mode': 'form',
            'target': 'new',
            'context':{'default_purchase_order_id':self.id,},
            'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
        }

    @api.multi
    def get_payment_ref(self):
        for rec in self:
            payment_ids = self.env['account.payment'].search([('communication', '=', rec.name)])
            rec.payment_ids=  payment_ids
    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        immediate_transfer_line_ids = []
        for picking in self.picking_ids:
            immediate_transfer_line_ids.append([0, False, {
                'picking_id': picking.id,
                'to_immediate': True
            }])
        sale_delivery = self.env['stock.immediate.transfer'].create({
            'pick_ids': [(4, p.id) for p in self.picking_ids],
            'show_transfers': False,
            'immediate_transfer_line_ids': immediate_transfer_line_ids
        })
        sale_delivery.with_context(button_validate_picking_ids=sale_delivery.pick_ids.ids).process()
        return res

    @api.multi
    def set_to_draft(self):
        self.ensure_one()
        immediate_return_line_ids = []
        location_id = False
        move_id = False

        stock_picking = self.env['stock.picking'].search([('origin','=',self.name),('name','like','%IN%')])[-1]
        # raise ValidationError(str(stock_picking))
        if stock_picking:
            for return_line in stock_picking.move_line_ids_without_package:
                move_id = return_line.id
                location_id = return_line.location_dest_id.id
                move_id = return_line.id
                if return_line.product_id.type == 'product':
                    immediate_return_line_ids.append([0, False, {
                            'product_id': return_line.product_id.id,
                            'quantity': return_line.qty_done,
                            'uom_id': return_line.product_uom_id.id,
                            'move_id': self.env['stock.move'].sudo().search([('reference','=',stock_picking.name),('product_id','=',return_line.product_id.id)]).id,
                            'to_refund': True,
                            }])
                    # raise ValidationError(str())
            if location_id:
                # immediate_return_line_ids['move_id'] = self.env['stock.move'].search([('id','=',move_id)])
                self.env['stock.return.picking'].create({
                        'picking_id': stock_picking.id,
                        'product_return_moves': immediate_return_line_ids,
                        'location_id':stock_picking.location_id.id
                        }).create_returns()
            #
                pickings = self.env['stock.picking'].search([('origin','like',stock_picking.name)])
                # self.env['stock.immediate.transfer'].sudo().create({'pick_ids': [(4, picking.id)]}).process()
                immediate_transfer_line_ids = []
                for picking in pickings:
                    immediate_transfer_line_ids.append([0, False, {
                        'picking_id': picking.id,
                        'to_immediate': True,
                    }])

                sale_delivery = self.env['stock.immediate.transfer'].create({
                    'pick_ids': [(4, picking.id)],
                    'show_transfers': False,
                    'immediate_transfer_line_ids': immediate_transfer_line_ids
                })
                # raise ValidationError(str(sale_delivery))
                sale_delivery.with_context(button_validate_picking_ids=sale_delivery.pick_ids.ids).process()
            #
            #
            return self.write({'state': 'draft'})


    def add_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order.payment',
            'view_mode': 'form',
            'target': 'new',
            'context':{'default_partner_id':self.partner_id.id,
                    'default_amount':self.resteApayer,
                    'default_memo': str(self.name),
                    'default_purchase_order_id':self.id,
                    'default_payment_date':self.date_order
                        },
            'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
        }

    @api.multi
    def calculReste(self):
        for rec in self:
            encaissement_ids = self.env['account.payment'].search([('communication', '=', rec.name)])
            # rec.encaissement_ids=  encaissement_ids
            somme=0
            for encaiss in encaissement_ids :
                somme+=encaiss.amount
            rec.resteApayer=rec.amount_total-somme


class PurchaseOrderPaymet(models.Model):
    _name = "purchase.order.payment"

    purchase_order_id = fields.Many2one('purchase.order')
    memo = fields.Char('Origin')
    partner_id = fields.Many2one('res.partner')
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    amount = fields.Float("Montant", required=True)
    num = fields.Char('N°')
    date = fields.Date('Date')
    banque_list = fields.Selection([ ('STB', 'STB'),('BNA', 'BNA' ),('BH', 'BH'),('BFPME', 'BFPME'),('BTS', 'BTS'),('BTE', 'BTE'),('BTL', 'BTL'),('TSB', 'TSB'),
            ('Zitouna', 'Zitouna'),('Al_Baraka', 'Al Baraka'),('Al_Wifak', 'Al Wifak'),('Amen_Bank', 'Amen Bank'),('Attijari_Bank', 'Attijari Bank'),('ATB', 'ATB'),('ABC', 'ABC'),
            ('BIAT', 'BIAT'),('BT', 'BT'),('BTK', 'BTK'),('BFT', 'BFT'),('Citi_Bank', 'Citi Bank'),('QNB_Tunis', 'QNB Tunis'),('UBCI', 'UBCI'),('UIB', 'UIB')],default='STB')
    check_bool = fields.Boolean('')

    @api.onchange('journal_id')
    def onchange_visible(self):
        if self.journal_id.checkInfo:
            self.check_bool = True
        else:
            self.check_bool = False
    def post_payment(self):
        # try:
        date = self.payment_date
        vals= {
            'partner_id':self.partner_id.id,
            'journal_id':self.journal_id.id,
            'partner_type':'customer',
            'amount':self.amount,
            'communication':self.memo,
            'show_type': True,
            'payment_type':'inbound',
            'payment_method_id':1,
            'check_bool':self.check_bool ,
            'num':self.num if self.journal_id.checkInfo else '',
            'date':self.date if self.journal_id.checkInfo else False,
            'banque_list':self.banque_list if self.journal_id.checkInfo else ''
            }
        self.env['account.payment'].create(vals).post()
        if self.purchase_order_id.resteApayer != 0.0 :
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order.payment',
                'view_mode': 'form',
                'target': 'new',
                'context':{'default_partner_id':self.purchase_order_id.partner_id.id,
                        'default_amount':self.purchase_order_id.resteApayer,
                        'default_memo': str(self.purchase_order_id.name),
                        'default_purchase_order_id':self.purchase_order_id.id,
                        'default_payment_date':self.purchase_order_id.date_order
                            },
                'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
            }        # except Exception as e:
        #     self.sale_order_id.resteApayer += self.amount
