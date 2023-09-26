from odoo import api, fields, models
from datetime import datetime, date, time

from odoo.exceptions import UserError
import json

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    #to remove - query ypdate
    inv_updated = fields.Boolean(default=True)
        
    @api.multi
    def action_view_invoice(self):
        action = super(SaleOrder,self).action_view_invoice()
        if action.get('context',False):
            action['context'] = "{'type':'out_invoice', 'journal_type': 'sale','create':False}"
        #print('action=',action['context'])
        return action

    @api.model
    def _default_warehouse_id(self):
        company = self.env.user.company_id.id
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        return warehouse_ids
    client_order_ref = fields.Char(string='Customer Reference', copy=False, track_visibility='onchange')
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},
        default=_default_warehouse_id, track_visibility='onchange')



    @api.multi
    def action_cancel(self):
        result = super(SaleOrder, self).action_cancel()
        self.mapped('invoice_ids').action_cancel()
        self.cancel_production()
        return result
    
    @api.multi
    def cancel_production(self):
        obj_production = self.env['mrp.production']
        production_states = {
                            'confirmed':'Confirmed',
                            'planned':'Planned',
                            'progress':'In Progress',
                            'done':'Done',
                            'cancel':'Cancelled'
                            }
        for rec in self:
            productions = obj_production.search([('origin','=',rec.name)])
            for production in productions:
                if production.state in ['confirmed','planned']:
                    production.action_cancel()
                if production.state in ['progress','done']:
                    raise UserError(f"A production order already exist for this order. \n"\
                                    f"Please check with production team.\n" \
                                    f"Cancel the related production first.\n\n"
                                    f"Production Order Ref: {production.name}\n" \
                                    f"Production Order Status: {production_states[production.state]}")
                
    
    @api.multi
    def write(self, values):
        res = super(SaleOrder, self).write(values)
        vals_update = {}
        if 'del_method' in values:
            vals_update['del_method'] = values['del_method']
        if 'del_sure' in values:
            vals_update['del_sure'] = values['del_sure']

        if vals_update or \
        "commitment_date" in values or \
        "client_order_ref" in values:
            invoice_to_update = self.mapped('invoice_ids').filtered(lambda i: i.state not in ['paid','cancel'] and not \
                                                                    i.refund_invoice_id)
            picking_to_update  = self.mapped('picking_ids').filtered(lambda p: p.state not in ['done','cancel'] and not \
                                                                     p.backorder_id)
            invoice_to_update.write(vals_update)
            if "commitment_date" in values:
                invoice_to_update.write({'del_date':values['commitment_date']})
                vals_update['scheduled_date'] = values['commitment_date']
            picking_to_update.write(vals_update)
            if "client_order_ref" in values:
                vals_update_delivery = {}
                vals_update_invoice = {}
                vals_update_delivery['client_order_ref'] = values['client_order_ref']
                vals_update_invoice['name'] = values['client_order_ref']
                invoice_to_update.write(vals_update_invoice)
                picking_to_update.write(vals_update_delivery)
        ##Change picking_type_id and location_id according to warehouse_id
        for do_pick in self.picking_ids:
            if do_pick.state in ['draft','waiting', 'assigned','confirmed']:
                picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing'),('warehouse_id', '=', self.warehouse_id.id),('active', '=', True)])[0]
                val_picking_type_id = picking_type.id or False
                val_location_id = picking_type.default_location_src_id.id if picking_type.default_location_src_id else False
                if val_picking_type_id and val_location_id:
                    if do_pick.state in ['assigned']:
                        do_pick.do_unreserve()
                    #do_pick.write({'picking_type_id': val_picking_type_id,'location_id': val_location_id})
                    do_pick.write({'picking_type_id': val_picking_type_id})
                do_pick.onchange_picking_type()
        ##KPL##
        today_begining = datetime.combine(date.today(), time())
        if 'commitment_date' in values and \
        self.commitment_date and \
        self.commitment_date < today_begining:
            raise UserError(f"Delivery date must be today or greater !")
        #######
        return res

    ##KPL##
    @api.model
    def create(self, vals):
        result = super(SaleOrder, self).create(vals)
        today_begining = datetime.combine(date.today(), time())
        if vals.get('commitment_date',False):
            commitment_date = datetime.strptime(vals['commitment_date'], '%Y-%m-%d %H:%M:%S')
            if commitment_date < today_begining:
                raise UserError(f"Delivery date must be today or greater !")
        return result

    #######
    def _get_del_method(self):
        return [('del','Delivery'),
                ('ta','Take Away')]
        
    def _get_del_sure(self):
        return [('sure','Sure'),
                ('not_sure','Not Sure')]
    
    del_method = fields.Selection(_get_del_method,string="DEL / TA",track_visibility='onchnage')
    del_sure = fields.Selection(_get_del_sure,string="Del. Sure / Not",track_visibility='onchnage')
    commitment_date = fields.Datetime('Delivery Date',
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)],'waiting': [('readonly', False)],'sale': [('readonly', False)]},
        copy=False, oldname='requested_date', readonly=True,
        help="This is the delivery date promised to the customer. If set, the delivery order "
             "will be scheduled based on this date rather than product lead times.",track_visibility='onchnage')
    
    #@api.onchange('commitment_date')
    #def onchange_commitment_date(self):
    #    today_begining = datetime.combine(date.today(), time())
    #    #self.commitment_date = False
    #    if self.commitment_date and \
    #    self.commitment_date < today_begining:
    #        raise UserError(f"Delivery date must be today or greater !")
        
                            
    @api.multi
    def action_confirm(self):
        for rec in self:
            msgs = []
            rec.partner_id.check_mandatory()
            if not rec.del_method:
                msgs.append(f"DEl / TA must be required")   
            if not rec.del_sure:
                msgs.append(f"Delivery Sure / Not Sure must be required")
            if not rec.commitment_date:
                msgs.append(f"Delivery date must be required")   
            today_begining = datetime.combine(date.today(), time())
            if self.commitment_date and \
            self.commitment_date < today_begining:
                msgs.append(f"Delivery date must be today or greater !") 
            if msgs:
                raise UserError("\n".join(msgs))
        return super(SaleOrder,self).action_confirm()
    
    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({'del_method' :  self.del_method,
                             'del_sure' : self.del_sure,
                             'del_date' : self.commitment_date
                             })
        return invoice_vals
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    can_edit_unit_price = fields.Boolean(compute='_get_user_group')
    can_edit_tax = fields.Boolean(compute='_get_user_group')
    
    @api.onchange('name')
    def check_description(self):
        if self.product_id and \
        self.name:
            vals = {}
            #domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
            if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
                #vals['product_uom'] = self.product_id.uom_id
                vals['product_uom_qty'] = self.product_uom_qty or 1.0
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=vals.get('product_uom_qty') or self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id
            )
            #print("Context=",self._context)
            #print('self.name=',self.name)
            name = self.get_sale_order_line_multiline_description_sale(product)
            if name not in self.name and self.name and not self.name.isspace():
                raise UserError(f"Product description: {name} must be in description")
    
    """
    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        return super(SaleOrderLine,self.with_context({'product_id_change':True})).product_id_change()
    """
         
    @api.depends('product_id')
    def _get_user_group(self):
        for rec in self:
            if rec.env.user.has_group(f'manar_ext.group_edit_sale_price_unit'):
                rec.can_edit_unit_price = True
            else:
                rec.can_edit_unit_price = False
            
            if rec.env.user.has_group(f'manar_ext.group_edit_sale_tax'):
                rec.can_edit_tax = True
            else:
                rec.can_edit_tax = False
    
    @api.multi
    def write(self, values):
        res = super(SaleOrderLine, self).write(values)
        if values.get('name',False):
            inv_lines = self.env['account.invoice.line'].search([('sale_line_ids','in',[self.id]),
                                                                 ('invoice_id.refund_invoice_id','=',False),
                                                                 ])
            for inv_line in inv_lines:
                inv_line.name = "\n".join(list(set(inv_line.sale_line_ids.mapped('name'))))
            stock_moves = self.env['stock.move'].search([('sale_line_id','=',self.id),
                                                         ('picking_id','!=',False),
                                                         ('picking_id.backorder_id','=',False)])
            stock_moves.write({'name':values['name']})
            
        return res
    
    
    
    