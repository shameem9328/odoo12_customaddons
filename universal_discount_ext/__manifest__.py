# -*- coding: utf-8 -*-
{
    'name': "Universal Discount Ext",

    'summary': """
        Universal Discount v12.0""",

    'description': """
        - Apply a field in Insurance and Invoice module to calculate discount after the order lines are inserted.
        - Can be enabled from (**Note** : Charts of Accounts must be installed).
             
             Settings -> general settings -> invoice 
        
        - Maintains the global tax entries in accounts specified by you (**Note** : To see journal entries in Invoicing:
         (in debug mode) 
             
             Settings -> users -> select user -> Check "Show Full Accounting Features")
        
        - Maintains the global discount entries in accounts specified by you.
        - Label given to you will be used as name given to discount field.
        - Also update the report PDF printout with global discount value.
    """,

    'author': "Mast-IT",
    'category': 'Sales Management',
    'version': '1.1.1',
    'license': 'LGPL-3',
    'depends': ['base', 'dhaif_insurance_service_ext', 'invoice_report_modify_ext'],

    'data': [
        'views/ks_policy_order.xml',
        'views/ks_account_invoice.xml',
        #'views/ks_purchase_order.xml',
        #'views/ks_account_invoice_supplier_form.xml',
        'views/ks_account_account.xml',
        'views/ks_report.xml',
        'views/assets.xml',

    ],
    'application': True
}
