# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api,tools
import html2text
from odoo.tools.translate import _
import re
from odoo.addons.phone_validation.tools import phone_validation
import json
import time
import http.client
import http.client
import requests
import base64
import urllib.parse


class Partner(models.Model):
    _inherit = 'res.partner'

    is_visible_whatsapp = fields.Boolean(string="Is Visible Whastapp", compute="_compute_whatsapp_partner_visibility")


    def _compute_whatsapp_partner_visibility(self):
        for rec in self:
            rec.is_visible_whatsapp = rec.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.customer_flwup_whts_available')

    def _phone_get_always_international(self):
        if self.partner_id.company_id:
            return self.partner_id.company_id.phone_international_format == 'prefix'
        return self.company_id.phone_international_format == 'prefix'

    def _phone_get_country(self):
        if self.country_id:
            return self.country_id
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



    def action_followup_whatsapp_sent(self):
        customer_flwup_whts_available = self.env['ir.config_parameter'].sudo().get_param( 'mast_odoo_whatsapp_integration.customer_flwup_whts_available')
        if customer_flwup_whts_available:
            for record in self:
                #followup_message_template_message = str(record.company_id.overdue_msg or '')
                followup_message_template_message = str(self.env['mail.template']._render_template((record.company_id.overdue_msg), 'res.partner', record.id) or '')
                statement_whts_msg = self.env['ir.config_parameter'].sudo().get_param( 'mast_odoo_whatsapp_integration.statement_whts_msg')
                if statement_whts_msg:
                    followup_message_template_message += "\n" + statement_whts_msg
                record_mobile=record.mobile
                if record.mobile:
                    record_mobile = record.phone_format(record.mobile)
                record.action_statement_contact_sent(record, followup_message_template_message, record_mobile)

    @api.model
    def _run_check_customerfollowup_followup(self):
        customer_flwup_whts_available = self.env['ir.config_parameter'].sudo().get_param( 'mast_odoo_whatsapp_integration.customer_flwup_whts_available')
        customer_flwup_whts_send_type = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.customer_flwup_whts_send_type')
        if customer_flwup_whts_available and customer_flwup_whts_send_type=='auto':
            res_partner = self.env['res.partner'].sudo().search(['|', ('parent_id', '=', False), ('is_company', '=', True)])
            for rec in res_partner:
                if rec.followup_status in ['in_need_of_action','with_overdue_invoices']:
                    rec.action_followup_whatsapp_sent()


    def action_statement_contact_sent(self,partner_id,message,mobile):
        token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
        instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
        customer_flwup_whts_available = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.customer_flwup_whts_available')
        for rec in self:
            if customer_flwup_whts_available:
                for record in partner_id:
                    res_ids = rec['ids'] if 'ids' in rec else rec.ids
                    pdf = record.env.ref('account_reports.action_report_followup').render_qweb_pdf(res_ids)[0]
                    pdf_attachment_id = base64.b64encode(pdf)
                    if pdf_attachment_id:
                        doc = urllib.parse.quote_plus(pdf_attachment_id)
                        custom_msg = message
                        custom_msg = str(tools.html2plaintext(custom_msg))
                        filename = "Followup Statement"
                        referenceId = None
                        nocache = None
                        conn_msg = http.client.HTTPSConnection("api.ultramsg.com")
                        headers = {'content-type': "application/x-www-form-urlencoded"}
                        if mobile:
                            record_mobile = mobile
                            payload_doc = f"token={token}&to={record_mobile}&filename={filename}&caption={str(urllib.parse.quote(custom_msg))}&document={doc}&referenceId={referenceId}&nocache{nocache}".format(token=token, number=record_mobile, filename=filename, caption=custom_msg, doc=doc,referenceId=referenceId, nocache=nocache)
                            payload_doc = payload_doc.encode('utf8').decode('iso-8859-1')
                            doc_pst_url = "/{instance_id}/messages/document".format(instance_id=instance_id)
                            conn_msg.request("POST", doc_pst_url, payload_doc, headers)
                            res = conn_msg.getresponse()
                            data_doc = res.read()
                            msg_sent_status = data_doc.decode("utf-8")
                            final_dictionary = eval(msg_sent_status)
                            time.sleep(2)
                            if final_dictionary.get('sent') == 'true':
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
                                #print("result.get('messages')[0].get('status')",result.get('messages')[0].get('status'))
                                if result.get('messages')[0].get('status') == 'invalid':
                                    msg = (('Failure reason:The number does not have WhatsApp.Whatsapp Message not send.Check mobile %s or check with integration api provider.') % record_mobile)
                                    #rec.message_post( body="Whatsapp message to " + record.name + "<br/>" + result.get('messages')[0].get('status') + "<br/>"+msg , attachments=[('%s.pdf' % rec.name, pdf)])
                                    rec.message_post(body="Whatsapp message to: " + str(record.name or record.parent_id.name or '') + "<br/>" + "Mobile:" + str(record_mobile or '') + "<br/>" +"Status:"+ str(result.get('messages')[0].get('status') or '') +"<br/>"+ str(msg or '') + "<br/>",attachments=[('%s.pdf' % rec.name, pdf)])
                                elif result.get('messages')[0].get('status') == 'queue':
                                    #rec.message_post( body="Whatsapp message to " + record.name + "<br/>" + result.get('messages')[0].get('status') + "<br/>", attachments=[('%s.pdf' % rec.name, pdf)])
                                    rec.message_post(body="Whatsapp message to: " + str(record.name or record.parent_id.name or '') + "<br/>" + "Mobile:" + str(record_mobile or '') + "<br/>" +"Status:"+ str( result.get('messages')[0].get('status') or '') + "<br/>" + str(custom_msg or '') + "<br/>", attachments=[('%s.pdf' % rec.name, pdf)])
                                else:
                                    #rec.message_post( body="Whatsapp message to " + record.name + "<br/>" + result.get('messages')[0].get('status') + "<br/>", attachments=[('%s.pdf' % rec.name, pdf)])
                                    rec.message_post(body="Whatsapp message to: " + str(record.name or record.parent_id.name or '') + "<br/>" + "Mobile:" + str(record_mobile or '') + "<br/>" +"Status:"+ str( result.get('messages')[0].get('status') or '') + "<br/>" + str(custom_msg or '') + "<br/>", attachments=[('%s.pdf' % rec.name, pdf)])

                            if final_dictionary.get('error'):
                                rec.message_post(body="Whatsapp message to: " + str(record.name or record.parent_id.name or '') + "<br/>" + "Mobile:" + str(record_mobile or '') + "<br/>" +"Status:"+ str(final_dictionary.get('error') or '') + "<br/>" + "<br/>" + str(custom_msg or ''),   attachments=[('%s.pdf' % rec.name, pdf)])
                        else:
                            rec.message_post(body="Whatsapp message to: " + str(record.name or record.parent_id.name or '') + "<br/>" + "Status:" +  "<br/>" + str("Mobile number does not exist!!!") + "<br/>", attachments=[('%s.pdf' % rec.name, pdf)])

    def action_followup_contact_whatsapp_sent(self):
        for rec in self:
            #followup_message_template_message = str(rec.company_id.overdue_msg or '')
            followup_message_template_message = str(self.env['mail.template']._render_template((rec.company_id.overdue_msg), 'res.partner', rec.id) or '')
            statement_whts_msg = str(self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.statement_whts_msg')or '')
            if statement_whts_msg:
                followup_message_template_message+="\n"+statement_whts_msg
            return {'type': 'ir.actions.act_window',
                    'name': _('Whatsapp to contacts'),
                    'res_model': 'whatsapp.quotation.multiple.contact',
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {
                        'default_customer_id': rec.id,
                        'default_message':tools.html2plaintext(followup_message_template_message),
                        'default_statement_id': rec.id,
                        },
                    }
