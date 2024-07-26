# -*- coding: utf-8 -*-
{
    'name': "Retenue à la source Tunisie",

    'summary': """
        Le retenue à la source selon les exigences de la loi tunisien""",

    'description': """
        
    """,

    'author': "",  

    'category': 'Accounting',
    'version': '12.0.1',

    'depends': ['base', 'account'],

    'data': [
        'data/retenue_type_data.xml',
        'security/ir.model.access.csv',
        'views/tax_view.xml',
        'views/res_partner.xml',
        'views/account_payment.xml',
        'report/retenue_ala_source.xml'
    ],
    'demo': [
    ],
    'country':'Tunisia',
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'auto_install': False,
}
