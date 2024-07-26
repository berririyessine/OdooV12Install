# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

from datetime import datetime,date
from odoo import models, fields, api

class RetenueType(models.TransientModel):
    _name = 'retenue.type'

class PartnerDetails(models.TransientModel):
    _name = 'partner.details'

    partner_ids= fields.Many2many('res.partner', default=lambda self: self.env['res.partner'].search(['|',('customer','=',True), ('supplier','=',True)]))
    date_from = fields.Date(string="Date From",default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_to = fields.Date(string="Date To", default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))

    company_id= fields.Many2one('res.company', default=lambda self: self.env['res.company'].browse(self.env['res.company']._company_default_get('partner.details')).id)

    def GenererDetails(self):
        for rec in self:
            import datetime
            DATEFORMAT =  "%Y-%m-%d"
            today = date.today()
            current_date =today.strftime(DATEFORMAT)
            list =[]
            total = 0.0
            total_paid = 0.0
            total_reste = 0.0
            # partner_ids = self.env['res.partner'].search([('custoemr','=',True)])
            for partner in rec.partner_ids:
                total = 0.0
                total_paid = 0.0
                total_reste = 0.0
                start_date=datetime.datetime.strptime(str(rec.date_from), "%Y-%m-%d")
                end_date=datetime.datetime.strptime(str(rec.date_to), "%Y-%m-%d")
                date_from= start_date.replace(hour=1, minute=0)
                date_to = end_date.replace(hour=0, minute=0)
                sale_ids = self.env['sale.order'].search([('partner_id', '=', partner.id),('state', '=', 'sale'), ('confirmation_date','>=',date_from),('confirmation_date','<=',date_to)])
                purchase_ids = self.env['purchase.order'].search([('partner_id', '=', partner.id),('state', '=', 'purchase'), ('date_order_copy','>=',date_from),('date_order_copy','<=',date_to)])
                invoice_ids = self.env['account.invoice'].search([('partner_id', '=', partner.id),('date_invoice','>=',rec.date_from),('date_invoice','<=',rec.date_to),('state', 'in',( 'open','paid')),('origin', '=', False),('type', 'in', ['out_invoice', 'in_invoice'])])
                payment_ids = self.env['account.payment'].search([('partner_id', '=', partner.id),('state', 'not in',( 'draft','cancelled'))])
                avoir_ids = self.env['account.invoice'].search([('partner_id', '=', partner.id),('date_invoice','>=',rec.date_from),('date_invoice','<=',rec.date_to),('state', 'in',( 'open','paid')),('origin', '=', False),('type', 'in', ['out_refund', 'in_refund'])])

                if partner.customer == True:
                    for sale in sale_ids:
                        total += sale.amount_total
                else:
                    for purchase in purchase_ids:
                        total += purchase.amount_total
                    # total_reste += sale.resteApayer
                for inv in invoice_ids:
                    total += inv.amount_total
                    # total_reste += inv.residual
                for payment in payment_ids:
                    total_paid += payment.amount
                for avoir in avoir_ids:
                    total_paid += avoir.amount_total
                total_reste = total - total_paid
                if total_reste != 0.0:
                    detail_ids = self.env['partner.detail.line'].create({
                        "partner_id":partner.id,
                        "company_id":rec.company_id.id,
                        "total":total,
                        "total_paid":total_paid,
                        "total_reste":total_reste,
                    })
                    list.append(detail_ids.id)
            # raise ValidationError(str(list))
            detailS_ids = self.env['partner.details.model'].create({
                "company_id":rec.company_id.id,
                "line_details":[ (6, 0, list)],
                "date_from":date_from,
                "date_to":date_to,
            })
            return self.env.ref('account_due_list.rapport_etat_client').report_action(detailS_ids)


class PartnerDetailsLines(models.Model):
    _name = 'partner.detail.line'

    partner_id= fields.Many2one('res.partner')
    company_id= fields.Many2one('res.company', default=lambda self: self.env['res.company'].browse(self.env['res.company']._company_default_get('partner.detail.line')).id)

    total = fields.Float("")
    total_paid = fields.Float("")
    total_reste = fields.Float("")
class PartnerDetailModel(models.Model):
    _name = 'partner.details.model'
    company_id= fields.Many2one('res.company', default=lambda self: self.env['res.company'].browse(self.env['res.company']._company_default_get('partner.details.model')).id)
    line_details = fields.Many2many("partner.detail.line")
    date_from = fields.Date(string="Date From",default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_to = fields.Date(string="Date To", default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))

