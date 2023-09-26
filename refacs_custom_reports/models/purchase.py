from odoo import models,api
from functools import partial
from odoo.tools.misc import formatLang

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    def _amount_by_group(self):
        for order in self:
            currency = order.currency_id or order.company_id.currency_id
            fmt = partial(formatLang, self.with_context(lang=order.partner_id.lang).env, currency_obj=currency)
            res = {}
            for line in order.order_line:
                price_reduce = line.price_unit * (1.0 - 0 / 100.0)
                taxes = line.taxes_id.compute_all(price_reduce, quantity=line.product_uom_qty, product=line.product_id, partner=order.partner_id)['taxes']
                for tax in line.taxes_id:
                    group = tax.tax_group_id
                    res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                    for t in taxes:
                        if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                            res[group]['amount'] += t['amount']
                            res[group]['base'] += t['base']
            res = sorted(res.items(), key=lambda l: l[0].sequence)
            res = [(
                l[0].name, l[1]['amount'], l[1]['base'],
                fmt(l[1]['amount']), fmt(l[1]['base']),
                len(res),
            ) for l in res]
            return res

    @api.multi
    def action_rfq_send(self):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        if self.env.context.get('send_rfq', False):
            template_id = ir_model_data.get_object_reference('purchase', 'email_template_edi_purchase')[1]
        else:
            template_id = ir_model_data.get_object_reference('purchase', 'email_template_edi_purchase_done')[1]
        report_with_letter_head = self.env.ref('refacs_custom_reports.action_report_purchase_order_with_logo')
        if template_id:
            template_id = self.env['mail.template'].sudo().browse(template_id)
            if template_id.report_template.id != report_with_letter_head.id:
                template_id.report_template = report_with_letter_head.id
        return super(PurchaseOrder, self).action_rfq_send()

    @api.multi
    def print_quotation(self):
        self.write({'state': "sent"})
        return self.env.ref('purchase.report_purchase_quotation').report_action(self)