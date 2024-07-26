# -*- encoding: utf-8 -*-

{
    'name' : 'Tunisia - Accounting 12.0',
    'version' : '1.0',
    'author' : 'Maher Jaballi',    
    'summary': 'Manage Chart of Accounts and Taxes template for companies in Tunisia with odoo 12',
    'category' : 'Localization',
    'description': """
This is the base module to manage Chart of Accounts and Taxes template for companies in Tunisia.
=================================================================================================
""",

    'depends': ['base_iban', 'account'],
    'init_xml' : [],
    'data': [
        'data/tn_pcg_taxes.xml',
        'data/plan_comptable_general.xml',
        'data/tn_tax.xml',
        'data/tn_fiscal_templates.xml',        
    ],
    'images': [
		'images/suru_tn.png',
        ],
    'test': [],
    'demo_xml' : [],
    'active': True,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
