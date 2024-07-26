# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-Today Ascetic Business Solution <www.asceticbs.com>
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
#################################################################################
{
   'name':"Repair Order Summary",
   'author':"Ascetic Business Solution",
   'category':"Sales",
   'summary':"""Repair Summary""",
   'website':"http://www.asceticbs.com",
   'description':"""Repair Summary""" ,

   'version' : '12.0.1.0',
   'depends' : ['repair','hr'],
   'license'     : 'AGPL-3',
   'data':[ 'views/repair_order_view.xml',
            'views/hr_employee_view.xml',
            'wizard/employee_order_view.xml',
            'Report/repair_order_report_action.xml',
            'Report/repair_order_report_template.xml',      
  ],
    'images': ['static/description/banner.png'],
    'installable':True,
    'application':True,
    'auto_install':False,

}
