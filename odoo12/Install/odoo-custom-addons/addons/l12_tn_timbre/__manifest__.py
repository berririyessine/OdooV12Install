# -*- coding: utf-8 -*-

{
    'name': 'Tunisia - Timbre fiscal avec écriture comptable',
    'version': '12.0',
    'author': 'Maher Jaballi',
    'category': 'Accounting',
    'summary': 'Timbre avec écriture comptable',
    'description': """
This is the module to manage the Fiscal Timbre in Odoo.
========================================================================

This module applies to companies based in Tunisia.


""",

    'depends': ['base','account','sale', 'purchase' ,'l12n_tn','retenue_ala_source_tunisie'],
    'data': [

    'data/timbre_data.xml',

    'security/ir.model.access.csv',

    'views/timbre_view.xml',
    'views/sale_view.xml',
    #'views/purchase_views.xml',
    'views/payment_invoice_view.xml',

    'reports/invoice_report.xml',
    'reports/sale_report.xml'

    ],

    'images': ['static/description/banner.jpg'],

    'installable': True,
    'application': False,
    'auto_install': False,
}
