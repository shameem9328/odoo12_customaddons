# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
#from odoo import api, fields, models, _, SUPERUSER_ID

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def _get_del_method(self):
        return [('del','Delivery'),
                ('ta','Take Away')]
    
    def _get_del_sure(self):
        return [('sure','Sure'),
                ('not_sure','Not Sure')]
    
    del_method = fields.Selection(_get_del_method,string="DEL / TA",track_visibility='onchnage')
    del_sure = fields.Selection(_get_del_sure,string="Del. Sure / Not",track_visibility='onchnage')
    client_order_ref = fields.Char(string='Customer Reference', copy=False, track_visibility='onchange')
    #location_id = fields.Many2one('stock.location', "Source Location",default=lambda self: self.env['stock.picking.type'].browse(
    #        self._context.get('default_picking_type_id')).default_location_src_id,readonly=True, required=True,states={'draft': [('readonly', False)], 'waiting': [('readonly', False)], 'confirmed': [('readonly', False)], 'assigned': [('readonly', False)], 'done': [('readonly', False)]}, track_visibility='onchange')
    #picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type',required=True,readonly=True,
    #    states={'draft': [('readonly', False)], 'waiting': [('readonly', False)], 'confirmed': [('readonly', False)], 'assigned': [('readonly', False)], 'done': [('readonly', False)]}, track_visibility='onchange')
    warehouse_id = fields.Many2one('stock.warehouse',compute="_compute_warehouse_id",store=True,readonly=True)
    
    @api.depends('picking_type_id')
    def _compute_warehouse_id(self):
        for rec in self:
            rec.warehouse_id = rec.picking_type_id.warehouse_id.id
    
    @api.onchange('picking_type_id', 'partner_id')
    def onchange_picking_type(self):
        if self.picking_type_id:
            if self.picking_type_id.default_location_src_id:
                location_id = self.picking_type_id.default_location_src_id.id
            elif self.partner_id:
                location_id = self.partner_id.property_stock_supplier.id
            else:
                customerloc, location_id = self.env['stock.warehouse']._get_partner_locations()

            if self.picking_type_id.default_location_dest_id:
                location_dest_id = self.picking_type_id.default_location_dest_id.id
            elif self.partner_id:
                location_dest_id = self.partner_id.property_stock_customer.id
            else:
                location_dest_id, supplierloc = self.env['stock.warehouse']._get_partner_locations()
            #if self.state == 'draft':
            if self.state not in ['cancel','done']:
                self.location_id = location_id
                self.location_dest_id = location_dest_id
        # TDE CLEANME move into onchange_partner_id
        if self.partner_id and self.partner_id.picking_warn:
            if self.partner_id.picking_warn == 'no-message' and self.partner_id.parent_id:
                partner = self.partner_id.parent_id
            elif self.partner_id.picking_warn not in (
            'no-message', 'block') and self.partner_id.parent_id.picking_warn == 'block':
                partner = self.partner_id.parent_id
            else:
                partner = self.partner_id
            if partner.picking_warn != 'no-message':
                if partner.picking_warn == 'block':
                    self.partner_id = False
                return {'warning': {
                    'title': ("Warning for %s") % partner.name,
                    'message': partner.picking_warn_msg
                }}



