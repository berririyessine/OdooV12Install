from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date
from odoo import models, fields, api

class report_inherit(models.Model):
    _inherit = 'product.template'
    marque = fields.Char()
    capacite = fields.Char()
    couleur = fields.Char()
    code_article = fields.Char()
    puissance = fields.Char()
    garantie = fields.Char()




class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    qty_minimum = fields.Float('')
    image_autre = fields.Binary('image')




class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'


    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability_alert(self):
        if not self.product_id or not self. or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product = self.product_id.with_context(
                warehouse=self.order_id.warehouse_id.id,
                lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
            )
            product_qty = self.product_id.qty_minimum
            if product_qty != 0.0:

                if product.virtual_available <= product_qty :
                        message =  ('Le stock de produit %s a atteint le stock minimum %s.') % \
                                (self.product_id.name, self.product_id.qty_minimum)
                        warning_mess = {
                            'title': ('Merci de Verifier Votre Stock!'),
                            'message' : message
                        }
                        return {'warning': warning_mess}

        return {}
