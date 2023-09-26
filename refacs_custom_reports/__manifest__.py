# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Refacs Custom Reports',
    'version': '1.0',
    'category': 'Sale,Stock,Account,Purchase',
    'author':'Mast Information Technology - Bahrain',
    'description': "Coming Soon",
    'depends': ['sale_stock',
                'account',
                'purchase',
                'repair','partner_fax','point_of_sale'
                ],
    'website': 'http://www.mast-it.com',
    'data': [
            'data/res_lang.xml',
            'reports/report_templates.xml',
            'reports/report_paperformat.xml',
            'reports/sale_report_templates.xml',
            'reports/purchase_order_templates.xml',
            'reports/report_invoice.xml',
            'reports/report_deliveryslip.xml',
            'reports/report_receivednote.xml',
            'reports/report_movementnote.xml',
            'reports/report_payment_receipt_templates.xml',
            'reports/repair_templates_repair_order.xml',
            'reports/reports.xml',
            'reports/point_of_sale_report.xml',
            'views/repair_views.xml',
            'views/res_company_view.xml',
            
             ],
    'installable': True,
    'application': True,
    'qweb': ['static/src/xml/*.xml'],
    
}
