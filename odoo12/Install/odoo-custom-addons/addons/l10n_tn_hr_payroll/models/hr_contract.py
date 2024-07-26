from odoo import fields, models
from odoo.addons import decimal_precision as dp

class HrContract(models.Model):
    _inherit = 'hr.contract'

    nationalite= fields.Char('Nationalite', size=64)
    qualif= fields.Char('Qualification', size=64)
    niveau= fields.Char('Niveau', size=64)
    coef= fields.Char('Coefficient', size=64)
    type_avance= fields.Selection([('1', 'Une fois/mois'), ('2', 'Suivant salaire')], 'Plafond Avance',
                                    required=True, )
    type_salaire= fields.Selection([('mensuel', 'Mensuel'), ('horaire', 'Horaire')], 'Type Salaire',
                                     required=True, defaut='mensuel')
    prime_pr= fields.Float('Prime de Présence', digits_compute=dp.get_precision('Payroll'))
    prime_trspr= fields.Float('Ind. de Transport', digits_compute=dp.get_precision('Payroll'), default=0.059)
    prime_excep= fields.Float('Primde d encouragement', digits_compute=dp.get_precision('Payroll'))
    prime_risque= fields.Float('Prime de risque', digits_compute=dp.get_precision('Payroll'))
    prime_function= fields.Float('Prime de fonction', digits_compute=dp.get_precision('Payroll'))
    prime_aide= fields.Float('Prime divers', digits_compute=dp.get_precision('Payroll'))
    prime_lait= fields.Float('Primde de lait', digits_compute=dp.get_precision('Payroll'))
    REINV= fields.Float('Reinvestissement', digits_compute=dp.get_precision('Payroll'))
    wage= fields.Float('Wage', digits_compute=dp.get_precision('Payroll'), required=True,
                         help="Basic Salary of the employee")
    number_month= fields.Integer('Number of Month', required=True,default=12)