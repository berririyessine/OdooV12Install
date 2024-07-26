# -*- coding: utf-8 -*-

{
    'name': 'Account Payment Purchase',
    'version': '12',
    'category': 'Purchase',

    'summary': "Adds payment on purchase orders",

    'depends': [
        'purchase','account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/purchse_order_view.xml',
        'views/payment_view.xml',

    ],

}
