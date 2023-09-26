# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Sale Coupon Customize",
    'summary': """Allows to use POS discount coupons in sales orders""",
    'description': """Integrate coupon mechanism in sales orders.""",
    'category': 'Sales',
    'version': '1.0',
    'author': 'Mast-IT Bahrain',
    'depends': ['sale_management','vouchers_pos'],
    'data': [
        'security/sale_coupon_security.xml',
        'wizard/sale_coupon_apply_code_views.xml',
        'views/sale_order_views.xml',
        'views/res_config_settings_views.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
