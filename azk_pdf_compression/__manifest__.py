# -*- coding: utf-8 -*-
{
    'name': "PDF Attachment Compression",
    
    'summary': """Compress PDF Attachments based on model, size and age in addition to select the output quality""",

    'description': """
        This module includes:
        - A rules model to specify the attachment compression rules
        - A scheduled action to run the active compression rules
        - Option to run individual rules from server actions
    """,
    
    'author': "Mast",
    'website': "https://mast-it.com",
    "license": "AGPL-3",
    "price": 30.00,
    "currency": "USD",
    'category': 'Tools',
    'version': '12.0.0.0',
    'application': False,
    
    'depends': ['base','mail'],

    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/compression_rules_view.xml',
        'wizard/debug_rule.xml',
        'wizard/message_wizard.xml',
    ],
    'images': ['static/description/banner.gif'],
}
