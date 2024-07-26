# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Invoice Monthly Listing Report',
    'version': '13.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Accounting',
    'description':
        """
        This Module add below functionality into odoo

        1.This odoo application allows you to print print Invoice Monthly Listing Report in excel file\n

    """,
    'summary': 'odoo app will print Monthly/half monthly Invoice Listing Report In Excel, invocie monthly report, invoice monthly listing, monthly due open invoice, paid invoice, invoice xsl report, customer monthly invoice statement, invoice anaylsis, invoice statement',
    'depends': ['account'],
    'data': [
        'wizard/invoice_listing_views.xml',
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':19.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
