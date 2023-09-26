# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
#from odoo.tools.misc import formatLang
from datetime import timedelta, datetime
#from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        obj_partner_coupon = self.env['partner.coupon.pos']
        for line in self.order_line:
            if line.is_reward_so_line:
                value = {
                         'partner_id': self.partner_id.id,
                         'coupon_pos': line.pos_coupon_code,
                      }
                obj_partner_coupon.update_history(value)
        return res
    @api.multi
    def coupon_apply_code_from_pos(self):
        action = self.env.ref('sale_coupon_customize.sale_coupon_apply_code_wizard_action').read()[0]

        action.update({
            'views': [[False, 'form']],
            'context': "{'default_sale_id': " + str(self.id) + "}",
        })
        return action

    def _create_reward_so_line(self, program):
        self.write({'order_line': [(0, False, value) for value in self._get_reward_so_line_values(program)]})

    def _get_reward_values_so_product(self, program):
        if program.type == 'percentage':
            price_unit = self.amount_total * program.voucher_val / 100
        else:
            price_unit = program.voucher_val

        gift_product = self.env.ref('vouchers_pos.gift_product_pos')
        taxes = gift_product.taxes_id
        if self.fiscal_position_id:
            taxes = self.fiscal_position_id.map_tax(taxes)
        return {
            'product_id': gift_product.id,
            'price_unit': - price_unit,
            'product_uom_qty': 1,
            'is_reward_so_line': True,
            'name': gift_product.name,
            'product_uom': gift_product.uom_id.id,
            'tax_id': [(4, tax.id, False) for tax in taxes],
            'pos_coupon_code': program.code,
            'sequence': 100
        }

    def _get_reward_so_line_values(self, program):
        self.ensure_one()
        self = self.with_context(lang=self.partner_id.lang)
        program = program.with_context(lang=self.partner_id.lang)
        if self.env.ref('vouchers_pos.gift_product_pos'):
            return [self._get_reward_values_so_product(program)]

    def check_voucher_products(self, program):
        vouchers = program.voucher
        if vouchers and vouchers.voucher_type == 'product':
            voucher_pdt = vouchers.product_id.id
            if voucher_pdt in self.order_line.mapped('product_id').mapped('id'):
                flag = True
            else:
                flag = False
        elif vouchers and vouchers.voucher_type == 'category':
            voucher_pos_categ = vouchers.product_categ.id
            if voucher_pos_categ in self.order_line.mapped('product_id').mapped('pos_categ_id').mapped('id'):
                flag = True
            else:
                flag = False
        else:
            flag = True
        return  flag

    def _check_voucher_code(self, program):
        message = {}
        obj_partner_limit = self.env['partner.coupon.pos']
        code = program.code
        start_date = program.start_date
        end_date = program.end_date
        total_avail = program.total_avail
        limit = program.limit
        sigle_partner_id = program.partner_id
        today = datetime.today().date()
        if program.type == 'percentage':
            price_unit = self.amount_total * program.voucher_val / 100
        else:
            price_unit = program.voucher_val
        for line in self.order_line:
            if code in line.mapped('pos_coupon_code'):
                message = {'error': _('The coupon code is already applied on this order')}
        pdt_flag = self.check_voucher_products(program)
        if not message:
            if not self.order_line:
                message = {'error': _('You cannot apply coupon without products.')}
            elif not pdt_flag:
                message = {'error': _('This coupon is not applicable on the products or category you have selected !')}
            elif sigle_partner_id and sigle_partner_id.id != self.partner_id.id:
                message = {'error': _('Coupon usage is limited to a particular customer.')}
            elif end_date and end_date < today:
                message = {'error': _('Coupon code is expired')}
            elif start_date and start_date > today:
                message = {'error': _('This coupon code is not acceptable now')}
            elif total_avail and total_avail <= 0:
                message = {'error': _('Invalid code or no coupons left')}
            elif (self.amount_total - price_unit) <= 0:
                message = {'error': _('Coupon amount is too large to apply. The total amount cannot be negative')}
            elif limit:
                total_limit = 0
                pos_limit = obj_partner_limit.search([('partner_id', '=', self.partner_id.id),('coupon_pos', '=', code)])
                for lt in pos_limit:
                    total_limit += lt.number_pos
                if limit <= total_limit:
                    message = {'error': _('Coupon usage is limited to a perticular customer')}
        return message


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_reward_so_line = fields.Boolean('Is a program reward line')
    pos_coupon_code = fields.Char(string="Coupon Applied")
    
    #fkp-25/07/2020
    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine,self)._prepare_invoice_line(qty)
        res.update({'is_reward_ai_line':self.is_reward_so_line,
                    'pos_coupon_code':self.pos_coupon_code
                    })
        return res


