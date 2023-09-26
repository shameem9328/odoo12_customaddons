# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Almanar Custom Reports',
    'version': '1.0',
    'category': 'All',
    'author':'Mast Information Technology - Bahrain',
    'description': "Coming Soon",
    'depends': [
                'manar_ext','sale_coupon_customize','purchase'
                ],
    #'website': 'http://www.mast-it.com',
    'data': [
            'reports/report_paperformat.xml',
            'reports/report_invoice.xml',
            'reports/sale_report_templates.xml',
            'reports/purchase_order_templates.xml',
            'reports/report_deliveryslip.xml',
            'reports/report_payment_receipt_templates.xml',
            'reports/report_invoice_without_letterhead.xml',
            'reports/reports.xml',
            'views/report_templates.xml',
            'views/report_templates_new.xml',
            'views/res_partner.xml',
             ],
    'installable': True,
    'application': True,
    'qweb': ['static/src/xml/*.xml'],
    
}
