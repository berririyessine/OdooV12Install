from odoo.exceptions import UserError, ValidationError

from odoo import api, models, fields


class AccountPayment(models.Model):
    _inherit = 'account.payment'
    retenue_type = fields.Char('')

    @api.multi
    def cancel(self):
        res = super().cancel()
        for rec in self:
            rec.move_name = ''
        return res

    @api.multi
    def set_to_draft(self):
        for rec in self:
            piece_comptable= self.env['account.move.line'].search([('payment_id', 'in', self.ids)])
            if piece_comptable:
                piece_comptable[0].move_id.unlink()
                self.cancel()
            
