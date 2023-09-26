import base64
import time

from odoo import models, fields, api, _,tools
import urllib.parse as parse
from odoo.exceptions import UserError
from itertools import groupby
import json
import http.client
import http.client
import base64
import urllib.parse
import requests
import ssl
from datetime import datetime
import html2text
import urllib.parse
from odoo.addons.phone_validation.tools import phone_validation


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_visible_whatsapp = fields.Boolean(string="Is Visible Whastapp", compute="_compute_whatsapp_payment_visibility")

    #@api.depends('name')
    def _compute_whatsapp_payment_visibility(self):
        for rec in self:
            rec.is_visible_whatsapp = rec.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.payments_whts_available')


    def _phone_get_always_international(self):
        if self.partner_id.company_id:
            return self.partner_id.company_id.phone_international_format == 'prefix'
        return self.company_id.phone_international_format == 'prefix'

    def _phone_get_country(self):
        if self.partner_id.country_id:
            return self.partner_id.country_id
        return self.company_id.country_id

    def phone_format(self, number, country=None, company=None):
        country = country or self._phone_get_country()
        if not country:
            return number
        # always_international = company.phone_international_format == 'prefix' if company else self._phone_get_always_international()
        return phone_validation.phone_format(
            number,
            country.code if country else None,
            country.phone_code if country else None,
            raise_exception=False
        )

    def action_payment_whatsapp_sent(self):
        for rec in self:
            payment_message_template = (rec.company_id.payment_message_template_message)
            custom_msg = str(self.env['mail.template']._render_template((payment_message_template), 'account.payment', rec.id) or '')
            payment_whts_msg = str(self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.payment_whts_msg') or '')
            custom_msg += "\n" + payment_whts_msg
            record_phone = rec.partner_id.mobile
            if record_phone:
                record_phone = rec.phone_format(rec.partner_id.mobile)
            rec.action_payment_contact_sent(rec.partner_id, custom_msg, record_phone)
        return

    def post(self):
        res = super(AccountPayment, self).post()
        for rec in self:
            payments_whts_available = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.payments_whts_available')
            payments_whts_send_type = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.payments_whts_send_type')
            #payment_whts_msg = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.payment_whts_msg')
            #custommesage = "Thank you for your payment. Here is your payment receipt *{}*amounting to {} {} from {}.\n \nDo not hesitate to contact us if you have any question.\n".format( str(self.name), str(self.currency_id.symbol), str(self.amount),str(self.company_id.name))
            if payments_whts_available and payments_whts_send_type == 'auto':
                rec.action_payment_whatsapp_sent()
        return res


    def action_payment_whatsapp_contact_sent(self):
        for rec in self:
            payment_message_template = (rec.company_id.payment_message_template_message)
            custom_msg = str(self.env['mail.template']._render_template((payment_message_template), 'account.payment', rec.id) or '')
            payment_whts_msg = str(self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.payment_whts_msg') or '')
            custom_msg += "\n" + payment_whts_msg
            return {'type': 'ir.actions.act_window',
                    'name': _('Whatsapp to contacts'),
                    'res_model': 'whatsapp.quotation.multiple.contact',
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {
                        'default_customer_id': rec.partner_id.id,
                        'default_message':tools.html2plaintext(custom_msg),
                        'default_payment_id': rec.id,
                        },
                    }

    def action_payment_contact_sent(self, partner_id, message, to):
        token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
        instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
        conn = http.client.HTTPSConnection("api.ultramsg.com")
        headers = {'content-type': "application/x-www-form-urlencoded"}
        for rec in self:
            if self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.payment_template_id'):
                print_template = self.env['ir.actions.report'].sudo().browse(int(self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.payment_template_id')))
                pdf = print_template.render_qweb_pdf(rec.id)[0] if print_template else None
            else:
                pdf = rec.env.ref('account.action_report_payment_receipt').render_qweb_pdf(rec.id)[0]
            record_phone = to
            if record_phone:
                if rec.id:
                    if pdf:
                        pdf_attachment_id = base64.b64encode(pdf)
                        if pdf_attachment_id:
                            document = pdf_attachment_id
                            doc = urllib.parse.quote_plus(document)
                            bdy_msg = message
                            bdy_msg = str(tools.html2plaintext(bdy_msg))
                            filename = str("Payment Receipt\n"+str(rec.name or''))
                            referenceId = None
                            nocache = None
                            payload_doc = f"token={token}&to={record_phone}&filename={filename}&caption={str(urllib.parse.quote(bdy_msg))}&document={doc}&referenceId={referenceId}&nocache{nocache}".format(token=token, number=record_phone, filename=filename, doc=doc,referenceId=referenceId, nocache=nocache)
                            payload_doc = payload_doc.encode('utf8').decode('iso-8859-1')
                            doc_pst_url = "/{instance_id}/messages/document".format(instance_id=instance_id)
                            conn.request("POST", doc_pst_url, payload_doc, headers)
                            res = conn.getresponse()
                            data_doc = res.read()
                            msg_sent_status = data_doc.decode("utf-8")
                            final_dictionary = eval(msg_sent_status)
                            if final_dictionary.get('sent') == 'true':
                                time.sleep(2)
                                msg_id = int(final_dictionary.get('id'))
                                msg_status_url = "https://api.ultramsg.com/{instance_id}/messages".format(instance_id=instance_id)
                                querystring = {
                                    "token": token,
                                    "page": 1,
                                    "limit": 1,
                                    "status": "",
                                    "sort": "",
                                    "id": int(msg_id),
                                    "referenceId": "",
                                    "from": "",
                                    "to": "",
                                    "ack": "",
                                    "msgId": "",
                                    "start_date": "",
                                    "end_date": ""
                                }
                                headers = {'content-type': 'application/x-www-form-urlencoded'}
                                response = requests.request("GET", msg_status_url, headers=headers, params=querystring)
                                result = json.loads(response.text)
                                if result.get('messages')[0].get('status') == 'invalid':
                                    msg = (_('Failure reason:The number does not have WhatsApp.Whatsapp Message not send.Check mobile %s or check with integration api provider.') % record_phone)
                                    #rec.message_post(body="Whatsapp message to " + partner_id.name + "<br/>" +result.get('messages')[0].get('status') + "<br/>" + msg,attachments=[('%s.pdf' % rec.name, pdf)])
                                    rec.message_post(body="Whatsapp message to: " + str(partner_id.name or partner_id.parent_id.name or '') + "<br/>" + "Mobile:" + str(record_phone or '') + "<br/>" + str( result.get('messages')[0].get('status') or '') +"<br/>"+str(msg or '')+ "<br/>",attachments=[('%s.pdf' % rec.name, pdf)])
                                else:
                                    rec.message_post(body="Whatsapp message to: " + str(partner_id.name or partner_id.parent_id.name or '') + "<br/>" + "Mobile:" + str(record_phone or '') + "<br/>" + str( result.get('messages')[0].get('status') or '') + "<br/>"+str(bdy_msg or '')+ "<br/>",attachments=[('%s.pdf' % rec.name, pdf)])
                            if final_dictionary.get('error'):
                                rec.message_post(body="Whatsapp message to: " + str(partner_id.name or partner_id.parent_id.name or '') + "<br/>" + "Mobile:" + str(record_phone or '') + "<br/>" + str(final_dictionary.get('error') or '') + "<br/>"+"<br/>"+str(bdy_msg or ''),attachments=[('%s.pdf' % rec.name, pdf)])



            else:
                rec.message_post(body="Whatsapp:" + "<br/>" + "Customer does not exist mobile number")
            return


