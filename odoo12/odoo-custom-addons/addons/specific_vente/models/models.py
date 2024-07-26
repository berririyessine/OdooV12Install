# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError,ValidationError
class ProducProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('categ_id','type')
    def compute_code_a_barre(self):
        for rec in self:
            if rec.purchase_ok == True and rec.type == 'product':
                if rec.categ_id:
                    rec.barcode = str(rec.categ_id.code) + str(rec.categ_id.next_number).zfill(8)

    # @api.model
    # @api.returns('self', lambda value: value.id)
    # def create(self, vals):
    #     categorie= self.env['product.category'].search([('id','=',vals['categ_id'])])
    #     # raise ValidationError(str(categorie.name))
    #     categorie.write({'next_number' : categorie.next_number+1})
    #     return super(ProducProduct, self).create(vals)
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    marge = fields.Float('marge',digits_compute=dp.get_precision('Product Price'))
    lst_price = fields.Float(
        'Sale Price', compute='onchange_calculer',
        digits=dp.get_precision('Product Price'), inverse='_set_product_lst_price',
        help="The sale price is managed from the product template. Click on the 'Configure Variants' button to set the extra attribute prices.")
    rangement = fields.Many2one('rangement.artc', 'Rangement')

    @api.onchange('marge','standard_price')
    def onchange_calculer(self):
        for rec in self:
            rec.list_price = rec.standard_price * (rec.marge/100) + rec.standard_price
            rec.lst_price = rec.list_price

    @api.depends('list_price', 'price_extra')
    def _compute_product_lst_price(self):
        to_uom = None
        if 'uom' in self._context:
            to_uom = self.env['uom.uom'].browse([self._context['uom']])

        for product in self:
            if to_uom:
                list_price = product.uom_id._compute_price(product.list_price, to_uom)

            else:
                list_price = product.list_price
            product.lst_price = list_price + product.price_extra
            if product.marge:
                list_price = product.standard_price * (product.marge/100) + product.standard_price
            product.lst_price = list_price

    @api.onchange('categ_id','type')
    def compute_code_a_barre(self):
        for rec in self:
            if rec.purchase_ok == True and rec.type == 'product':
                if rec.categ_id:
                    rec.barcode = str(rec.categ_id.code) + str(rec.categ_id.next_number).zfill(8)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        categorie= self.env['product.category'].search([('id','=',vals['categ_id'])])
        # raise ValidationError(str(categorie.name))
        categorie.write({'next_number' : categorie.next_number+1})
        return super(ProductTemplate, self).create(vals)

class ProductRangement(models.Model):
    _name = 'rangement.artc'
    name = fields.Char('Nom')


# Banques en liste
class PaymentInhert(models.Model):
    _inherit = 'account.payment'
    banque_list = fields.Selection([ ('STB', 'STB'),('BNA', 'BNA' ),('BH', 'BH'),('BFPME', 'BFPME'),('BTS', 'BTS'),('BTE', 'BTE'),('BTL', 'BTL'),('TSB', 'TSB'),
    ('Zitouna', 'Zitouna'),('Al_Baraka', 'Al Baraka'),('Al_Wifak', 'Al Wifak'),('Amen_Bank', 'Amen Bank'),('Attijari_Bank', 'Attijari Bank'),('ATB', 'ATB'),('ABC', 'ABC'),
    ('BIAT', 'BIAT'),('BT', 'BT'),('BTK', 'BTK'),('BFT', 'BFT'),('Citi_Bank', 'Citi Bank'),('QNB_Tunis', 'QNB Tunis'),('UBCI', 'UBCI'),('UIB', 'UIB')],default='STB')

class ProductCategoryInherit(models.Model):
    _inherit = 'product.category'
    code = fields.Char('')
    next_number= fields.Integer('',size=8,default=1)
