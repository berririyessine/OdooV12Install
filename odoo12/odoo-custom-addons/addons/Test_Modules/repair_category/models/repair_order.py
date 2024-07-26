from odoo import models, fields


class RepairOrder(models.Model):
    """Extend to category_id field."""

    _inherit = 'repair.order'

    category_id = fields.Many2one('repair.category')
    marque_id = fields.Many2one('repair.marque')
    panne = fields.Char('')
    date_end = fields.Date(string="Date sortie")
    serial_number = fields.Char(string="Numéro de serie")
