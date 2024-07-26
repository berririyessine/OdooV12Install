# -*- coding: utf-8 -*-
{
    'name': "Update Invoice",

    'summary': """
         """,

    'description': """
      
       
    """,

    'author': "",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Tools',
    'version': '3.0',
    'images': ['static/description/icon.png'],

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
#         'security/security.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application':True,
    'installed_version':'3.0',
}