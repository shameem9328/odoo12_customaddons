# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
    
{
    'name': 'MAST Odoo-WhatsApp Integration',
    'version': '12.1',
    'category': 'Sales',
    'summary': 'WhatsApp Integration with Odoo',
    'description': """
This module for Integrate whatsapp directly with odoo.
    """,
    'depends': ['sale_management','account','base','account_reports','appointment_custom','stock','calendar','helpdesk'],
    'data': [
        'data/whatsapp_sheduler.xml',
        'data/calendar_data.xml',
        'data/calendar_cron.xml',
        'data/helpdesk_mail_data.xml',
        'views/assets.xml',
        'views/sale_order_views.xml',
        'views/message_template.xml',
        'views/res_config_settings_views.xml',
        'views/account_invoice_views.xml',
        'views/account_payment_views.xml',
        'views/followup_view.xml',
        'views/stock_picking_views.xml',
        'views/calendar_views.xml',
        'views/res_company_views.xml',
        'views/helpdesk_views.xml',
        'wizard/wizard_multiple_contact.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True
}

