# -*- coding: utf-8 -*-
{
    'name': "custom_print_format",
    'version':'12.0.0.1',
    'summary': """
        Custom Invoice Report
        """,
    'description': """
        This is a customized Invoice,Delivery Note print out...
    """,

    'author': "MAST IT",
    'license': "LGPL-3",
    'website': "https://www.mast-it.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['web', 'account','stock','point_of_sale'],

    'data': [
        'views/account_invoice_view.xml',
        'views/sale_order_view.xml',
        'views/inherited_invoice_report.xml',
        #'views/delivery_report.xml',
        'views/delivery_report_sale.xml',
        'views/report.xml',
        'views/report_invoice.xml',
        'views/point_of_sale_report.xml',

    ],
    'installable': True,
    'application': True,
    
}