class ResPartner(models.Model):
    _inherit = 'res.partner'

    solde_partner = fields.Float('', compute='get_total_solde')

    def get_total_solde(self):
        for rec in self:
            import datetime
            list =[]
            total = 0.0
            total_paid = 0.0
            total_reste = 0.0
            total = 0.0
            total_paid = 0.0
            total_reste = 0.0
            invoice_ids = self.env['account.move.line'].search([('partner_id','=',rec.id),('account_id.internal_type', 'in', ['receivable', 'payable'])])
            sale_ids = self.env['sale.order'].search([('partner_id','=',rec.id),('state', '=', 'sale')])
            purchase_ids = self.env['purchase.order'].search([('partner_id', '=', rec.id),('state', '=', 'purchase')])
            # sale_ids = self.env['sale.order'].search([('partner_id', '=', rec.id),('state', '=', 'sale')])
            # purchase_ids = self.env['purchase.order'].search([('partner_id', '=', rec.id),('state', '=', 'purchase')])
            # invoice_ids = self.env['account.invoice'].search([('partner_id', '=', rec.id),('state', 'in',( 'open','paid')),('origin', '=', False)])
            # payment_ids = self.env['account.payment'].search([('partner_id', '=', rec.id),('state', 'not in',( 'draft','cancelled'))])
            if rec.customer == True:
                for sale in sale_ids:
                    total += sale.amount_total
            else:
                for purchase in purchase_ids:
                    total += purchase.amount_total
                # total_reste += sale.resteApayer
            for inv in invoice_ids:
                total += inv.balance
                # total_reste += inv.residual
            # for payment in payment_ids:
            #     total_paid += payment.amount
            rec.solde_partner = total

class PaymentRestPaid(models.Model):
    _inherit = 'account.payment'
    solde_partner = fields.Float(related='partner_id.solde_partner')

class PurchaseRestPaid(models.Model):
    _inherit = 'purchase.order'
    solde_partner = fields.Float(related='partner_id.solde_partner')

class SaleRestPaid(models.Model):
    _inherit = 'sale.order'
    solde_partner = fields.Float(related='partner_id.solde_partner')

# class GradesClient(models.Model):
#     _name = 'grade.client'
#     grade = fields.Char('Grade', required=True)
#     niveau = fields.Char('Niveau', required=True)
#     currency_id = fields.Many2one("res.currency" , string="Currency" )
#     montant = fields.Monetary('Montant', required=True)
#
#
# class res_partner_inherited(models.Model):
#     _inherit = 'res.partner'
#     chiffre_affaire = fields.Monetary("Chiffre d'affaire")
#     grade = fields.Char("Grade")
#     def calc_chiffre_affaire(self):
#         # raise ValidationError ("hi")
#         lev = self.env['grade.client'].search([])
#         m1=m2=m3=m4=m5=m6=m7=m8=m9=m10=1000000000000000
#         g1=g2=g3=g4=g5=g6=g7=g8=g9=g10="a"
#         for rec in lev:
#             if rec.niveau =='1':
#                 g1=rec.grade
#                 m1=rec.montant
#             elif rec.niveau =='2':
#                 g2=rec.grade
#                 m2=rec.montant
#             elif rec.niveau =='3':
#                 g3=rec.grade
#                 m3=rec.montant
#             elif rec.niveau =='4':
#                 g4=rec.grade
#                 m4=rec.montant
#             elif rec.niveau =='5':
#                 g5=rec.grade
#                 m5=rec.montant
#             elif rec.niveau =='6':
#                 g6=rec.grade
#                 m6=rec.montant
#             elif rec.niveau =='7':
#                 g7=rec.grade
#                 m7=rec.montant
#             elif rec.niveau =='8':
#                 g8=rec.grade
#                 m8=rec.montant
#             elif rec.niveau =='9':
#                 g9=rec.grade
#                 m9=rec.montant
#             elif rec.niveau =='10':
#                 g10=rec.grade
#                 m10=rec.montant
#             else:
#                 g11="Inclassifiable"
#                     # if rec.chiffre_affaire<self.env['grade.client'].search([('niveau','=',1)]).montant:
#                     #     grade=self.env['grade.client'].search([('niveau','=',1)]).grade
#         for rec in self.env['res.partner'].search([]):
#             payment_ids = self.env['account.payment'].search([('partner_id', '=', rec.id),('state', 'not in',( 'draft','cancelled'))])
#             # raise ValidationError (payment_ids)
#             for payment in payment_ids:
#                 # raise ValidationError (payment.amount)
#                 rec.chiffre_affaire += payment.amount
#             if rec.chiffre_affaire<m2:
#                 if g1:
#                     rec.grade=g1
#             elif m3>rec.chiffre_affaire>=m2:
#                 if g2:
#                     rec.grade=g2
#             elif m4>rec.chiffre_affaire>=m3:
#                 if g3:
#                     rec.grade=g3
#             elif m5>rec.chiffre_affaire>=m4:
#                 if g4:
#                     rec.grade=g4
#             elif m6>rec.chiffre_affaire>=m5:
#                 if g5:
#                     rec.grade=g5
#             elif m7>rec.chiffre_affaire>=m6:
#                 if g6:
#                     rec.grade=g6
#             elif m8>rec.chiffre_affaire>=m7:
#                 if g7:
#                     rec.grade=g7
#             elif m9>rec.chiffre_affaire>=m8:
#                 if g8:
#                     rec.grade=g8
#             elif m10>rec.chiffre_affaire>=m9:
#                 if g9:
#                     rec.grade=g9
#             else:
#                 if g10:
#                     rec.grade=g10
