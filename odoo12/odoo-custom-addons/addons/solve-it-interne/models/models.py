from odoo.exceptions import UserError, ValidationError

from odoo import models, fields, api

class report_inherit(models.Model):
    _inherit = 'res.partner'
    RIB = fields.Char()
    N_Siret = fields.Char(size=14)
    NAF = fields.Char()
    N_TVAIC = fields.Integer()
    fax = fields.Char()


    @api.constrains('N_Siret')
    def _check_your_field(self):
        if self.N_Siret:
            if len(self.N_Siret) < 14:
                raise ValidationError('Number of characters must not exceed 14')

class devis_champ(models.Model):
    _inherit = 'sale.order'
    grt = fields.Date()
    liv_date = fields.Date()
    reg_mode = fields.Selection([
        ('esp', 'Espèce'),
        ('chec', 'Chèque'),
        ('traite', 'Traite'),
        ('vir', 'Virement'),
        ])
    @api.multi
    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'confirmation_date': datetime.datetime.strptime(self.validity_date, '%Y-%m-%d').date()
        })

        # Context key 'default_name' is sometimes propagated up to here.
        # We don't need it and it creates issues in the creation of linked records.
        context = self._context.copy()
        context.pop('default_name', None)

        self.with_context(context)._action_confirm()
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()
        return True

class custom_res_company(models.Model):
	_inherit = 'res.company'
	RIB = fields.Char('RIB')
