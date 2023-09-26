# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
    
{
    'name': 'Sayed Saleh Custom Reports',
    'version': '1.1',
    'author': 'Mast-IT Bahrain',
    'category': 'Sales',
    'summary': 'Sayed Saleh Custom Reports',
    'description': """
This module for modify reports.
    """,
    'depends': ['sale','account','stock','sale_discount_ext','point_of_sale','purchase'],
    'data': [
        'data/report_paperformat_data.xml',
        'report/report_invoice.xml',
        'report/sale_report_templates.xml',
        'report/purchase_order_templates.xml',
        'report/report_deliveryslip.xml',
        'report/report_payment_receipt_templates.xml',
        'report/report.xml',
        'report/point_of_sale_report.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True
}

