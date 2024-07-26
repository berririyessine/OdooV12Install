# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

def retenue_type_get(self):
    return [
            ('prive', u'Privé'),
            ('publique', 'Publique'),
                       ]
class AccountTax(models.Model):
    _inherit = 'account.tax'


    is_retenue = fields.Boolean(string="Retenue à la source")
    retenue_type = fields.Many2one('retenue.type', default=lambda self: self.env['retenue.type'].search([],limit=1))
    is_retenue_tva = fields.Boolean("Retenue TVA", default=False)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'

    def _get_default_retenue(self):
        res = self.env['account.tax'].search([('is_retenue', '=', True)])
        return res and res[0] or False

    retenue_ala_source = fields.Many2one('account.tax',
            ondelete='set null', string=u"Retenue à la source", default=_get_default_retenue, domain=[('is_retenue', '=', True)])

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    retenue_type = fields.Many2one('retenue.type', default=lambda self: self.env['retenue.type'].search([],limit=1))

    @api.one
    @api.depends('journal_id', 'is_retenue', 'amount')
    def _compute_total_retenue(self):
        for inv in self.invoice_ids:
            amount_to_pay = self.amount
            amount_untaxed = inv.amount_untaxed
            amount_tax = inv.amount_tax
            amount_timbre = inv.timbre
            retenue = inv.partner_id.retenue_ala_source
            if retenue and self.is_retenue:
                if amount_to_pay >= inv.amount_total:
                    if retenue.retenue_type == 'prive':
                        total_retenue = (amount_untaxed + amount_tax) * retenue.amount / 100.0
                        self.total_retenue = total_retenue
                    else:
                        for ret in retenue.children_tax_ids:
                            if ret.is_retenue_tva :
                                total_retenue = amount_tax * ret.amount / 100.0
                                self.total_retenue += total_retenue
                                self.retenue_tax += total_retenue
                            else:
                                total_retenue = (amount_untaxed + amount_tax) * ret.amount / 100.0
                                self.total_retenue += total_retenue
                                self.retenue_untaxed += total_retenue
                else:
                    if amount_to_pay >= inv.residual :
                        amount_to_pay-= amount_timbre
                    tax_amount = amount_tax/amount_untaxed
                    payment_tax_amount = amount_to_pay * tax_amount
                    payment_hors_tax_amount = amount_to_pay - payment_tax_amount
                    if retenue.retenue_type == 'prive':
                        total_retenue = (payment_hors_tax_amount + payment_tax_amount) * retenue.amount / 100.0
                        self.total_retenue = total_retenue
                    else:
                        for ret in retenue.children_tax_ids:
                            if ret.is_retenue_tva:
                                total_retenue = payment_tax_amount * ret.amount / 100.0
                                self.total_retenue += total_retenue
                                self.retenue_tax += total_retenue
                            else:
                                total_retenue = (payment_hors_tax_amount + payment_tax_amount) * ret.amount / 100.0
                                self.total_retenue += total_retenue
                                self.retenue_untaxed += total_retenue

        return True




    @api.multi
    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconciliable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:
        	#print("rec",rec)
            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # Use the right sequence to set the name
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
            if not rec.name and rec.payment_type != 'transfer':
                raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            # Create the journal entry
            print("-*/1")
            amount = (rec.amount - rec.total_retenue)  * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            print("-*/2")
            move = rec._create_payment_entry(amount)
            print("-*/3")
            if rec.total_retenue and rec.is_retenue:
                if self.partner_id.retenue_ala_source.retenue_type == 'prive' and rec.total_retenue :
                	#print("-*/31")
                    amount_retenue = rec.total_retenue  * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
                    account_retenue_id = rec.payment_type in ('outbound','transfer') and self.partner_id.retenue_ala_source.account_id.id or self.partner_id.retenue_ala_source.refund_account_id.id
                    if amount_retenue :
                        move_retenue = rec._create_retenue_entry(amount_retenue, account_retenue_id)
                        rec.invoice_ids.total_retenue = rec.total_retenue
                        rec.invoice_ids.retenue_type = rec.retenue_type.id
                        rec.invoice_ids.retenue_ala_source = rec.partner_id.retenue_ala_source.id
                  	#print("31")
                else:
                    for inv in rec.invoice_ids:
                        retenue = inv.partner_id.retenue_ala_source
                    for ret in retenue.children_tax_ids:
                        if ret.is_retenue_tva:
                            amount_retenue = rec.retenue_tax  * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
                            account_retenue_id = rec.payment_type in ('outbound','transfer') and ret.account_id.id or ret.refund_account_id.id
                            if amount_retenue :
                                move_retenue = rec._create_retenue_entry(amount_retenue, account_retenue_id)
                        else:
                            amount_retenue = rec.retenue_untaxed  * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
                            account_retenue_id = rec.payment_type in ('outbound','transfer') and ret.account_id.id or ret.refund_account_id.id
                            if amount_retenue :
                                move_retenue = rec._create_retenue_entry(amount_retenue, account_retenue_id)
                    #print("32")

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            print("-*/4")
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()
                transfer_credit_aml_retenue = move_retenue.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml_retenue = rec._create_transfer_entry(amount_retenue)
                (transfer_credit_aml_retenue + transfer_debit_aml_retenue).reconcile()
            print("-*/5")
            print("-*/6",move.name)
            rec.write({'state': 'posted', 'move_name': move.name})



    def _create_retenue_entry(self, amount, account_id):
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            invoice_currency = self.invoice_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)

        journal_id = self.env['account.journal'].search([('type','=','retenue')],limit=1)
        print("1",journal_id)

        move = self.env['account.move'].create(self._get_move_vals(journal_id))
        print("2",move)

        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        print("3")
        counterpart_aml = aml_obj.create(counterpart_aml_dict)
        print("4")

        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id)[2:]
            total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
            total_payment_company_signed = self.currency_id.with_context(date=self.payment_date).compute(self.amount, self.company_id.currency_id)
            if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
                amount_wo = total_payment_company_signed - total_residual_company_signed
            else:
                amount_wo = total_residual_company_signed - total_payment_company_signed
            if amount_wo > 0:
                debit_wo = amount_wo
                credit_wo = 0.0
                amount_currency_wo = abs(amount_currency_wo)
            else:
                debit_wo = 0.0
                credit_wo = -amount_wo
                amount_currency_wo = -abs(amount_currency_wo)
            writeoff_line['name'] = _('Counterpart')
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            print("5")
            writeoff_line = aml_obj.create(writeoff_line)
            print("6")
            if counterpart_aml['debit']:
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit']:
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo
        self.invoice_ids.register_payment(counterpart_aml)

        #Write counterpart lines
        if not self.currency_id != self.company_id.currency_id:
            amount_currency = 0
        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
        aa = self.env['account.journal'].search([('type','=','retenue')],limit=1)
        print("journal_id-******",journal_id)
        print("aaaaaaaaaaaaa",aa,move.journal_id)
        liquidity_aml_dict.update(self._get_liquidity_retenue_move_line_vals(-amount,account_id,move.journal_id))
        print("7",liquidity_aml_dict)
        aml_obj.create(liquidity_aml_dict)
        print("8")

        move.post()
        print("move",move)
        return move

    def _get_liquidity_retenue_move_line_vals(self, amount, account_id,journal_id):
        name = self.name
        print("journal_id",journal_id)
        if self.payment_type == 'transfer':
            name = _('Transfer to %s') % self.destination_journal_id.name
        vals = {
            'name': name,
            'account_id': account_id,
            'payment_id': self.id,
            'journal_id': journal_id.id,
            'currency_id':self.currency_id.id or False, #self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if journal_id.currency_id and self.currency_id != journal_id.currency_id:
            amount = self.currency_id.with_context(date=self.payment_date).compute(amount, journal_id.currency_id)
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(date=self.payment_date)._compute_amount_fields(amount, journal_id.currency_id, self.company_id.currency_id)
            print("**",amount_currency, journal_id.currency_id.id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': journal_id.currency_id.id,
            })

        print("vals",vals)
        return vals

    is_retenue = fields.Boolean(string="Soumis au retenue", default=False)
    total_retenue = fields.Monetary(string='Total retenue', store=True, readonly=True, compute='_compute_total_retenue')
    retenue_untaxed = fields.Monetary(string='Retenue', store=True, readonly=True, compute='_compute_total_retenue')
    retenue_tax = fields.Monetary(string='Retenue tva', store=True, readonly=True, compute='_compute_total_retenue')

