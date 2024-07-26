# -*- coding: utf-8 -*-

from odoo import fields, models, api,_

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.one
    @api.depends('amount_total')
    def _amount_timbre(self):
        for order in self:
            amount_timbre = order.amount_untaxed + order.amount_tax
            if order.timbre_fiscal  == True:
                timbre = self.env['config.timbre']._timbre(order.amount_untaxed + order.amount_tax)
                print("timbre['timbre']-sale",timbre['timbre'])
                self.timbre = timbre['timbre']

    # inherited methof from sale_order model
    @api.one
    @api.depends('order_line.price_subtotal', 'currency_id', 'company_id','timbre_fiscal')
    def _amount_all(self):

        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal

                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=order.partner_shipping_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })
            amount_timbre = order.amount_total 
            if (order.timbre_fiscal == True):
                timbre = self.env['config.timbre']._timbre(amount_timbre)
                self.timbre = timbre['timbre'] 
                self.amount_total = timbre['amount_timbre']


    timbre_fiscal = fields.Boolean(string="Droit de timbre",default=False)
    timbre = fields.Monetary(string='Timbre', store=True, readonly=True,
                             compute='_amount_timbre', track_visibility='onchange')

    # @api.multi
    # def _prepare_invoice(self):
    #     res = super(SaleOrder, self)._prepare_invoice()       
    #     if self.timbre_fiscal == True:
    #         res['timbre_fiscal'] =  True
    #         res['timbre'] =  self.timbre
    #     return res

