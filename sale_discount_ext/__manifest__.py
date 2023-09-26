# -*- coding: utf-8 -*-
{
    'name': "Sale Discount Ext",

    'summary': """
        Sale Discount Ext v12.0""",

    'description': """
        
    """,

    'author': "Mast-IT",
    'website': "https://www.mast-it.com/",
    'category': 'Sales Management',
    'version': '1.1.1',
    'depends': ['base', 'sale', 'sale_management'],

    'data': [
        'data/data_account.xml',
        'views/sale_order.xml',
        #'views/account_invoice.xml',
        

    ],
    #'installable': True,
    #'auto_install': False,
    'application': True
}
