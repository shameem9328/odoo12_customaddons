from odoo import models,api
from . import user_tz_dtm
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


    
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    custom_journal_id = fields.Many2one('account.journal', string='Journal', readonly=True, states={'draft': [('readonly', False)]},domain="[('type', 'in', {'out_invoice': ['sale'], 'out_refund': ['sale'], 'in_refund': ['purchase'], 'in_invoice': ['purchase']}.get(type, [])), ('company_id', '=', company_id)]")
    
    def action_invoice_open(self):
        res=super().action_invoice_open()
        for rec in self:
            if not rec.custom_journal_id:
                raise UserError(_('Please set journal  to this invoice.'))
        return res

    @api.onchange('custom_journal_id')
    def onchange_custom_journal(self):
        if self.custom_journal_id:
            self.journal_id=self.custom_journal_id


    

    
    def get_amount_discount(self):
        has_disc = any(line.discount for line in self.invoice_line_ids)
        if not has_disc:
            return 0
        amount_disc = 0
        for line in self.invoice_line_ids:
            disc = line.price_unit - line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            amount_disc += round(disc * line.quantity,self.currency_id.decimal_places)
        return amount_disc

    def amount_disc_calculation(self):
        discount = 0
        if self.discount_pdt_id():
            for line in self.invoice_line_ids:
                if line.product_id.id == self.discount_pdt_id().id:
                    discount += abs(line.price_unit)
        return discount


    def discount_pdt_id(self):
        obj_pos = self.env['pos.order'].sudo()
        disc_pdt=None
        if obj_pos.search([('invoice_id', 'in', self.ids)]):
            disc_pdt = obj_pos.search([('invoice_id', 'in', self.ids)])[0].config_id.discount_product_id
        return disc_pdt or False



    def invoice_datetime(self):
        date_day = self.date_invoice
        if date_day:
            obj_pos = self.env['pos.order'].sudo()
            if obj_pos.search([('invoice_id', 'in', self.ids)]):
                inv_datetime = self.create_date
                # date_day = inv_datetime.astimezone(local).strftime(dt_tm_format)
                date_day = user_tz_dtm.get_tz_date_time_str(self, inv_datetime, self.env.user)
            else:
                # date_day = date_day.strftime(dt_format)
                date_day = user_tz_dtm.get_date_str(self, date_day, self.env.user)
            return date_day
        else:
            return ""


    def get_doc_ref_number(self):
        obj_pos = self.env['pos.order'].sudo()
        doc_ref = self.number
        if obj_pos.search([('invoice_id', 'in', self.ids)]):
            ref = obj_pos.search([('invoice_id', 'in', self.ids)])[0].config_id.name
            doc_ref = ref + ' - ' + doc_ref
        return doc_ref
    

    

        

