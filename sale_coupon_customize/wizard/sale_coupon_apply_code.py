# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleCouponApplyCode(models.TransientModel):
    _name = 'sale.coupon.apply.code.wizard'
    _description = 'Sales Coupon Apply Code Wizard'

    coupon_code = fields.Char(string="Coupon", required=True)

    @api.multi
    def process_coupon(self):
        """
        Apply the entered coupon code if valid, raise an UserError otherwise.
        """
        sales_order = self.env['sale.order'].browse(self.env.context.get('active_id'))
        error_status = self.apply_coupon(sales_order, self.coupon_code)
        if error_status.get('error', False):
            raise UserError(error_status.get('error', False))
        if error_status.get('not_found', False):
            raise UserError(error_status.get('not_found', False))

    def apply_coupon(self, order, coupon_code):
        error_status = {}
        program = self.env['gift.coupon.pos'].search([('code', '=', coupon_code)])
        if program:
            error_status = order._check_voucher_code(program)
            if not error_status:
                order._create_reward_so_line(program)
        else:
            error_status = {'not_found': _('The code %s is invalid') % (coupon_code)}
        return error_status
