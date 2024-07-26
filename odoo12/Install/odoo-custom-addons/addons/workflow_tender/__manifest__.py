# -*- coding: utf-8 -*-
{
    'name': "workflow_tender",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','sale','account'],

    # always loaded
    'data': [
        'security/security.xml',
        'data/prospection_stage_data.xml',
        'views/templates.xml',
        'views/appel_offre_physique.xml',
        'views/appel_offre_tuneps.xml',
        'views/questionnaire_technique.xml',
        'views/prospection_view.xml',
        'views/preparation_config.xml',
        'views/stage_view.xml',
        'views/workflow_view.xml',
        'views/devis_inherit_view.xml',
        'views/invoice_inherit_view.xml',
        'views/menu_view.xml',

    ],
    'qweb': ['static/src/xml/add_button.xml'],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}