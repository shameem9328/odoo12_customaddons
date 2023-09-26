from odoo import models,fields,api 
from odoo.tools.misc import formatLang
from functools import partial


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def amount_disc_calculation(self):
        discount = 0
        for line in self.order_line:
            if line.product_id == self.env.ref('sale_discount_ext.discount_pdt'):
                discount += abs(line.price_unit)
        return discount

    def discount_pdt_id(self):
        return self.env.ref('sale_discount_ext.discount_pdt') or False
    