from odoo import models,api
from . import user_tz_dtm

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    def get_description(self):
        line = self
        if line.product_id and \
        line.product_id.default_code and \
        line.product_id.default_code in line.move_id.name:
            description = line.move_id.name
            return description.replace(f"[{line.product_id.default_code}]",'')
        else:
            return line.move_id.name
        
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def get_extra_values(self,which):
        sales_orders = self.group_id and self.group_id.sale_id
        if not sales_orders:
            return
        rec_names = []
        inv_status = ['draft','cancel']
        if which == 'invoice':
            invoices = sales_orders.mapped('invoice_ids').filtered(lambda i:i.state not in inv_status)
            rec_names = invoices.mapped('number')
        ################################    
        return ",".join(list(set(rec_names)))

