from odoo import models, fields, api, _
import html2text
import urllib.parse as parse

class SendMultipleContactQuotationMessage(models.TransientModel):
    _name = 'whatsapp.quotation.multiple.contact'

    customer_id=fields.Many2one('res.partner',string="Customer")
    contact_line_ids=fields.One2many('contact.lines','wizard_id',string="Contact Lines", auto_join=True, copy=False)
    sale_order_id=fields.Many2one('sale.order',string="Sale Order")
    picking_id=fields.Many2one('stock.picking',string="Delivery Note")
    invoice_id=fields.Many2one('account.invoice',string="Invoice")
    payment_id=fields.Many2one('account.payment',string="Payment")
    statement_id=fields.Many2one('res.partner',string="Statement")
    ticket_id=fields.Many2one('helpdesk.ticket',string="Ticket")
    message = fields.Text(string="Message", required=True)

    @api.onchange('customer_id')
    def onchange_customer_id(self):
        if self.customer_id:
            partner_ids = self.env['res.partner'].sudo().search([('parent_id', '=', self.customer_id.id)])
            lines = []
            for line in partner_ids:
                vals = {
                    'partner_id': line.id,
                    'mobile': line.mobile,
                }
                lines.append((0, 0, vals))
            self.contact_line_ids = lines

    def send_multiple_contact_message(self):
        whatsa_auth_token = self.env['ir.config_parameter'].sudo().get_param( 'mast_odoo_whatsapp_integration.whatsa_auth_token')
        instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
        if self.contact_line_ids:
            contacts = self.contact_line_ids.filtered(lambda contact: contact.mobile!=False)
            for cont in contacts:
                mobile_to=cont.partner_id.phone_format(cont.mobile)
                message=self.message
                if self.sale_order_id:
                    self.sale_order_id.whatsapp_send_msg(whatsa_auth_token,instance_id,message,mobile_to,cont.partner_id)
                if self.picking_id:
                    self.picking_id.action_delivery_whatsapp_contactmessage(message,mobile_to,cont.partner_id)
                if self.invoice_id:
                    self.invoice_id.action_invoice_contact_sent(cont.partner_id,message,mobile_to)
                if self.payment_id:
                    self.payment_id.action_payment_contact_sent(cont.partner_id,message,mobile_to)
                if self.statement_id:
                    self.statement_id.action_statement_contact_sent(cont.partner_id,message,mobile_to)
                if self.ticket_id:
                    self.ticket_id.send_helpdesk_whatsapp(message,cont.partner_id,mobile_to)







class ContactLines(models.TransientModel):
    _name = 'contact.lines'

    wizard_id=fields.Many2one('whatsapp.quotation.multiple.contact',sytring="Wizard", ondelete='cascade', index=True, copy=False)
    partner_id = fields.Many2one('res.partner', string="Recipient",required=True)
    mobile = fields.Char(string="Contact Number",)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.mobile=self.partner_id.mobile


