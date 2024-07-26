# -*- coding: utf-8 -*-
{
    'name': "stock_specific",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','stock','sale','stock_3dview','purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/stock_location_view_inherit.xml',
        'views/purchase_order_view_inherit.xml',
        'views/sale_ordre_inherit_view.xml',
        'report/etat_stock_emplacement.xml',
        'report/inherit_bn_reception.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}