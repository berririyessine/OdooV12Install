# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'
    exo_tva = fields.Boolean(string='Exonéré de TVA')
    exo_timbre = fields.Boolean(string='Exonéré du Timbre')
    date_limite_tva =  fields.Date(string='Date limite "TVA"')
    date_limite_timbre =  fields.Date(string='Date limite "Timbre"')
    num_attest = fields.Char(String='N° Attest')



class AccountInvoiceInherit(models.Model):
    _inherit = 'account.invoice'

    exo_tva = fields.Boolean(string='Exonéré de TVA', related='partner_id.exo_tva')
    exo_timbre = fields.Boolean(string='Exonéré du Timbre', related='partner_id.exo_timbre')
    date_limite_tva = fields.Date(string='date limite "TVA"', related='partner_id.date_limite_tva')
    date_limite_timbre = fields.Date(string='Date limite "Timbre"', related='partner_id.date_limite_timbre')


    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        super(AccountInvoiceInherit, self)._compute_amount()
        if rec.exo_timbre == True:
            rec.timbre = ''
            rec.amount_total -= rec.amount_timbre
            rec.amount_total_company_signed = rec.amount_total
            pass
        if rec.exo_tva == True:
            rec.amount_tax = 0.0
            for r in rec.tax_line_ids:
                r.amount = 0.0
            rec.amount_total = rec.amount_untaxed - rec.amount_tax
            rec.amount_total += rec.amount_timbre
            pass
