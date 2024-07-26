# -*- coding: utf-8 -*-

from collections import OrderedDict
import json
import re
import uuid
from functools import partial

from lxml import etree
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_encode

from odoo import api, exceptions, fields, models, _
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils
from odoo.tools.misc import formatLang

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)

# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}

# mapping invoice type to refund type
TYPE2REFUND = {
    'out_invoice': 'out_refund',        # Customer Invoice
    'in_invoice': 'in_refund',          # Vendor Bill
    'out_refund': 'out_invoice',        # Customer Credit Note
    'in_refund': 'in_invoice',          # Vendor Credit Note
}

MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')

class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = 'account.invoice'

    @api.model
    def _default_currency(self):
        journal = self._default_journal()
        return journal.currency_id or journal.company_id.currency_id or self.env.user.company_id.currency_id

    @api.model
    def _default_journal(self):
        if self._context.get('default_journal_id', False):
            return self.env['account.journal'].browse(self._context.get('default_journal_id'))
        inv_type = self._context.get('type', 'out_invoice')
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [
            ('type', 'in', [TYPE2JOURNAL[ty] for ty in inv_types if ty in TYPE2JOURNAL]),
            ('company_id', '=', company_id),
        ]
        company_currency_id = self.env['res.company'].browse(company_id).currency_id.id
        currency_id = self._context.get('default_currency_id') or company_currency_id
        currency_clause = [('currency_id', '=', currency_id)]
        if currency_id == company_currency_id:
            currency_clause = ['|', ('currency_id', '=', False)] + currency_clause
        return (
            self.env['account.journal'].search(domain + currency_clause, limit=1)
            or self.env['account.journal'].search(domain, limit=1)
        )

    name = fields.Char(string='Reference/Description', index=True,  readonly=False,  copy=False, help='The name that will be used on account move lines')

    origin = fields.Char(string='Source Document', help="Reference of the document that produced this invoice.", readonly=False )
 
    
    reference = fields.Char(string='Payment Ref.', copy=False, readonly=False,  help='The payment communication that will be automatically populated once the invoice validation. You can also write a free communication.')
    comment = fields.Text('Additional Information', readonly=False, )

    date_invoice = fields.Date(string='Invoice Date', readonly=False,  index=True, help="Keep empty to use the current date", copy=False)
    date_due = fields.Date(string='Due Date',readonly=False,  index=True, copy=False,
        help="If you use payment terms, the due date will be computed automatically at the generation "
             "of accounting entries. The Payment terms may compute several due dates, for example 50% "
             "now and 50% in one month, but if you want to force a due date, make sure that the payment "
             "term is not set on the invoice. If you keep the Payment terms and the due date empty, it "
             "means direct payment.")
    partner_id = fields.Many2one('res.partner', string='Partner', change_default=True,    readonly=False,   track_visibility='always', ondelete='restrict', help="You can find a contact by its Name, TIN, Email or Internal Reference.")
   
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', oldname='payment_term',
        readonly=False, 
        help="If you use payment terms, the due date will be computed automatically at the generation "
             "of accounting entries. If you keep the payment terms and the due date empty, it means direct payment. "
             "The payment terms may compute several due dates, for example 50% now, 50% in one month.")
    date = fields.Date(string='Accounting Date',
        copy=False,
        help="Keep empty to use the invoice date.",
        readonly=False )

    account_id = fields.Many2one('account.account', string='Account',
        readonly=False,   domain=[('deprecated', '=', False)], help="The partner account used for this invoice.")
    invoice_line_ids = fields.One2many('account.invoice.line', 'invoice_id', string='Invoice Lines', oldname='invoice_line',
        readonly=False,  copy=True)
    tax_line_ids = fields.One2many('account.invoice.tax', 'invoice_id', string='Tax Lines', oldname='tax_line',
        readonly=False,  copy=True)
    
   
    currency_id = fields.Many2one('res.currency', string='Currency',
        required=True, readonly=False, 
        default=_default_currency, track_visibility='always')
    
    journal_id = fields.Many2one('account.journal', string='Journal',
        required=True, readonly=False, 
        default=_default_journal,
        domain="[('type', 'in', {'out_invoice': ['sale'], 'out_refund': ['sale'], 'in_refund': ['purchase'], 'in_invoice': ['purchase']}.get(type, [])), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, readonly=False,    default=lambda self: self.env['res.company']._company_default_get('account.invoice'))

    
    partner_bank_id = fields.Many2one('res.partner.bank', string='Bank Account',
        help='Bank Account Number to which the invoice will be paid. A Company bank account if this is a Customer Invoice or Vendor Credit Note, otherwise a Partner bank account number.',
        readonly=False ) #Default value computed in default_get for out_invoices

    
    user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
        readonly=False,         default=lambda self: self.env.user, copy=False)
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', oldname='fiscal_position',   readonly=False )
  
    cash_rounding_id = fields.Many2one('account.cash.rounding', string='Cash Rounding Method',
        readonly=False, help='Defines the smallest coinage of the currency that can be used to pay by cash.')



   