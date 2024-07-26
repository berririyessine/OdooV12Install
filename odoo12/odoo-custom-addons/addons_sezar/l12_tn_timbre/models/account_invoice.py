# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError,UserError
from odoo import fields, models, api,_
class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'
    exo_tva = fields.Boolean(string='Exonéré de TVA')
    exo_timbre = fields.Boolean(string='Exonéré du Timbre')
    date_limite_tva =  fields.Date(string='Date limite "TVA"')
    date_limite_timbre =  fields.Date(string='Date limite "Timbre"')
    num_attest = fields.Char(String='N° Attest')


class AccountInnvoice(models.Model):
    _inherit = "account.invoice"

    exo_tva = fields.Boolean(string='Exonéré de TVA', related='partner_id.exo_tva')
    exo_timbre = fields.Boolean(string='Exonéré du Timbre', related='partner_id.exo_timbre')
    date_limite_tva = fields.Date(string='date limite "TVA"', related='partner_id.date_limite_tva')
    date_limite_timbre = fields.Date(string='Date limite "Timbre"', related='partner_id.date_limite_timbre')
    matched_debit_ids = fields.Many2many('account.partial.reconcile',  string='Matched Debits',)
    line_ids = fields.One2many('account.move.line', 'move_id', string='Journal Items', copy=True, readonly=True,
        states={'draft': [('readonly', False)]})

    # def button_draft(self):
    #     self.ensure_one()
    #     self.write({'state': 'draft'})
    #     query = "DELETE FROM account_move_line WHERE move_id="+str(self.move_id.id)
    #     self._cr.execute(query)
    #
    # def button_draft(self):
    #     self.ensure_one()
    #     self.write({'state': 'draft'})
    #     mov = self.env['account.move'].search([('id','=',self.move_id.id)])
    #     invoice=self.env['account.invoice'].search([('id','=',self.id)])
    #     invoice.move_id=False
    #     mov.sudo().unlink()

        # AccountMoveLine = self.env['account.move.line'].search([('move_id', '=', self.move_id.id)])
        # # excluded_move_ids = []
        # #
        # # excluded_move_ids = AccountMoveLine.search([('move_id', '=', self.move_id.id)])
        # # raise ValidationError(str(excluded_move_ids))
        # # for move in self:
        # #     # if move in move.line_ids.mapped('full_reconcile_id.exchange_move_id'):
        # #     #     raise UserError(_('You cannot reset to draft an exchange difference journal entry.'))
        # #     # if move.tax_cash_basis_rec_id:
        # #     #     raise UserError(_('You cannot reset to draft a tax cash basis journal entry.'))
        # #     # if move.restrict_mode_hash_table and move.state == 'posted' and move.id not in excluded_move_ids:
        # #     #     raise UserError(_('You cannot modify a posted entry of this journal because it is in strict mode.'))
        # #     # We remove all the analytics entries for this journal
        # #     raise ValidationError(str(move.mapped('line_ids')))
        # #     move.mapped('line_ids.analytic_line_ids').unlink()
        # # excluded_move_ids = AccountMoveLine.search([('move_id', '=', self.move_id.id)])
        # # raise ValidationError(str(AccountMoveLine))
        #
        #
        # # raise ValidationError(str(AccountMoveLine))
        #
        # self.mapped('line_ids').remove_move_reconcile()
        # for move in AccountMoveLine:
        #     move.sudo().unlink()
        # self.write({'state': 'draft'})


    @api.one
    @api.depends('timbre_fiscal','amount_total')
    def _amount_timbre(self):
        for order in self:
            amount_timbre = order.amount_untaxed + order.amount_tax
            if order.timbre_fiscal  == True:
               timbre = self.env['config.timbre']._timbre(order.amount_untaxed + order.amount_tax)
               self.timbre = timbre['timbre']


    # inherited method from account invoice model
    @api.onchange('partner_id','invoice_line_ids')
    def onchange_timbre(self):
        for order in self:
            if order.exo_timbre == True:
                order.timbre_fiscal=False
            if order.exo_tva == True:
                order.amount_tax = 0.0
                for rec in order.tax_line_ids:
                    rec.amount = 0.0


    @api.one
    @api.depends('payment_term_id','invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'timbre_fiscal','company_id', 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount) for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        for order in self:
            amount_timbre = order.amount_total
            if order.timbre_fiscal  == True:
                timbre = self.env['config.timbre']._timbre(amount_timbre)
                self.timbre = timbre['timbre']
                self.amount_total = timbre['amount_timbre']
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign




    timbre = fields.Monetary(string='Timbre', store=True, readonly=True,
                             compute='_amount_timbre', track_visibility='onchange')
    timbre_fiscal = fields.Boolean(string="Droit de timbre",default=True)


    # Creates invoice related analytics and financial move lines
    @api.multi
    def action_move_create(self):
        if self.move_name == False:
            account_move = self.env['account.move']

            for inv in self:
                if not inv.journal_id.sequence_id:
                    raise UserError(_('Please define sequence on the journal related to this invoice.'))
                if not inv.invoice_line_ids:
                    raise UserError(_('Please create some invoice lines.'))
                if inv.move_id:
                    continue

                ctx = dict(self._context, lang=inv.partner_id.lang)

                if not inv.date_invoice:
                    inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
                company_currency = inv.company_id.currency_id

                iml = inv.invoice_line_move_line_get()
                iml += inv.tax_line_move_line_get()
                # create timbre line in account move line
                iml += inv.timbre_line_move_line_get()

                diff_currency = inv.currency_id != company_currency
                total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

                name = inv.name or '/'
                if inv.payment_term_id:
                    totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                    res_amount_currency = total_currency
                    ctx['date'] = inv._get_currency_rate_date()
                    for i, t in enumerate(totlines):
                        if inv.currency_id != company_currency:
                            amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                        else:
                            amount_currency = False

                        # last line: add the diff
                        res_amount_currency -= amount_currency or 0
                        if i + 1 == len(totlines):
                            amount_currency += res_amount_currency

                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': t[1],
                            'account_id': inv.account_id.id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                else:
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': total,
                        'account_id': inv.account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
                line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
                line = inv.group_lines(iml, line)

                journal = inv.journal_id.with_context(ctx)
                line = inv.finalize_invoice_move_lines(line)

                date = inv.date or inv.date_invoice
                move_vals = {
                    'ref': inv.reference,
                    'line_ids': line,
                    'journal_id': journal.id,
                    'date': date,
                    'narration': inv.comment,
                }
                ctx['company_id'] = inv.company_id.id
                ctx['invoice'] = inv
                ctx_nolang = ctx.copy()
                ctx_nolang.pop('lang', None)
                move = account_move.with_context(ctx_nolang).create(move_vals)
                # Pass invoice in context in method post: used if you want to get the same
                # account move reference when creating the same invoice after a cancelled one:
                move.post()
                # make the invoice point to that move
                vals = {
                    'move_id': move.id,
                    'date': date,
                    'move_name': move.name,
                }
                inv.with_context(ctx).write(vals)
        else:
            # raise ValidationError('ok')
            account_move = self.env['account.move']
            for inv in self:
                if not inv.journal_id.sequence_id:
                    raise UserError(_('Please define sequence on the journal related to this invoice.'))
                if not inv.invoice_line_ids:
                    raise UserError(_('Please create some invoice lines.'))
                if inv.move_id:
                    continue

                ctx = dict(self._context, lang=inv.partner_id.lang)

                if not inv.date_invoice:
                    inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
                company_currency = inv.company_id.currency_id

                iml = inv.invoice_line_move_line_get()
                iml += inv.tax_line_move_line_get()
                # create timbre line in account move line
                iml += inv.timbre_line_move_line_get()

                diff_currency = inv.currency_id != company_currency
                total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

                name = inv.move_name
                if inv.payment_term_id:
                    totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                    res_amount_currency = total_currency
                    ctx['date'] = inv._get_currency_rate_date()
                    for i, t in enumerate(totlines):
                        if inv.currency_id != company_currency:
                            amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                        else:
                            amount_currency = False

                        # last line: add the diff
                        res_amount_currency -= amount_currency or 0
                        if i + 1 == len(totlines):
                            amount_currency += res_amount_currency

                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': t[1],
                            'account_id': inv.account_id.id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                else:
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': total,
                        'account_id': inv.account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
                line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
                line = inv.group_lines(iml, line)

                journal = inv.journal_id.with_context(ctx)
                line = inv.finalize_invoice_move_lines(line)

                date = inv.date or inv.date_invoice
                move_vals = {
                    'ref': inv.reference,
                    'line_ids': line,
                    'journal_id': journal.id,
                    'date': date,
                    'narration': inv.comment,
                }
                ctx['company_id'] = inv.company_id.id
                ctx['invoice'] = inv
                ctx_nolang = ctx.copy()
                ctx_nolang.pop('lang', None)
                move = account_move.with_context(ctx_nolang).create(move_vals)
                # Pass invoice in context in method post: used if you want to get the same
                # account move reference when creating the same invoice after a cancelled one:
                # move.post()
                # make the invoice point to that move
                vals = {
                    'move_id': move.id,
                    'date': date,
                    'move_name': self.move_name,
                }
                inv.with_context(ctx).write(vals)
                inv.move_id.write({'name':self.move_name})
                inv.move_id.action_post()
                                # move.name = self.move_name

        return True

    # create timbre line in account move line
    @api.model
    def timbre_line_move_line_get(self):
        res = []
        timbre_account = self.env['config.timbre'].search([('name','=','Timbre Fiscal')]).account_id.id
        if not timbre_account:
            raise ValidationError("Compte De Droit d’enregistrement n'est pas paramétré. \n Allez dans Comptabilité/Configuration/Comptablité/Configuration Timbre")
        for record in self:
            if record.timbre_fiscal  == True:

                res.append({
                    'type': 'tax',
                    'name': 'Timbre',
                    'price_unit': self.timbre,
                    'quantity': 1,
                    'price': self.timbre,
                    'account_id': timbre_account,
                    #'account_analytic_id': tax_line.account_analytic_id.id,
                    'invoice_id': self.id,
                })
        return res
# class AccountMoveLine(models.Model):
#     _inherit ='account.move.line'
#
#     @api.multi
#     def _update_check(self):
#         """ Raise Warning to cause rollback if the move is posted, some entries are reconciled or the move is older than the lock date"""
#         move_ids = set()
#         for line in self:
#             err_msg = _('Move name (id): %s (%s)') % (line.move_id.name, str(line.move_id.id))
#             # if line.move_id.state != 'draft':
#                 # raise UserError(_('You cannot do this modification on a posted journal entry, you can just change some non legal fields. You must revert the journal entry to cancel it.\n%s.') % err_msg)
#             if line.reconciled and not (line.debit == 0 and line.credit == 0):
#                 raise UserError(_('You cannot do this modification on a reconciled entry. You can just change some non legal fields or you must unreconcile first.\n%s.') % err_msg)
#             if line.move_id.id not in move_ids:
#                 move_ids.add(line.move_id.id)
#         self.env['account.move'].browse(list(move_ids))._check_lock_date()
#         return True
# class AccountMove(models.Model):
#     _inherit ='account.move'
#
#     @api.multi
#     def assert_balanced(self):
#         if not self.ids:
#             return True
#         prec = self.env['decimal.precision'].precision_get('Account')
#
#         self._cr.execute("""\
#             SELECT      move_id
#             FROM        account_move_line
#             WHERE       move_id in %s
#             GROUP BY    move_id
#             HAVING      abs(sum(debit) - sum(credit)) > %s
#             """, (tuple(self.ids), 10 ** (-max(5, prec))))
# #         if len(self._cr.fetchall()) != 0:
# #             raise UserError(_("Cannot create unbalanced journal entry."))
#         return True

class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'
    num = fields.Char('N°')
    date = fields.Date('Date')
    banq = fields.Selection([ ('STB', 'STB'),('BNA', 'BNA' ),('BH', 'BH'),('BFPME', 'BFPME'),('BTS', 'BTS'),('BTE', 'BTE'),('BTL', 'BTL'),('TSB', 'TSB'),
            ('Zitouna', 'Zitouna'),('Al_Baraka', 'Al Baraka'),('Al_Wifak', 'Al Wifak'),('Amen_Bank', 'Amen Bank'),('Attijari_Bank', 'Attijari Bank'),('ATB', 'ATB'),('ABC', 'ABC'),
            ('BIAT', 'BIAT'),('BT', 'BT'),('BTK', 'BTK'),('BFT', 'BFT'),('Citi_Bank', 'Citi Bank'),('QNB_Tunis', 'QNB Tunis'),('UBCI', 'UBCI'),('UIB', 'UIB')],default='STB')
    check_bool = fields.Boolean('')

    @api.onchange('journal_id')
    def onchange_visible(self):
        if self.journal_id.checkInfo:
            self.check_bool = True
            # print(self.test_bool)
        else:
            self.check_bool = False

class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'
    checkInfo = fields.Boolean(string="info supp" ,default=False)
