# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        vals['del_method'] = self.sale_line_id.order_id.del_method
        vals['del_sure'] = self.sale_line_id.order_id.del_sure
        vals['client_order_ref'] = self.sale_line_id.order_id.client_order_ref
        return vals

