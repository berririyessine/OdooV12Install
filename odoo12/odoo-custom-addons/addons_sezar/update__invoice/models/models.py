# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class test(models.Model):
    _name = "test"
    @api.model
    def modif_journal(self):
        # print "*************************newwwwww"
        jr=self.env['account.journal'].search([('id','=',1)])
        
        if jr : 
#             if len(jr)!=0:
            jr[0].refund_sequence=True
                
                
class InvoiceInherited(models.Model):
    _inherit = "account.invoice"
    _sql_constraints = [
        ('number_uniq',  'CHECK(1=1)', 'Invoice Number must be unique per Company!'),
    ] 
    
    #@api.multi
    def Return_To_Dratf_State(self):
        self.ensure_one()
        self.write({'state': 'draft'})
        mov = self.env['account.move'].search([('id','=',self.move_id.id)])
        invoice=self.env['account.invoice'].search([('id','=',self.id)])
        invoice.move_id=False
        mov.sudo().unlink()

           
    @api.model
    def create(self, vals):
        jr=self.env['account.journal'].search([('id','=',1)])
        jr2=self.env['account.journal'].search([('id','=',2)])
        if jr : 
            jr[0].refund_sequence=True
        if jr2 : 
            jr2[0].refund_sequence=True
        invoice=super(InvoiceInherited,self).create(vals)
        return invoice
#         if invoice.origin and invoice.name:
#             invoice.move_name=invoice.origin
#         return invoice
#     @api.onchange('origin')
#     def get_move_name(self):
#         try:
#             if self.origin:
#                 self.move_name=self.origin
#                 print('**move_name**')
#                 print(self.move_name)
#         except Exception , e:
#             print (e.message+'*******')
#             print('move name exception')
#             
#             
#     @api.multi
#     def action_invoice_open(self):
#         if self.move_name:
#             invoice=self.env['account.invoice'].search([('number','=',self.move_name),('is_modified','=',True)])
#             if invoice:
#                 lines=self.env['account.move.line'].search([('invoice_id','=',invoice.id)])
#                 if lines:
#                     for line in lines:
#                         line.sudo().unlink()
#                 invoice.active=False
#         # lots of duplicate calls to action_invoice_open, so we remove those already open
#         to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
#         if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft']):
#             raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))
#         to_open_invoices.action_date_assign()
#         to_open_invoices.action_move_create()
#         return to_open_invoices.invoice_validate()
    
    
    
class AccountMoveLine(models.Model):
    _inherit ='account.move.line'
     
    @api.multi
    def _update_check(self):
        """ Raise Warning to cause rollback if the move is posted, some entries are reconciled or the move is older than the lock date"""
        move_ids = set()
        for line in self:
            err_msg = _('Move name (id): %s (%s)') % (line.move_id.name, str(line.move_id.id))
#             if line.move_id.state != 'draft':
#                 raise UserError(_('You cannot do this modification on a posted journal entry, you can just change some non legal fields. You must revert the journal entry to cancel it.\n%s.') % err_msg)
            if line.reconciled and not (line.debit == 0 and line.credit == 0):
                raise UserError(_('You cannot do this modification on a reconciled entry. You can just change some non legal fields or you must unreconcile first.\n%s.') % err_msg)
            if line.move_id.id not in move_ids:
                move_ids.add(line.move_id.id)
        self.env['account.move'].browse(list(move_ids))._check_lock_date()
        return True
     
#     
class AccountMove(models.Model):
    _inherit ='account.move'
         
    @api.multi
    def assert_balanced(self):
        if not self.ids:
            return True
        prec = self.env['decimal.precision'].precision_get('Account')
 
        self._cr.execute("""\
            SELECT      move_id
            FROM        account_move_line
            WHERE       move_id in %s
            GROUP BY    move_id
            HAVING      abs(sum(debit) - sum(credit)) > %s
            """, (tuple(self.ids), 10 ** (-max(5, prec))))
#         if len(self._cr.fetchall()) != 0:
#             raise UserError(_("Cannot create unbalanced journal entry."))
        return True
