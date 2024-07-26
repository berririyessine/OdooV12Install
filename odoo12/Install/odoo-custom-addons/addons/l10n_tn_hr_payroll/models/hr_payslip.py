# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import babel
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    appears_on_payslip = fields.Boolean(string='Apparaît dans le bulletin de paie', related='salary_rule_id.appears_on_payslip', store=True)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'    
   
    @api.multi
    def action_payslip_cancel(self):
        #res = super(HrPayslip,self).action_payslip_cancel()
        #if self.filtered(lambda slip: slip.state == 'done'):
        #    raise UserError(_("Cannot cancelfdbgsdbsdb a payslip that is done."))
        self.write({'state': 'cancel'})
        return super(HrPayslip, self).action_payslip_cancel()

    struct_id = fields.Many2one('hr.payroll.structure', string='Structure',
        readonly=False, 
        help='Defines the rules that have to be applied to this payslip, accordingly '
             'to the contract chosen. If you let empty the field contract, this field isn\'t '
             'mandatory anymore and thus the rules applied will be all the rules set on the '
             'structure of all contracts of the employee valid for the chosen period')
    name = fields.Char(string='Payslip Name', readonly=False)
    number = fields.Char(string='Reference', readonly=False, copy=False )
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, readonly=False,states={'draft': [('readonly', False)]})
   
    date_from = fields.Date(string='Date From', readonly=False, required=True,  default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_to = fields.Date(string='Date To', readonly=False, required=True,
        default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
    # this is chaos: 4 states are defined, 3 are used ('verify' isn't) and 5 exist ('confirm' seems to have existed)
   
    line_ids = fields.One2many('hr.payslip.line', 'slip_id', string='Payslip Lines', readonly=False )
    company_id = fields.Many2one('res.company', string='Company', readonly=False, copy=False,
        default=lambda self: self.env['res.company']._company_default_get() )
    worked_days_line_ids = fields.One2many('hr.payslip.worked_days', 'payslip_id', string='Payslip Worked Days', copy=True, readonly=False)
    input_line_ids = fields.One2many('hr.payslip.input', 'payslip_id', string='Payslip Inputs',  readonly=False )
    paid = fields.Boolean(string='Made Payment Order ? ', readonly=False, copy=False )
    note = fields.Text(string='Internal Note', readonly=False )
    contract_id = fields.Many2one('hr.contract', string='Contract', readonly=False )
   
    credit_note = fields.Boolean(string='Credit Note', readonly=False,  help="Indicates this payslip has a refund of another")
    payslip_run_id = fields.Many2one('hr.payslip.run', string='Payslip Batches', readonly=False, copy=False )




