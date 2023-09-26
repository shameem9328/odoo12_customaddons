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


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_visible_whatsapp = fields.Boolean(string="Is Visible Whastapp", compute="_compute_whatsapp_delivery_visibility")

    # @api.depends('number')
    def _compute_whatsapp_delivery_visibility(self):
        for rec in self:
            rec.is_visible_whatsapp = rec.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.do_whts_available')


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

    # def action_delivery_whatsapp_sent(self):
    #     for rec in self:
    #         record_phone = rec.partner_id.mobile
    #         if record_phone:
    #             record_phone = rec.phone_format(rec.partner_id.mobile)
    #             if  self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.do_template_id'):
    #                 print_template=self.env['ir.actions.report'].sudo().browse(int(self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.do_template_id')))
    #                 pdf=print_template.render_qweb_pdf(rec.id)[0] if print_template else None
    #             else:
    #                 pdf = rec.env.ref('stock.action_report_delivery').render_qweb_pdf(rec.id)[0]
    #             #pdf = self.env.ref('stock.action_report_delivery').render_qweb_pdf(self.id)[0]
    #             if pdf:
    #                 pdf_attachment_id = base64.b64encode(pdf)
    #                 if pdf_attachment_id:
    #                     token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
    #                     instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
    #                     document = pdf_attachment_id
    #                     doc = urllib.parse.quote_plus(document)
    #                     bdy_msg = "Dear *{}*,\nHere is your order is shipped *{}* from {}.\n \nDo not hesitate to contact us if you have any question.\n".format(str(rec.partner_id.name), str(rec.name),str(rec.company_id.name))
    #                     filename = str("Delivery Note\n")
    #                     referenceId = None
    #                     nocache = None
    #                     conn = http.client.HTTPSConnection("api.ultramsg.com")
    #                     headers = {'content-type': "application/x-www-form-urlencoded"}
    #                     payload_doc = f"token={token}&to={record_phone}&filename={filename}&caption={bdy_msg}&document={doc}&referenceId={referenceId}&nocache{nocache}".format(token=token, number=record_phone, filename=filename, doc=doc, referenceId=referenceId,nocache=nocache)
    #                     doc_pst_url = "/{instance_id}/messages/document".format(instance_id=instance_id)
    #                     conn.request("POST", doc_pst_url, payload_doc, headers)
    #                     res = conn.getresponse()
    #                     data_doc = res.read()
    #                     msg_sent_status = data_doc.decode("utf-8")
    #                     final_dictionary = eval(msg_sent_status)
    #                     if final_dictionary.get('sent') == 'true':
    #                         time.sleep(2)
    #                         msg_id = int(final_dictionary.get('id'))
    #                         msg_status_url = "https://api.ultramsg.com/{instance_id}/messages".format(instance_id=instance_id)
    #                         querystring = {
    #                                     "token": token,
    #                                     "page": 1,
    #                                     "limit": 1,
    #                                     "status": "",
    #                                     "sort": "",
    #                                     "id": int(msg_id),
    #                                     "referenceId": "",
    #                                     "from": "",
    #                                     "to": "",
    #                                     "ack": "",
    #                                     "msgId": "",
    #                                     "start_date": "",
    #                                     "end_date": ""
    #                         }
    #                         headers = {'content-type': 'application/x-www-form-urlencoded'}
    #                         response = requests.request("GET", msg_status_url, headers=headers, params=querystring)
    #                         result = json.loads(response.text)
    #                         if result.get('messages')[0].get('status') == 'invalid':
    #                             msg = (_('Failure reason:The number does not have WhatsApp.Whatsapp Message not send.Check mobile %s or check with integration api provider.') % record_phone)
    #                             rec.message_post(body="Status:" + result.get('messages')[0].get('status') + "<br/>" + msg,attachments=[('%s.pdf' % self.name, pdf)])
    #                         elif result.get('messages')[0].get('status') == 'queue':
    #                             rec.message_post(body="Whatsapp Status:" + result.get('messages')[0].get('status') + "<br/>",attachments=[('%s.pdf' % self.name, pdf)])
    #                         else:
    #                             rec.message_post(body="Whatsapp",attachments=[('%s.pdf' % rec.name, pdf)], )
    #                     if final_dictionary.get('error'):
    #                         rec.message_post_with_view("mast_odoo_whatsapp_integration.whatsapp_message_template",
    #                                 values={
    #                                     "message": str(final_dictionary.get('error')),
    #                                     },
    #                                     subtype_id=self.env.ref("mail.mt_note").id,
    #                                     )
    #         else:
    #             rec.message_post(body="Whatsapp:" +"<br/>"+"Customer does not exist mobile number")
    #     return

    def action_delivery_whatsapp_sent(self):
        for rec in self:
            record_phone = rec.partner_id.mobile
            delivery_message_template_message = (rec.company_id.delivery_message_template_message)
            custom_msg = str(self.env['mail.template']._render_template((delivery_message_template_message), 'stock.picking', rec.id) or '')
            do_whts_msg = str(self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.do_whts_msg') or '')
            if do_whts_msg:
                custom_msg += "\n" + do_whts_msg
            if record_phone:
                record_phone = rec.phone_format(rec.partner_id.mobile)
                rec.action_delivery_whatsapp_contactmessage(custom_msg,record_phone,rec.partner_id)
            else:
                rec.message_post(body="Whatsapp:" +"<br/>"+str(rec.partner_id.name or '')+"<br/>"+"Customer does not exist mobile number")
        return


    def action_delivery_whatsapp_contact(self):
        for rec in self:
            contact_wizard=self.env['whatsapp.quotation.multiple.contact'].sudo().search([]).unlink()
            delivery_message_template_message = (rec.company_id.delivery_message_template_message)
            custom_msg = str(self.env['mail.template']._render_template((delivery_message_template_message), 'stock.picking', rec.id) or '')
            do_whts_msg = str(self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.do_whts_msg') or '')
            if do_whts_msg:
                custom_msg+= "\n" +do_whts_msg
            return {'type': 'ir.actions.act_window',
                    'name': _('Whatsapp to contacts'),
                    'res_model': 'whatsapp.quotation.multiple.contact',
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {
                        'default_customer_id': rec.partner_id.id,
                        'default_message':tools.html2plaintext(custom_msg),
                        'default_picking_id': rec.id,
                        },
            }


    def action_done(self):
        res = super(StockPicking, self).action_done()
        do_whts_available = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.do_whts_available')
        do_whts_send_type = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.do_whts_send_type')
        if do_whts_available and do_whts_send_type == 'auto' and self.picking_type_code=='outgoing':
            self.action_delivery_whatsapp_sent()
        return res


    def action_delivery_whatsapp_contactmessage(self,message,mobile_to,partner_id):
        for rec in self:
            record_phone = mobile_to
            if record_phone:
                token = self.env['ir.config_parameter'].sudo().get_param( 'mast_odoo_whatsapp_integration.whatsa_auth_token')
                instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
                if  self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.do_template_id'):
                    print_template=self.env['ir.actions.report'].sudo().browse(int(self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.do_template_id')))
                    pdf=print_template.render_qweb_pdf(rec.id)[0] if print_template else None
                else:
                    pdf = rec.env.ref('stock.action_report_delivery').render_qweb_pdf(rec.id)[0]
                #pdf = self.env.ref('stock.action_report_delivery').render_qweb_pdf(self.id)[0]
                if pdf:
                    pdf_attachment_id = base64.b64encode(pdf)
                    if pdf_attachment_id:
                        document = pdf_attachment_id
                        doc = urllib.parse.quote_plus(document)
                        bdy_msg=str(tools.html2plaintext(message))
                        filename = str("Delivery Note\n")
                        referenceId = None
                        nocache = None
                        conn = http.client.HTTPSConnection("api.ultramsg.com")
                        headers = {'content-type': "application/x-www-form-urlencoded"}
                        payload_doc = f"token={token}&to={record_phone}&filename={filename}&caption={str(urllib.parse.quote(bdy_msg))}&document={doc}&referenceId={referenceId}&nocache{nocache}".format(token=token, number=record_phone, filename=filename,caption=str(bdy_msg), doc=doc, referenceId=referenceId,nocache=nocache)
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
                                rec.message_post(body="Whatsapp message to: " + str(partner_id.name or partner_id.parent_id.name or '') + "<br/>" + "Mobile:" + str(record_phone or '') + "<br/>" + str(result.get('messages')[0].get('status') or '') +"<br/>"+ str(msg or '') + "<br/>",attachments=[('%s.pdf' % rec.name, pdf)])
                            elif result.get('messages')[0].get('status') == 'queue':
                                #rec.message_post(body="Whatsapp message to "+ partner_id.name + "<br/>" + result.get('messages')[0].get('status') + "<br/>",attachments=[('%s.pdf' % rec.name, pdf)])
                                rec.message_post(body="Whatsapp message to: " + str(partner_id.name or partner_id.parent_id.name or '') + "<br/>" + "Mobile:" + str(record_phone or '') + "<br/>" + str(result.get('messages')[0].get('status') or '') + "<br/>" + str(bdy_msg or '') + "<br/>",attachments=[('%s.pdf' % rec.name, pdf)])
                            else:
                                #rec.message_post(body="Whatsapp message to "+ partner_id.name + "<br/>" + result.get('messages')[0].get('status') + "<br/>",attachments=[('%s.pdf' % rec.name, pdf)])
                                rec.message_post(body="Whatsapp message to: " + str(partner_id.name or partner_id.parent_id.name or '') + "<br/>" + "Mobile:" + str(record_phone or '') + "<br/>" + str(result.get('messages')[0].get('status') or '') + "<br/>" + str(bdy_msg or '') + "<br/>", attachments=[('%s.pdf' % rec.name, pdf)])
                        if final_dictionary.get('error'):
                            rec.message_post(body="Whatsapp message to: " + str(partner_id.name or partner_id.parent_id.name or '') + "<br/>" + "Mobile:" + str(record_phone or '') + "<br/>" + str(final_dictionary.get('error') or '') + "<br/>" + "<br/>" + str(bdy_msg or ''),attachments=[('%s.pdf' % rec.name, pdf)])
                            # rec.message_post_with_view("mast_odoo_whatsapp_integration.whatsapp_message_template",
                            #         values={
                            #             "message": str(final_dictionary.get('error')),
                            #             },
                            #             subtype_id=rec.env.ref("mail.mt_note").id,
                            #             )
            else:
                rec.message_post(body="Whatsapp to:"+str(partner_id.name or '')+"<br/>"+"Customer does not exist mobile number!!!")
        return
