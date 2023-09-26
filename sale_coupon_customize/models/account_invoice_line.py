# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
#fkp - 25/07/2020
class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    is_reward_ai_line = fields.Boolean('Is a program reward line')
    pos_coupon_code = fields.Char(string="Coupon Applied")
    
    

