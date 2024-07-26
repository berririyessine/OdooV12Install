# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-today Ascetic Business Solution <www.asceticbs.com>
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
from odoo import api,fields,models,_

class Employee(models.Model):
    _inherit = "hr.employee"

    repair_order_count = fields.Integer(string='Repairs',compute='_compute_repair_order_count')
    
    #view of repair order
    def action_view(self):
        sale_date= self.env['repair.order'].search([('user_id','=',self.user_id.id),('state','=','confirmed')])
        return { 
                'name': ('Repair'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'repair.order',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain':[('user_id','=',self.user_id.id),('state','=','confirmed')],
                }

    #compute method of repair order count
    def _compute_repair_order_count(self):
        count = self.env['repair.order'].search_count([('user_id','=',self.user_id.id),('state','=','confirmed')])
        self.repair_order_count = count
  
    
