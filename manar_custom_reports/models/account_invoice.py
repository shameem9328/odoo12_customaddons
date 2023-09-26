from odoo import models,api
from . import user_tz_dtm

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    def get_description(self):
        line = self
        if line.product_id and \
        line.product_id.default_code and \
        line.product_id.default_code in line.name:
            description = line.name
            return description.replace(f"[{line.product_id.default_code}]",'')
        else:
            return line.name
        
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
    
    def get_extra_values(self,which):
        vals = {}
        so_ids = list(set(self.invoice_line_ids.mapped('sale_line_ids').mapped('order_id').mapped('id')))
        sales_orders = self.env['sale.order'].browse(so_ids)
        if which == "del_date":
            rec_dates = [] 
            rec_days = []
            rec_times = []
            if not self.del_date:
                for so in sales_orders:
                    for picking in so.picking_ids.filtered(lambda p:p.state not in ['cancel'] and p.scheduled_date):
                        rec_dates.append(user_tz_dtm.get_date_str(self,picking.scheduled_date))
                        rec_days.append(user_tz_dtm.get_tz_date_time(self,picking.scheduled_date).strftime("%A"))
                        rec_times.append(user_tz_dtm.get_tz_date_time(self,picking.scheduled_date).strftime("%I:%M %p"))
            else:
                rec_dates.append(user_tz_dtm.get_date_str(self,self.del_date))
                rec_days.append(user_tz_dtm.get_tz_date_time(self,self.del_date).strftime("%A"))
                rec_times.append(user_tz_dtm.get_tz_date_time(self,self.del_date).strftime("%I:%M %p"))
            vals.update({'dates':",".join(rec_dates),
                         'days':",".join(rec_days),
                         'times':",".join(rec_times)
                         })
        elif which == "warehouse":
            vals['name'] = ",".join(sales_orders.mapped('warehouse_id').mapped('name'))
        elif which == 'amount_reward':
            amount_reward = 0
            for line in self.invoice_line_ids:
                if line.is_reward_ai_line or \
                len(line.sale_line_ids.ids) == 1 and \
                line.sale_line_ids.is_reward_so_line:
                    amount_reward += abs(line.price_subtotal)
                vals['name'] = amount_reward and abs(amount_reward) or 0
        return vals
    
    @api.multi
    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        template = self.env.ref('account.email_template_edi_invoice', False)
        if template:
            report_with_letter_head = self.env.ref('account.account_invoices')
            if template.report_template.id != report_with_letter_head.id:
                template.report_template = report_with_letter_head.id
        return super(AccountInvoice,self).action_invoice_sent()
    
    
    