class AccountInvoiceInherit(models.Model):
    _inherit = "account.invoice"

    @api.model
    def validateMF(self,test_str):
        import re
        res = None
        temp = re.search(r'[a-z]', test_str, re.I)
        if temp is not None:
            res = temp.start()
        return str(test_str[:res+1].replace("/",""))

    # retenue_type = fields.Many2one('retenue.type', default=lambda self: self.env['retenue.type'].search([],limit=1))
    total_retenue = fields.Monetary(string='Total retenue', store=True, readonly=True)
    retenue_ala_source = fields.Many2one('account.tax',
            ondelete='set null', string=u"Retenue à la source", domain=[('is_retenue', '=', True)])

class AccountJournal(models.Model):
    _inherit = "account.journal"

    type = fields.Selection([
            ('sale', 'Sale'),
            ('purchase', 'Purchase'),
            ('cash', 'Cash'),
            ('bank', 'Bank'),
            ('retenue', u'Retenue à la source'),
            ('general', 'Miscellaneous'),
        ], required=True,
        help="Select 'Sale' for customer invoices journals.\n"\
        "Select 'Purchase' for vendor bills journals.\n"\
        "Select 'Cash' or 'Bank' for journals that are used in customer or vendor payments.\n"\
        "Select 'General' for miscellaneous operations journals.")


    @api.multi
    def open_action(self):
        """return action based on type for related journals"""
        action_name = self._context.get('action_name', False)
        if not action_name:
            if self.type == 'bank':
                action_name = 'action_bank_statement_tree'
            elif self.type == 'cash':
                action_name = 'action_view_bank_statement_tree'
            elif self.type == 'sale':
                action_name = 'action_invoice_tree1'
            elif self.type == 'purchase':
                action_name = 'action_invoice_tree2'
            else:
                action_name = 'action_move_journal_line'

        _journal_invoice_type_map = {
            ('sale', None): 'out_invoice',
            ('purchase', None): 'in_invoice',
            ('sale', 'refund'): 'out_refund',
            ('purchase', 'refund'): 'in_refund',
            ('bank', None): 'bank',
            ('cash', None): 'cash',
            ('general', None): 'general',
            ('retenue', None): 'general',
        }
        invoice_type = _journal_invoice_type_map[(self.type, self._context.get('invoice_type'))]

        ctx = self._context.copy()
        ctx.pop('group_by', None)
        ctx.update({
            'journal_type': self.type,
            'default_journal_id': self.id,
            'search_default_journal_id': self.id,
            'default_type': invoice_type,
            'type': invoice_type
        })

        [action] = self.env.ref('account.%s' % action_name).read()
        action['context'] = ctx
        action['domain'] = self._context.get('use_domain', [])
        if action_name in ['action_bank_statement_tree', 'action_view_bank_statement_tree']:
            action['views'] = False
            action['view_id'] = False
        return action



class APRetenueType(models.Model):
    _name = "retenue.type"
    name=fields.Char('')
