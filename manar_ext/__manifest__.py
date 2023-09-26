{
    'name': 'Almanar Ext',
    'category': 'All',
    'author':'Mast Information Technology - Bahrain',
    'description': "Coming Soon",
    'depends': ['sale','delivery','sale_stock','mrp','point_of_sale','account_cancel'],
    'website': 'http://www.mast-it.com',
    'data': [
            'views/res_partner_views.xml',
            'views/sale_views.xml',
            'views/stock_picking_views.xml',
            'views/account_invoice_views.xml',
            'views/account_payment_views.xml',
            'security/sale_security.xml',
            'views/model_ext_views.xml',
            'views/templates.xml',
            'views/product_views.xml',
            'security/ir.model.access.csv',
             ],
    'installable': True,
    'application': True,
    'qweb': ['static/src/xml/*.xml'],
    
}
