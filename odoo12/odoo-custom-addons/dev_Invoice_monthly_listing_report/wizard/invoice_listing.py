# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import models, fields, api, _
from datetime import datetime
from io import BytesIO
import xlwt
from xlwt import easyxf
import base64

class invoice_listing_wizard(models.TransientModel):
    _name = 'invoice.listing.wizard'
    
    @api.model
    def _get_year(self):
        lst = []
        year = datetime.now().today().year
        lst.append((str(year-3),_(str(year-3))))
        lst.append((str(year-2),_(str(year-2))))
        lst.append((str(year-1),_(str(year-1))))
        lst.append((str(year),_(str(year))))
        lst.append((str(year+1),_(str(year+1))))
        lst.append((str(year+2),_(str(year+2))))
        lst.append((str(year+3),_(str(year+3))))
        return lst
    
    @api.model
    def _current_year(self):
        year = datetime.now().today().year
        return str(year)

    year = fields.Selection('_get_year',string='Year',default=_current_year, required="1")
    print_previos_years = fields.Boolean('Print Previous Years')
    company_id = fields.Many2one('res.company', default= lambda self:self.env.user.company_id.id, required="1")
    excel_file = fields.Binary('Excel File')
    filter_by = fields.Selection([('month','Monthly'),('half_month','Half Month')], string='Filter By', default='month', required="1")
    state = fields.Selection([('open','In Payment'),('open_paid','In Payment & Paid')], string='Invoice State', default='open')
    
    def get_style(self):
        main_header_style = easyxf('font:height 300;'
                                   'align: horiz center;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin")
                                   
        header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz center;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")
        
        left_header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz left;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")
        
        text_left = easyxf('font:height 200; align: horiz left;')
        
        text_right = easyxf('font:height 200; align: horiz right;', num_format_str='0.00')
        
        text_left_bold = easyxf('font:height 200; align: horiz right;font:bold True;')
        
        text_right_bold = easyxf('font:height 200; align: horiz right;font:bold True;', num_format_str='0.00') 
        text_center = easyxf('font:height 200; align: horiz center;'
                             "borders: top thin,left thin,right thin,bottom thin")  
        
        return [main_header_style, left_header_style,header_style, text_left, text_right, text_left_bold, text_right_bold, text_center]
        
    
    
    def get_invoice_data(self,user_id, partner_id):
        if self.state == 'open':
            state = ['in_payment']
        else:
            state = ['in_payment','paid']
            
        if self.filter_by == 'month':
            if self.state == 'open':
                query = """select date_part('month', invoice_date) as month, sum(amount_residual) \
                          from account_move  \
                          where invoice_payment_state in %s and  EXTRACT(year FROM "invoice_date") = %s and company_id = %s and \
                          type in ('out_invoice','out_refund') and invoice_user_id = %s and partner_id = %s \
                          group by date_part('month', invoice_date) \
                          order by date_part('month', invoice_date)
                          """
            else:
                query = """select date_part('month', invoice_date) as month, sum(amount_total) \
                          from account_move  \
                          where invoice_payment_state in %s and  EXTRACT(year FROM "invoice_date") = %s and company_id = %s and \
                          type in ('out_invoice','out_refund') and invoice_user_id = %s and partner_id = %s \
                          group by date_part('month', invoice_date) \
                          order by date_part('month', invoice_date)
                          """
                          
        else:
            if self.state == 'open':
                query = """select date_part('month', invoice_date) as month, date_part('day', invoice_date) as day, sum(amount_residual) \
                          from account_move  \
                          where invoice_payment_state in %s and  EXTRACT(year FROM "invoice_date") = %s and company_id = %s and \
                          type in ('out_invoice','out_refund') and invoice_user_id = %s  and partner_id = %s \
                          group by date_part('month', invoice_date), date_part('day', invoice_date) \
                          order by date_part('month', invoice_date)
                          """
            else:
                query = """select date_part('month', invoice_date) as month, date_part('day', invoice_date) as day, sum(amount_total) \
                          from account_move  \
                          where invoice_payment_state in %s and  EXTRACT(year FROM "invoice_date") = %s and company_id = %s and \
                          type in ('out_invoice','out_refund') and invoice_user_id = %s and partner_id = %s \
                          group by date_part('month', invoice_date), date_part('day', invoice_date) \
                          order by date_part('month', invoice_date)
                          """

        params = (tuple(state), self.year, self.company_id.id,user_id, partner_id)

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        return result
        
    def get_before_invoice_data(self,user_id, partner_id):
        if self.state == 'open':
            state = ['in_payment']
        else:
            state = ['in_payment','paid']
            
        if self.state == 'open':
            query = """select sum(amount_residual) from account_move  \
                      where invoice_payment_state in %s and  EXTRACT(year FROM "invoice_date") < %s and company_id = %s and \
                      type in ('out_invoice','out_refund') and invoice_user_id = %s and partner_id = %s """
        else:
            query = """select sum(amount_total) from account_move  \
                      where invoice_payment_state in %s and  EXTRACT(year FROM "invoice_date") < %s and company_id = %s and \
                      type in ('out_invoice','out_refund') and invoice_user_id = %s and partner_id = %s """

        params = (tuple(state), self.year, self.company_id.id, user_id, partner_id)


        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        if result[0].get('sum'):
            return result[0].get('sum')
        else:
            return 0.00
        
    def get_user_partner_id(self):
        if self.state == 'open':
            state = ['in_payment']
        else:
            state = ['in_payment','paid']
        print ("ca=========",self)
        query = """select partner_id, invoice_user_id from account_move \
                  where invoice_payment_state in %s and EXTRACT(year FROM "invoice_date") = %s and company_id = %s and \
                  type in ('out_invoice','out_refund') \
                  group by partner_id, invoice_user_id
                  """
        print ("gg=========")
        params = (tuple(state) ,self.year, self.company_id.id)


        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchall()
        print ("gg=====all====",result)
        return result
        
        
    def create_excel_header(self,worksheet,main_header_style,header_style,text_left):
        worksheet.write_merge(0, 1, 1, 4, 'Monthly Invoice Listing - '+ self.year, main_header_style)
        row = 3
        last_year = str(int(self.year) - 1)
        worksheet.write(row, 0, 'Salesperson', header_style)
        worksheet.write(row, 1, 'Payment Term', header_style)
        worksheet.write(row, 2, 'Customer', header_style)
        col = 2
        if self.print_previos_years:
            worksheet.write(row, col+1, '< '+ last_year, header_style)
        else:
            col = col - 1
        if self.filter_by == 'month':
            worksheet.write(row, col+2, '01 - '+self.year, header_style)
            worksheet.write(row, col+3, '02 - '+self.year, header_style)
            worksheet.write(row, col+4, '03 - '+self.year, header_style)
            worksheet.write(row, col+5, '04 - '+self.year, header_style)
            worksheet.write(row, col+6, '05 - '+self.year, header_style)
            worksheet.write(row, col+7, '06 - '+self.year, header_style)
            worksheet.write(row, col+8, '07 - '+self.year, header_style)
            worksheet.write(row, col+9, '08 - '+self.year, header_style)
            worksheet.write(row, col+10, '09 - '+self.year, header_style)
            worksheet.write(row, col+11, '10 - '+self.year, header_style)
            worksheet.write(row, col+12, '11 - '+self.year, header_style)
            worksheet.write(row, col+13, '12 - '+self.year, header_style)
            worksheet.write(row, col+14, 'TOTAL', header_style)
        else:
            worksheet.write_merge(row,row, col+2, col+3, '01 - '+self.year, header_style)
            worksheet.write(row+1, col+2, '01- 15 Days', header_style)
            worksheet.write(row+1, col+3, '> 16 Days', header_style)
            
            worksheet.write_merge(row,row, col+4, col+5, '02 - '+self.year, header_style)
            worksheet.write(row+1, col+4, '01- 15 Days', header_style)
            worksheet.write(row+1, col+5, '> 16 Days', header_style)
            
            worksheet.write_merge(row,row, col+6, col+7, '03 - '+self.year, header_style)
            worksheet.write(row+1, col+6, '01- 15 Days', header_style)
            worksheet.write(row+1, col+7, '> 16 Days', header_style)
            
            worksheet.write_merge(row,row, col+8, col+9, '04 - '+self.year, header_style)
            worksheet.write(row+1, col+8, '01- 15 Days', header_style)
            worksheet.write(row+1, col+9, '> 16 Days', header_style)
            
            worksheet.write_merge(row,row, col+10, col+11, '05 - '+self.year, header_style)
            worksheet.write(row+1, col+10, '01- 15 Days', header_style)
            worksheet.write(row+1, col+11, '> 16 Days', header_style)
            
            worksheet.write_merge(row,row, col+12, col+13, '06 - '+self.year, header_style)
            worksheet.write(row+1, col+12, '01- 15 Days', header_style)
            worksheet.write(row+1, col+13, '> 16 Days', header_style)
            
            worksheet.write_merge(row,row, col+14, col+15, '07 - '+self.year, header_style)
            worksheet.write(row+1, col+14, '01- 15 Days', header_style)
            worksheet.write(row+1, col+15, '> 16 Days', header_style)
            
            worksheet.write_merge(row,row, col+16, col+17, '08 - '+self.year, header_style)
            worksheet.write(row+1, col+16, '01- 15 Days', header_style)
            worksheet.write(row+1, col+17, '> 16 Days', header_style)
            
            worksheet.write_merge(row,row, col+18, col+19, '09 - '+self.year, header_style)
            worksheet.write(row+1, col+18, '01- 15 Days', header_style)
            worksheet.write(row+1, col+19, '> 16 Days', header_style)
            
            worksheet.write_merge(row,row, col+20, col+21, '10 - '+self.year, header_style)
            worksheet.write(row+1, col+20, '01- 15 Days', header_style)
            worksheet.write(row+1, col+21, '> 16 Days', header_style)
            
            worksheet.write_merge(row,row, col+22, col+23, '11 - '+self.year, header_style)
            worksheet.write(row+1, col+22, '01- 15 Days', header_style)
            worksheet.write(row+1, col+23, '> 16 Days', header_style)
            
            worksheet.write_merge(row,row, col+24, col+25, '12 - '+self.year, header_style)
            worksheet.write(row+1, col+24, '01- 15 Days', header_style)
            worksheet.write(row+1, col+25, '> 16 Days', header_style)
            
            worksheet.write(row, col+26, 'Total', header_style)
        return worksheet, row
        
        
    def get_user_name(self,user_id):
        return self.env['res.users'].sudo().browse(user_id).name
    
    def get_partner_name(self,partner_id,term=False):
        partner = self.env['res.partner'].sudo().browse(partner_id)
        if not term:
            return partner.name
        else:
            return partner.property_payment_term_id and partner.property_payment_term_id.name or ' '
    
    def get_month_val(self, amt_lines, month, split=False):
        if not split:
            for line in amt_lines:
                if int(line.get('month')) == month:
                    return line.get('sum')
            return 0.00
        else:
            v1 = v2 = 0
            
            for line in amt_lines:
                if int(line.get('month')) == month and int(line.get('day')) in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]:
                    v1 += line.get('sum')
                
                if int(line.get('month')) == month and int(line.get('day')) > 15:
                    v2+= line.get('sum')
            return [v1,v2]
                    
    
    def create_table_values(self,worksheet,text_left,text_right,text_right_bold):
        lines = self.get_user_partner_id()
        if self.filter_by == 'month':
            row = 5
        else:
            row = 6
        for line in lines:
            user_name = self.get_user_name(line.get('user_id'))
            partner_name = self.get_partner_name(line.get('partner_id'))
            term = self.get_partner_name(line.get('partner_id'),True)
            worksheet.write(row, 0, user_name, text_left)
            worksheet.write(row, 1, term, text_left)
            worksheet.write(row, 2, partner_name, text_left)
            amt_lines = self.get_invoice_data(line.get('user_id'),line.get('partner_id'))
            
            col = 2
            if self.print_previos_years:
                previos_amount = self.get_before_invoice_data(line.get('user_id'),line.get('partner_id'))
                worksheet.write(row, col+1, previos_amount, text_right)
            else:
                col = col - 1
            if self.filter_by == 'month':
                total = 0
                amount_1 = self.get_month_val(amt_lines, 1)
                worksheet.write(row, col+2, amount_1, text_right)
                amount_2 = self.get_month_val(amt_lines, 2)
                worksheet.write(row, col+3, amount_2, text_right)
                amount_3 = self.get_month_val(amt_lines, 3)
                worksheet.write(row, col+4, amount_3, text_right)
                amount_4 = self.get_month_val(amt_lines, 4)
                worksheet.write(row, col+5, amount_4, text_right)
                amount_5 = self.get_month_val(amt_lines, 5)
                worksheet.write(row, col+6, amount_5, text_right)
                amount_6 = self.get_month_val(amt_lines, 6)
                worksheet.write(row, col+7, amount_6, text_right)
                amount_7 = self.get_month_val(amt_lines, 7)
                worksheet.write(row, col+8, amount_7, text_right)
                amount_8 = self.get_month_val(amt_lines, 8)
                worksheet.write(row, col+9, amount_8, text_right)
                amount_9 = self.get_month_val(amt_lines, 9)
                worksheet.write(row, col+10, amount_9, text_right)
                amount_10 = self.get_month_val(amt_lines, 10)
                worksheet.write(row, col+11, amount_10, text_right)
                amount_11 = self.get_month_val(amt_lines, 11)
                worksheet.write(row, col+12, amount_11, text_right)
                amount_12 = self.get_month_val(amt_lines, 12)
                worksheet.write(row, col+13, amount_12, text_right)
                total = amount_1 + amount_2 + amount_3 + amount_4 + amount_5 + amount_6 + amount_7 + amount_8 + amount_9 + amount_10 + amount_11+ amount_12
                worksheet.write(row, col+14, total, text_right_bold)
                row+=1
            else:
                total = 0
                c = 2
                for i in range(1,13):
                    lst = self.get_month_val(amt_lines, i, split=True)
                    total += lst[0] + lst[1]
                    worksheet.write(row, col+c, lst[0], text_right)
                    c+=1
                    worksheet.write(row, col+c, lst[1], text_right)
                    c+=1
                
                worksheet.write(row, col+c, total, text_right_bold)
                row+=1
        return worksheet, row
        

    def print_excel(self):
        # Style of Excel Sheet 
        excel_style = self.get_style()
        main_header_style = excel_style[0]
        left_header_style = excel_style[1]
        header_style = excel_style[2]
        text_left = excel_style[3]
        text_right = excel_style[4]
        text_left_bold = excel_style[5]
        text_right_bold = excel_style[6]
        text_center = excel_style[7]

        # Define Wookbook and add sheet 
        workbook = xlwt.Workbook()
        filename = 'Invoice Monthly List.xls'
        worksheet = workbook.add_sheet('Invoice Month Listing')
        for i in range(0,120):
            if i == 2 :
                worksheet.col(i).width = 350 * 30
            elif i == 0:
                worksheet.col(i).width = 250 * 30
            elif i == 1:
                worksheet.col(i).width = 180 * 30
            else:
                worksheet.col(i).width = 130 * 30

        # Print Excel Header
        worksheet,row = self.create_excel_header(worksheet,main_header_style,header_style,text_left)
        worksheet, row = self.create_table_values(worksheet,text_left,text_right,text_right_bold)

        #download Excel File
        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        excel_file = base64.encodestring(fp.read())
        fp.close()
        self.write({'excel_file': excel_file})

        if self.excel_file:
            active_id = self.ids[0]
            return {
                'type': 'ir.actions.act_url',
                'url': 'web/content/?model=invoice.listing.wizard&download=true&field=excel_file&id=%s&filename=%s' % (
                    active_id, filename),
                'target': 'new',
            }
    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
