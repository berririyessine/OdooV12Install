# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payments Due list',
    'version': '11.0.2.0.0',
    'category': 'Generic Modules/Payment',
    'author': 'Odoo Community Association (OCA)',
    'summary': 'Check printing commons',
    'website': 'https://github.com/OCA/account-payment',
    'license': 'LGPL-3',
    'depends': ['account','sale','purchase','contacts'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/payment_view.xml',
        'views/partner_invoice_view.xml',
        'views/partner_state.xml',
        'report/detaille_invoice_report.xml',
        'report/report_etat_partner.xml',

    ],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'auto_install': False,
}
