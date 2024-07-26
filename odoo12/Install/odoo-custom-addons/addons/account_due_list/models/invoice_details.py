# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

from datetime import datetime,date
from odoo import models, fields, api

class PartnerInvoiceDetails(models.TransientModel):
    _name = 'partner.invoice.details'

    partner_id= fields.Many2one('res.partner',required=True)
    company_id= fields.Many2one('res.company', default=lambda self: self.env['res.company'].browse(self.env['res.company']._company_default_get('partner.invoice.details')).id)

    date_from = fields.Date(string="Date From",default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_to = fields.Date(string="Date To", default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))



    def GenererDetails(self):
        for rec in self:
            import datetime
            DATEFORMAT =  "%Y-%m-%d"


            today = date.today()
            current_date =today.strftime(DATEFORMAT)
            list =[]
            list_sale =[]
            list_purchase =[]
            start_date=datetime.datetime.strptime(str(rec.date_from), "%Y-%m-%d")
            end_date=datetime.datetime.strptime(str(rec.date_to), "%Y-%m-%d")
            date_from= start_date.replace(hour=1, minute=0)
            date_to = end_date.replace(hour=0, minute=0)
            invoice_ids = self.env['account.move.line'].search([('partner_id','=',rec.partner_id.id),('date','>=',rec.date_from),('date','<=',rec.date_to),('account_id.internal_type', 'in', ['receivable', 'payable'])])
            sale_ids = self.env['sale.order'].search([('partner_id','=',rec.partner_id.id),('state', '=', 'sale'), ('confirmation_date','>=',date_from),('confirmation_date','<=',date_to)])
            purchase_ids = self.env['purchase.order'].search([('partner_id', '=', rec.partner_id.id),('state', '=', 'purchase'), ('date_order_copy','>=',date_from),('date_order_copy','<=',date_to)])

            for res in invoice_ids:
                res.echeance_boolean = False
                list.append(res.id)
                # raise ValidationError(str(res.invoice_id.date_due) +" " + str(current_date))
                if (str(res.date_maturity) < str(current_date)) and res.reconciled != True:
                    res.echeance_boolean = True
            for order in sale_ids:
                list_sale.append(order.id)
            for purchase in purchase_ids:
                list_purchase.append(purchase.id)
            detail_ids = self.env['partner.invoice.line'].create({
                "partner_id":rec.partner_id.id,
                "company_id":rec.company_id.id,
                "invoice_ids":[ (6, 0, list)],
                "sale_ids":[ (6, 0, list_sale)],
                "purchase_ids":[ (6, 0, list_purchase)],
            })
            return self.env.ref('account_due_list.rapport_facture_client').report_action(detail_ids)




class PartnerInvoiceDetailsLines(models.Model):
    _name = 'partner.invoice.line'

    partner_id= fields.Many2one('res.partner')
    company_id= fields.Many2one('res.company', default=lambda self: self.env['res.company'].browse(self.env['res.company']._company_default_get('partner.invoice.line')).id)
    invoice_ids = fields.Many2many("account.move.line")
    sale_ids = fields.Many2many("sale.order")
    purchase_ids = fields.Many2many("purchase.order")


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'
    echeance_boolean = fields.Boolean('')
