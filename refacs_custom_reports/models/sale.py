from odoo import models,api 

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    def get_price_subtotal(self):
        line = self
        price = line.price_unit * (1 - (0 or 0.0) / 100.0)
        taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
        return taxes['total_excluded']
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def get_amount_discount(self):
        has_disc = any(line.discount for line in self.order_line)
        if not has_disc:
            return 0
        amount_disc = 0
        for line in self.order_line:
            price_disc = line.price_unit - line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            amount_disc += price_disc * line.product_uom_qty
        return amount_disc
    
    def get_amount_untaxed(self):
        has_disc = any(line.discount for line in self.order_line)
        if not has_disc:
            return self.amount_untaxed
        amount_untaxed = 0
        for line in self.order_line:
            price = line.price_unit * (1 - (0 or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            amount_untaxed += taxes['total_excluded']
        return amount_untaxed
    
    @api.multi
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('sale', 'email_template_edi_sale')[1]
        template_id = self.env['mail.template'].browse(template_id)
        print("template_id11",template_id)
        report_with_letter_head = self.env.ref('refacs_custom_reports.action_report_saleorder')
        if template_id.report_template.id != report_with_letter_head.id:
            template_id.report_template = report_with_letter_head.id
        return super(SaleOrder,self).action_quotation_send()

    @api.multi
    def print_quotation(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})

        return self.env.ref('refacs_custom_reports.action_report_saleorder') \
            .with_context(discard_logo_check=True).report_action(self)