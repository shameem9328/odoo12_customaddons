from odoo import models,api
from . import user_tz_dtm

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    def get_price_subtotal(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (0 or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        return taxes['total_excluded'] if taxes else self.quantity * price
    
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.model
    def _get_payments_vals(self):
        res = super(AccountInvoice,self)._get_payments_vals()
        for payment_vals in res:
            payment_vals.update({'account_payment':self.env['account.payment'].browse(payment_vals['account_payment_id']),
                                 'date':user_tz_dtm.get_date_str(self,payment_vals['date'])
                                 })
        return res
    
    def get_amount_discount(self):
        has_disc = any(line.discount for line in self.invoice_line_ids)
        if not has_disc:
            return 0
        amount_disc = 0
        for line in self.invoice_line_ids:
            disc = line.price_unit - line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            amount_disc += disc * line.quantity
        return amount_disc
    
    def get_amount_untaxed(self):
        currency = self.currency_id or None
        has_disc = any(line.discount for line in self.invoice_line_ids)
        if not has_disc:
            return self.amount_untaxed
        amount_untaxed = 0
        for line in self.invoice_line_ids:
            price = line.price_unit * (1 - (0 or 0.0) / 100.0)
            taxes = False
            if line.invoice_line_tax_ids:
                taxes = line.invoice_line_tax_ids.compute_all(price, currency, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
                amount_untaxed += taxes['total_excluded'] if taxes else line.quantity * price
        return amount_untaxed
        
    def get_amount_in_currency(self,amount=0):
        return f'%.{self.currency_id.decimal_places}f' % amount
    
    @api.multi
    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        template = self.env.ref('account.email_template_edi_invoice', False)
        if template:
            report_with_letter_head = self.env.ref('refacs_custom_reports.account_invoices_with_logo')
            if template.report_template.id != report_with_letter_head.id:
                template.report_template = report_with_letter_head.id
        return super(AccountInvoice,self).action_invoice_sent()
    
    def get_extra_values(self,which):
        so_ids = list(set(self.invoice_line_ids.mapped('sale_line_ids').mapped('order_id').mapped('id')))
        sales_orders = self.env['sale.order'].browse(so_ids)
        pickings = sales_orders.mapped('picking_ids').filtered(lambda p:p.state in ['done'] and not \
                                           p.backorder_id)
        
        rec_names = []
        if which == 'delivery':
            rec_names = pickings.mapped('name')
        ################################    
        return ",".join(list(set(rec_names)))
        
    
    