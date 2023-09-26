# -*- coding: utf-8 -*-

{
    'name': 'Dhaif Account Payment',
    'category': 'Accounting',
    'summary': 'Dhaif Account Payment',
    'version': '1.0',
    'author': 'Mast',
    'description': """Add PDC date and cleared status
""",
    'depends': ['payment'],
    'data': [
        'views/account_payment_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}
