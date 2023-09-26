# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
    
{
    'name': 'Invoice Report Modify',
    'version': '1.1',
    'category': 'Invoices & Payments',
    'summary': 'Invoices & Payments',
    'description': """
This module for modify invoice report.
    """,
    'depends': ['account','base'],
    'data': [
        'views/report_invoice.xml',
        'views/report_templates.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}

