# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_sale_coupon_from_pos = fields.Boolean("Sale Coupon from POS", implied_group='sale_coupon_customize.group_sale_coupon_from_pos')




