# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016 rhfree (<http://rhfree.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Payroll - Tunisia',
    'category': 'Human Resources',
    'author': 'Maher Jaballi',
    "license": "AGPL-3",
    "version": "12.0.0",
    'depends': ['hr_payroll'],

    'description': """Tunisien Payroll Rules Basic Version.
======================

    - Configuration of hr_payroll for Tunisien localization
    - Basic configuration for newly installed company
    - Absence - Advances - CNSS - AMO
    - Pro version is complete and  handles all kinds of allowances and Bonuses, plus 
          .
    - Important: you need to fill the wage amount for the employee in the contract and chose Tunisien payroll from the structure field.
    """,
    'data': [
        'data/l10n_tn_hr_payroll_data.xml',
        'views/hr_contract_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_payslip_views.xml',
        'views/res_company_views.xml',
    ],
     'installable': True,
     "images":['static/description/Banner.png'],
}
