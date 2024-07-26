# -*- coding: utf-8 -*-

{
    'name': 'Account Payment Sale',
    'version': '12',
    'category': 'Sale',

    'summary': "Adds payment on sale orders",

    'depends': [
        'sale','account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/payment_view.xml',

    ],

}
