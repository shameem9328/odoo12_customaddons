# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class DiscountSales(models.Model):
    _inherit = "sale.order"

    discount_rate = fields.Float('Discount',
       readonly=True,
       states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    
    
    @api.multi
    def add_discount_pdt(self):
        for line in self.order_line:
            if line.product_id.id == self.env.ref('sale_discount_ext.discount_pdt').id:
                line.unlink()
        obj_order_line = self.env['sale.order.line']
        order_line_val = {}
        
        amount_discount = 0.0
        #if self.discount_type == 'percent':
        #    discount_total = self.discount_rate
        #lse:
        if self.discount_rate != 0:
            amount_discount = self.discount_rate
        
        last_so_line = self.env['sale.order.line'].search([('order_id', '=', self.id)], order='sequence desc', limit=1)
        last_sequence = last_so_line.sequence + 1 if last_so_line else 100
        order_line_val['product_id'] = self.env.ref('sale_discount_ext.discount_pdt').id
        order_line_val['price_unit'] = -1*amount_discount
        order_line_val['name'] = 'Discount'
        order_line_val['product_uom_qty'] = 1
        order_line_val['order_id'] = self.id
        order_line_val['sequence'] = last_sequence
        obj_order_line.create(order_line_val)
    
    
    """@api.multi
    def _prepare_invoice(self):
        for rec in self:
            res = super(DiscountSales, rec)._prepare_invoice()
            res['discount_rate'] = rec.discount_rate
            
        return res"""

    