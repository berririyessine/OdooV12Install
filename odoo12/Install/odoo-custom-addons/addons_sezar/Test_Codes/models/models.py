from odoo.exceptions import UserError, ValidationError

from odoo import models, fields, api

    _inherit = 'product.product'

    # @api.onchange('categ_id','type')
    # def compute_code_a_barre(self):
    #     for rec in self:
    #         if rec.purchase_ok == True and rec.type == 'product':
    #             if rec.categ_id:
    #                 rec.barcode = str(rec.categ_id.code) + str(rec.categ_id.next_number).zfill(8)
class Documents_Inherit(models.Model):
    _inherit = 'muk_dms.file'
    code = fields.Char((string="Code Document"))
    sequence = fields.Char (string = "Number", readonly=true, requierder=true, copy=false, index=true, default= 8 self:_('New'))


    @api.model
    def create(self, vals):
    	if vals.get('sequence', 'New') == 'New' :
           		 vals['sequence'] = self.env['ir.sequence'].next_by_code ('self.service') or 'New'
    	result = super ().create(vals)
        return result

    # @api.model
    # @api.returns('self', lambda value: value.id)
    # def create(self, vals):
    #     categorie= self.env['product.category'].search([('id','=',vals['categ_id'])])
    #     # raise ValidationError(str(categorie.name))
    #     categorie.write({'next_number' : categorie.next_number+1})
    #     # return super(ProductTemplate, self).create(vals)
