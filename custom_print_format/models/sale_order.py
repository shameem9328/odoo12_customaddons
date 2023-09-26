from odoo import models,api
from . import user_tz_dtm
from odoo import api, exceptions, fields, models, _


    
class SaleOrder(models.Model):
    _inherit = 'sale.order'


    lpo_number=fields.Char(string="LPO Number")



    
    def get_amount_discount(self):
        has_disc = any(line.discount for line in self.order_line)
        if not has_disc:
            return 0
        amount_disc = 0
        for line in self.order_line:
            disc = line.price_unit - line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            amount_disc += round(disc * line.product_uom_qty,self.pricelist_id.currency_id.decimal_places)
        return amount_disc








    

    

        

