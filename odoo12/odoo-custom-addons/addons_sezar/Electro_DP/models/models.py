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
    qty_maximum = fields.Float('')
    image_autre = fields.Binary('image')




class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'


    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability_alert(self):
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product = self.product_id.with_context(
                warehouse=self.order_id.warehouse_id.id,
                lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US')
            product_qty = self.product_id.qty_minimum
            if product_qty != 0.0:

                if product.qty_available-self.product_uom_qty <= product_qty :
                        message =  ('Le stock de produit %s a atteint le stock minimum %s.') % \
                                (self.product_id.name, self.product_id.qty_minimum)
                        warning_mess = {
                            'title': ('Merci de Verifier Votre Stock!'),
                            'message' : message
                        }
                        return {'warning': warning_mess}

        return {}






class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_qty', 'product_uom')
    def _onchange_product_id_check_availability_alert_max(self):
        if not self.product_id or not self.product_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product = self.product_id.with_context(lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US')
            product_qty_max = self.product_id.qty_maximum
            if product_qty_max != 0.0:

                if product.qty_available + self.product_qty > product_qty_max :
                        message =  ('Le stock de produit %s a dépassé le stock maximum %s.') % \
                                (self.product_id.name, self.product_id.qty_maximum)
                        warning_mess = {
                            'title': ('Merci de Verifier Votre Stock!'),
                            'message' : message
                        }
                        return {'warning': warning_mess}

        return {}

class purchase_custom(models.Model):
    _inherit = 'purchase.order'
    force_stock = fields.Boolean()

    def button_confirm(self):
        res = super(purchase_custom, self).button_confirm()
        lines = self.order_line
        for line in lines:
            if not line.product_id or not line.product_qty or not line.product_uom:
                line.product_packaging = False
                # raise ValidationError (lines.product_id.qty_maximum)
                return res

            if line.product_id.type == 'product':
                precision = line.env['decimal.precision'].precision_get('Product Unit of Measure')
                product = line.product_id.with_context(lang=line.order_id.partner_id.lang or line.env.user.lang or 'en_US')
                product_qty_max = line.product_id.qty_maximum
                # raise ValidationError (product_qty_max)
                if product_qty_max != 0.0:
                    if product.qty_available + line.product_qty > product_qty_max and self.force_stock==False:
                        raise ValidationError ("Le stock de produit " + str(line.product_id.name) +" a dépassé le stock maximum " + str(line.product_id.qty_maximum))
                    else:
                    # raise ValidationError ("pass")
                        return res
