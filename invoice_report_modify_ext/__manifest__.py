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
    'depends': ['account','base','dhaif_insurance_service_ext'],
    'data': [
        'views/report_invoice.xml',
        'views/report_templates.xml',
        'views/insurance_report_templates.xml',
        'views/report.xml',
        'views/report_payment_receipt_templates.xml',
        'views/report_sample_orderform.xml',
        'views/insurance_policy_views.xml',
        'wizard/sample_orderform.xml',
        'data/mail_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}

