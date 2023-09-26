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



class Invoice(models.Model):
    _inherit = 'account.invoice'

    is_visible_whatsapp = fields.Boolean(string="Is Visible Whastapp", compute="_compute_whatsapp_open_inv_visibility")


    #@api.depends('number')
    def _compute_whatsapp_open_inv_visibility(self):
        for rec in self:
            rec.is_visible_whatsapp = rec.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.inv_whts_available')

    def invoice_validate(self):
        res = super(Invoice, self).invoice_validate()
        inv_whts_send_type = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.inv_whts_send_type')
        inv_whts_available = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.inv_whts_available')
        #inv_whts_msg = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.inv_whts_msg')
        if inv_whts_available and inv_whts_send_type=='auto':
            self.action_invoice_whatsapp_sent()
            #record_phone = self.partner_id.mobile
            #if record_phone:
                #record_phone = self.phone_format(self.partner_id.mobile)
                #self.action_invoice_contact_sent(self.partner_id,inv_whts_msg,record_phone)
        return res

    def _phone_get_always_international(self):
        if self.partner_id.company_id:
            return  self.partner_id.company_id.phone_international_format == 'prefix'
        return self.company_id.phone_international_format == 'prefix'


    def _phone_get_country(self):
        if self.partner_id.country_id:
            return self.partner_id.country_id
        return self.company_id.country_id
    def phone_format(self, number, country=None, company=None):
        country = country or self._phone_get_country()
        if not country:
            return number
        #always_international = company.phone_international_format == 'prefix' if company else self._phone_get_always_international()
        return phone_validation.phone_format(
            number,
            country.code if country else None,
            country.phone_code if country else None,
            raise_exception=False
        )

    # def action_invoice_whatsapp_sent(self):
    #     token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
    #     instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
    #     inv_whts_msg = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.inv_whts_msg')
    #     for rec in self:
    #         record_phone = rec.partner_id.mobile
    #         if record_phone:
    #             record_phone = rec.phone_format(rec.partner_id.mobile)
    #             if rec.id:
    #                 conn_inv_msg = http.client.HTTPSConnection("api.ultramsg.com")
    #                 headers = {'content-type': "application/x-www-form-urlencoded"}
    #                 if rec.type=='out_invoice':
    #                     if inv_whts_msg:
    #                         payload_inv_msg = f"token={token}&to={record_phone}&body={inv_whts_msg}&priority=10&referenceId=".format(token=token, number=record_phone, message_body=inv_whts_msg)
    #                         pst_url_inv_msg = "/{instance_id}/messages/chat".format(instance_id=instance_id)
    #                         conn_inv_msg.request("POST", pst_url_inv_msg, payload_inv_msg, headers)
    #                         res_inv_msg = conn_inv_msg.getresponse()
    #                         data_doc = res_inv_msg.read()
    #                         msginv_sent_status = data_doc.decode("utf-8")
    #                         result_dict = eval(msginv_sent_status)
    #                         if result_dict.get('sent') == 'true':
    #                             time.sleep(2)
    #                             msg_id = int(result_dict.get('id'))
    #                             msg_status_url = "https://api.ultramsg.com/{instance_id}/messages".format(instance_id=instance_id)
    #                             querystring = {
    #                                 "token": token,
    #                                 "page": 1,
    #                                 "limit": 1,
    #                                 "status": "",
    #                                 "sort": "",
    #                                 "id": int(msg_id),
    #                                 "referenceId": "",
    #                                 "from": "",
    #                                 "to": "",
    #                                 "ack": "",
    #                                 "msgId": "",
    #                                 "start_date": "",
    #                                 "end_date": ""
    #                             }
    #                             headers = {'content-type': 'application/x-www-form-urlencoded'}
    #                             #time.sleep(2)
    #                             response = requests.request("GET", msg_status_url, headers=headers, params=querystring)
    #                             res = json.loads(response.text)
    #                             if res.get('messages')[0].get('status') == 'invalid':
    #                                 msg = (_('Failure reason:Whatsapp Message not send.Check mobile %s or check with integration api provider.') % record_phone)
    #                                 rec.message_post(body="Status:" + res.get('messages')[0].get('status') + "<br/>" + msg+","+inv_whts_msg)
    #                             elif res.get('messages')[0].get('status') == 'queue':
    #                                 rec.message_post(body="Whatsapp Status:" + res.get('messages')[0].get('status') + "<br/>" + inv_whts_msg)
    #                             else:
    #                                 rec.message_post(body="Whatsapp status:"+"<br/>"+inv_whts_msg)
    #                     portal_link = "%s" % (self.env['ir.config_parameter'].sudo().get_param('web.base.url'),)
    #                     portal_link_ext = portal_link + rec.get_portal_url()
    #                     conn_msg = http.client.HTTPSConnection("api.ultramsg.com")
    #                     headers = {'content-type': "application/x-www-form-urlencoded"}
    #                     bdy_msg = "Hello *{}*,\n your Invoice *{}* with amount {} {} from {}.\n \nPlease remit payment at your earliest convenience.\n\n  If you have any questions, please feel free to contact us\nFor more details:".format(
    #                         str(rec.partner_id.name), str(rec.number), str(rec.currency_id.symbol),
    #                         str(rec.amount_total),
    #                         str(rec.company_id.name))
    #                     if rec.state=='paid':
    #                         bdy_msg = "Hello *{}*,\n your Invoice *{}* with amount {} {} from {}.\n\nThis invoice is already paid.\n\n  If you have any questions, please feel free to contact us\nFor more details:".format(str(rec.partner_id.name), str(rec.number), str(rec.currency_id.symbol),str(rec.amount_total),str(rec.company_id.name))
    #                     bdy_msg += '\n' + portal_link_ext
    #                     payload_msg = f"token={token}&to={record_phone}&body={bdy_msg}&priority=10&referenceId=".format(token=token, number=record_phone, message_body=bdy_msg)
    #                     pst_url_msg = "/{instance_id}/messages/chat".format(instance_id=instance_id)
    #                     conn_msg.request("POST", pst_url_msg, payload_msg, headers)
    #                     res = conn_msg.getresponse()
    #                     data_doc = res.read()
    #                     msg_sent_status = data_doc.decode("utf-8")
    #                     final_dictionary = eval(msg_sent_status)
    #                     if final_dictionary.get('sent') == 'true':
    #                         time.sleep(2)
    #                         msg_id = int(final_dictionary.get('id'))
    #                         msg_status_url = "https://api.ultramsg.com/{instance_id}/messages".format(instance_id=instance_id)
    #                         querystring = {
    #                             "token": token,
    #                             "page": 1,
    #                             "limit": 1,
    #                             "status": "",
    #                             "sort": "",
    #                             "id": int(msg_id),
    #                             "referenceId": "",
    #                             "from": "",
    #                             "to": "",
    #                             "ack": "",
    #                             "msgId": "",
    #                             "start_date": "",
    #                             "end_date": ""
    #                         }
    #                         headers = {'content-type': 'application/x-www-form-urlencoded'}
    #
    #                         response = requests.request("GET", msg_status_url, headers=headers, params=querystring)
    #                         result = json.loads(response.text)
    #                         if result.get('messages')[0].get('status') == 'invalid':
    #                             msg = (_('Failure reason:The number does not have WhatsApp.Whatsapp Message not send.Check mobile %s or check with integration api provider.') % record_phone)
    #                             rec.message_post(body="Status:" + result.get('messages')[0].get('status') + "<br/>" + msg + "<br/>" + bdy_msg)
    #                         elif result.get('messages')[0].get('status') == 'queue':
    #                             rec.message_post(body="Whatsapp Status:" + result.get('messages')[0].get('status') + "<br/>"+bdy_msg)
    #                         else:
    #                             rec.message_post(body=bdy_msg,)
    #                     if final_dictionary.get('error'):
    #                         rec.message_post_with_view("mast_odoo_whatsapp_integration.whatsapp_message_template",
    #                             values={
    #                                 "message": str(final_dictionary.get('error')),
    #                                 },
    #                             subtype_id=self.env.ref("mail.mt_note").id,
    #                             )
    #
    #                     #report_template_id = self.env.ref('account.account_invoices').render_qweb_pdf(self.id)
    #                     # pdf = self.env.ref('account.account_invoices').render_qweb_pdf(self.id)[0]
    #                     # pdf_attachment_id = base64.b64encode(pdf)
    #                     # if pdf_attachment_id:
    #                     #     #pdf_attachment_id = base64.b64encode(report_template_id[0])
    #                     #     if pdf_attachment_id:
    #                     #         document = pdf_attachment_id
    #                     #         doc = urllib.parse.quote_plus(document)
    #                     #         #pdf=self.env.ref('account.account_invoices').retrieve_attachment(self)
    #                     #         filename = str("Invoice-" + str(self.number))
    #                     #         referenceId = None
    #                     #         nocache = None
    #                     #         conn_msg = http.client.HTTPSConnection("api.ultramsg.com")
    #                     #         conn = http.client.HTTPSConnection("api.ultramsg.com")
    #                     #         headers = {'content-type': "application/x-www-form-urlencoded"}
    #                     #         bdy_msg = "Hello *{}*,\n your Invoice *{}* with amount {} {} from {}.\n \nPlease remit payment at your earliest convenience.\n\n  If you have any questions, please feel free to contact us".format(
    #                     #             str(self.partner_id.name), str(self.number), str(self.currency_id.symbol),
    #                     #             str(self.amount_total),
    #                     #             str(self.company_id.name))
    #                     #         bdy_msg+='\n' + portal_link_ext
    #                     #
    #                     #
    #                     #         payload_msg = f"token={token}&to={record_phone}&body={bdy_msg}&priority=10&referenceId=".format(token=token, number=record_phone, message_body=bdy_msg)
    #                     #         pst_url_msg = "/{instance_id}/messages/chat".format(instance_id=instance_id)
    #                     #         payload_doc = f"token={token}&to={record_phone}&filename={filename}&document={doc}&referenceId={referenceId}&nocache{nocache}".format( token=token, number=record_phone, filename=filename, doc=doc, referenceId=referenceId,nocache=nocache)
    #                     #         doc_pst_url = "/{instance_id}/messages/document".format(instance_id=instance_id)
    #                     #         conn_msg.request("POST", pst_url_msg, payload_msg, headers)
    #                     #         conn.request("POST", doc_pst_url, payload_doc, headers)
    #                     #         res = conn.getresponse()
    #                     #         data_doc = res.read()
    #                     #         msg_sent_status = data_doc.decode("utf-8")
    #                     #         final_dictionary = eval(msg_sent_status)
    #                     #         #time.sleep(2)
    #                     #         if final_dictionary.get('sent') == 'true':
    #                     #             msg_id = int(final_dictionary.get('id'))
    #                     #             msg_status_url = "https://api.ultramsg.com/{instance_id}/messages".format(  instance_id=instance_id)
    #                     #             querystring = {
    #                     #                 "token": token,
    #                     #                 "page": 1,
    #                     #                 "limit": 1,
    #                     #                 "status": "",
    #                     #                 "sort": "",
    #                     #                 "id": int(msg_id),
    #                     #                 "referenceId": "",
    #                     #                 "from": "",
    #                     #                 "to": "",
    #                     #                 "ack": "",
    #                     #                 "msgId": "",
    #                     #                 "start_date": "",
    #                     #                 "end_date": ""
    #                     #             }
    #                     #             headers = {'content-type': 'application/x-www-form-urlencoded'}
    #                     #
    #                     #             response = requests.request("GET", msg_status_url, headers=headers, params=querystring)
    #                     #             result = json.loads(response.text)
    #                     #             if result.get('messages')[0].get('status') == 'invalid':
    #                     #                 msg = (_('Failure reason:The number does not have WhatsApp.Whatsapp Message not send.Check mobile %s or check with integration api provider.') %record_phone)
    #                     #                 self.message_post(body= "Status:"+ result.get('messages')[0].get('status')+"<br/>"+msg+"<br/>"+bdy_msg, attachment_ids=pdf.ids)
    #                     #             else:
    #                     #                 #self.message_post(body= "Status:"+ result.get('messages')[0].get('status')+"<br/>"+bdy_msg, attachment_ids=pdf.ids)
    #                     #                 self.message_post(body=bdy_msg, attachments=[('%s.pdf' % self.number, pdf)])
    #                     #
    #                     #         if final_dictionary.get('error'):
    #                     #             self.message_post_with_view("mast_odoo_whatsapp_integration.whatsapp_message_template",
    #                     #                                         values={
    #                     #                                             "message": str(final_dictionary.get('error')),
    #                     #                                         },
    #                     #                                         subtype_id=self.env.ref("mail.mt_note").id,
    #                     #                                         )
    #         else:
    #             rec.message_post(body="Whatsapp:" +"<br/>"+"Customer does not exist mobile number")
    #     return

    def action_invoice_whatsapp_sent(self):
        for rec in self:
            invoice_message_template = (rec.company_id.invoice_message_template_message)
            custom_msg = str(self.env['mail.template']._render_template((invoice_message_template), 'account.invoice', rec.id) or '')
            inv_whts_msg = str(self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.inv_whts_msg') or '')
            custom_msg += "\n" + inv_whts_msg
            record_phone = rec.partner_id.mobile
            if record_phone:
                record_phone = rec.phone_format(rec.partner_id.mobile)
            rec.action_invoice_contact_sent(rec.partner_id,custom_msg,record_phone)





    def action_invoice_whatsapp_contact_sent(self):
        contact_wizard=self.env['whatsapp.quotation.multiple.contact'].sudo().search([]).unlink()
        for rec in self:
            invoice_message_template = (rec.company_id.invoice_message_template_message)
            custom_msg = str(self.env['mail.template']._render_template((invoice_message_template), 'account.invoice', rec.id) or '')
            inv_whts_msg = str(self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.inv_whts_msg') or '')
            custom_msg += "\n" + inv_whts_msg
            return {'type': 'ir.actions.act_window',
                    'name': _('Whatsapp to contacts'),
                    'res_model': 'whatsapp.quotation.multiple.contact',
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {
                        'default_customer_id': rec.partner_id.id,
                        'default_message':str(tools.html2plaintext(custom_msg)),
                        'default_invoice_id': rec.id,
                        },
                    }


    def action_invoice_contact_sent(self,partner_id,message,to):
        token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
        instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
        #inv_whts_msg = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.inv_whts_msg')
        conn = http.client.HTTPSConnection("api.ultramsg.com")
        headers = {'content-type': "application/x-www-form-urlencoded"}
        for rec in self:
            if self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.inv_template_id'):
                print_template = self.env['ir.actions.report'].sudo().browse(int(self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.inv_template_id')))
                pdf = print_template.render_qweb_pdf(rec.id)[0] if print_template else None
            else:
                pdf = rec.env.ref('account.account_invoices').render_qweb_pdf(rec.id)[0]
            record_phone = to
            if record_phone:
                if rec.id:
                    if rec.type=='out_invoice':
                        if pdf:
                            pdf_attachment_id = base64.b64encode(pdf)
                            if pdf_attachment_id:
                                document = pdf_attachment_id
                                doc = urllib.parse.quote_plus(document)
                                bdy_msg = message
                                bdy_msg = str(tools.html2plaintext(bdy_msg))
                                filename = str("Invoice")
                                referenceId = None
                                nocache = None
                                payload_doc = f"token={token}&to={record_phone}&filename={filename}&caption={str(urllib.parse.quote(bdy_msg))}&document={doc}&referenceId={referenceId}&nocache{nocache}".format(  token=token, number=record_phone, filename=filename,caption=str(bdy_msg), doc=doc,referenceId=referenceId, nocache=nocache)
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
                                    response = requests.request("GET", msg_status_url, headers=headers,params=querystring)
                                    result = json.loads(response.text)
                                    if result.get('messages')[0].get('status') == 'invalid':
                                        msg = (_('Failure reason:The number does not have WhatsApp.Whatsapp Message not send.Check mobile %s or check with integration api provider.') % record_phone)
                                        rec.message_post(body="Whatsapp message to: " + str( partner_id.name or partner_id.parent_id.name or '') + "<br/>" + "Mobile:" + str( record_phone or '') + "<br/>" + str(result.get('messages')[0].get('status') or '') + "<br/>"+str(msg or '') ,attachments=[('%s.pdf' % rec.number, pdf)])
                                    else:
                                        rec.message_post(body="Whatsapp message to: " + str(partner_id.name or partner_id.parent_id.name or '') + "<br/>" + "Mobile:" + str( record_phone or '') + "<br/>" + str(result.get('messages')[0].get('status') or '') + "<br/>"+"<br/>"+str(bdy_msg or '') ,attachments=[('%s.pdf' % rec.number, pdf)])
                                if final_dictionary.get('error'):
                                    rec.message_post(body="Whatsapp message to: " + str(partner_id.name or partner_id.parent_id.name or '') + "<br/>" + "Mobile:" + str(record_phone or '') + "<br/>" + str(final_dictionary.get('error') or '') + "<br/>"+"<br/>"+str(bdy_msg or ''),attachments=[('%s.pdf' % rec.number, pdf)])
            else:
                rec.message_post(body="Whatsapp:" +"<br/>"+"Mobile number does not exist")
        return
