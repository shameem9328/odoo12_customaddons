# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
import urllib.parse as parse
from werkzeug import url_encode
from odoo.http import Controller, request, route
import html2text
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import requests
import ssl
import time

from odoo.tools import pytz
from odoo.addons.phone_validation.tools import phone_validation
import urllib.parse
from urllib.parse import quote




from odoo import models, fields, tools
from odoo import api, fields, models, _

# from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
import http.client
import requests
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_visible_whatsapp = fields.Boolean(string="Is Visible Whastapp", compute="_compute_whatsapp_qt_visibility")
    is_visible_order_whatsapp = fields.Boolean(string="Is Visible Order Whastapp", compute="_compute_order_whatsapp_visibility")


    @api.depends('name')
    def _compute_order_whatsapp_visibility(self):
        for rec in self:
            rec.is_visible_order_whatsapp = rec.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.order_whts_available')

    @api.depends('name')
    def _compute_whatsapp_qt_visibility(self):
        for rec in self:
            rec.is_visible_whatsapp = rec.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.qt_whts_available')

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
        #always_international = self._phone_get_always_international()
        return phone_validation.phone_format(
            number,
            country.code if country else None,
            country.phone_code if country else None,
            raise_exception=False
        )

    def usertimezone_order_date_time(self):
        for rec in self:
            user_tz = rec.env.user.tz or pytz.utc
            local = pytz.timezone(user_tz)
            order_date = datetime.strftime(pytz.utc.localize(datetime.strptime(str(rec.date_order), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), "%d/%m/%Y %H:%M:%S")
            return str(order_date or '')

    def user_confirmation_date_time(self):
        for rec in self:
            user_tz = rec.env.user.tz or pytz.utc
            local = pytz.timezone(user_tz)
            confirmation_date = datetime.strftime(pytz.utc.localize(datetime.strptime(str(rec.confirmation_date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), "%d/%m/%Y %H:%M:%S")
            return str(confirmation_date or '')
    def whatsapp_send_msg(self,whatsa_auth_token,instance_id,message,to,partner_id):
        if message:
            #message_string = ''
            #message = message.split(' ')
            #for msg in message:
                #message_string = message_string + msg + '%20'
            #message_string = message_string[:(len(message_string) - 3)]
            #message_string = message_string.encode('UTF-8')
            #message_body = message_string.decode('unicode-escape').encode('utf-8').decode('utf8')
            #message_body=message.encode('UTF-8').decode('unicode-escape')
            message_body=str(tools.html2plaintext(message))
            payload = f"token={whatsa_auth_token}&to={to}&body={str(urllib.parse.quote(message_body))}&priority=10&referenceId=".format(token=whatsa_auth_token, number=to, message_body=str(message_body))
            payload = payload.encode('utf8').decode('iso-8859-1')
            pst_url = "/{instance_id}/messages/chat".format(instance_id=instance_id)
            #conn = http.client.HTTPSConnection("api.ultramsg.com")
            conn = http.client.HTTPSConnection("api.ultramsg.com", context=ssl._create_unverified_context())
            headers = {'content-type': "application/x-www-form-urlencoded"}
            conn.request("POST", pst_url, payload, headers)
            res = conn.getresponse()
            data = res.read()
            msg_sent_status = data.decode("utf-8")
            final_dictionary = eval(msg_sent_status)
            #print("final_dictionary",final_dictionary)
            if final_dictionary.get('error'):
                self.message_post(body="Whatsapp message to: " + str(partner_id.name)+ "<br/>" + "Mobile:" + str(to or '')  + "<br/>" +"Status:"+ str(final_dictionary.get('error') or '')+ "<br/>" +"Message:"+str(message_body or ''))
                #self.message_post(body=str(final_dictionary.get('error')),subject="ASAS")
                # self.message_post_with_view("mast_odoo_whatsapp_integration.whatsapp_message_template",
                #                 values={
                #                          "message": "Whatsapp message to "+"\n"+partner_id.name+"\n"+"Mobile:"+to +"\n"+str(final_dictionary.get('error')),
                #                  },
                #                          subtype_id=self.env.ref("mail.mt_note").id,
                #                  )
            if final_dictionary.get('sent')=='true':
                if self.state=='draft':
                    self.update({'state':'sent'})
                time.sleep(2)
                msg_id = int(final_dictionary.get('id'))
                msg_status_url = "https://api.ultramsg.com/{instance_id}/messages".format(instance_id=instance_id)
                querystring = {
                    "token": whatsa_auth_token,
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
                res=json.loads(response.text)
                if res.get('messages')[0].get('status') == 'invalid':
                    msg=(_('Failure reason:Whatsapp Message not send.Check mobile  %s or check with integration api provider.') % to)
                    #self.message_post(body="Whatsapp message to: "+""+partner_id.name or partner_id.parent_id.name+"<br/>"+"Mobile:"+to +"<br/>"+"Whatsapp Status:" + res.get('messages')[0].get('status') + "<br/>"+msg+"<br/>")
                    self.message_post(body="Whatsapp message to: " + str(partner_id.name or partner_id.parent_id.name or '')+ "<br/>" + "Mobile:"+str(to or'') +"<br/>"+str(res.get('messages')[0].get('status') or '') + "<br/>"+str(msg or ''))
                elif res.get('messages')[0].get('status') == 'queue':
                    self.message_post(body="Whatsapp message to: " + str(partner_id.name or partner_id.parent_id.name or '')+ "<br/>" + "Mobile:"+str(to or'') +"<br/>"+str(res.get('messages')[0].get('status') or '') + "<br/>"+str(message_body or ''))
                else:
                    self.message_post(body="Whatsapp message to: " + str(partner_id.name or partner_id.parent_id.name or '')+ "<br/>" + "Mobile:"+str(to or'') +"<br/>"+str(res.get('messages')[0].get('status') or '') + "<br/>"+str(message_body or ''))
            return final_dictionary
        else:
            return

    # def quotation_whatsapp(self):
    #     #qt_message_template = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.qt_message_template_message')
    #     qt_message_template = self.company_id.qt_message_template_message
    #
    #     print("qt_message_template",qt_message_template)
    #     subject = self.env['mail.template']._render_template((qt_message_template), 'sale.order', self.id)
    #     print("subjects",subject)
    #
    #     whatsa_auth_token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
    #     instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
    #     to=None
    #     if self.partner_id.mobile:
    #         to = self.phone_format(self.partner_id.mobile)
    #     custom_msg=''
    #     user_tz = self.env.user.tz or pytz.utc
    #     local = pytz.timezone(user_tz)
    #     if self.state == 'draft' or self.state == 'sent':
    #         order_date = datetime.strftime(pytz.utc.localize(datetime.strptime(str(self.date_order), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), "%d/%m/%Y %H:%M:%S")
    #         custom_msg += "Hello *{}*,\n your Quotation *{}* with amount *{} {}* is ready.\n \nYour quotation date and time is:\n *{}*.\n\n  If you have any questions, please feel free to contact us.\n\n Please check the link below for more details:{}\n".format(str(self.partner_id.name),str(self.name),str(self.currency_id.symbol),str(self.amount_total),order_date,self.get_base_url()+self.get_portal_url())
    #         qt_whts_msg = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.qt_whts_msg')
    #         if qt_whts_msg:
    #             qt_whts_msg = "Hello " + self.partner_id.name + "\n" + qt_whts_msg
    #             self.whatsapp_send_msg(whatsa_auth_token, instance_id, qt_whts_msg, to,self.partner_id)
    #         else:
    #             self.whatsapp_send_msg(whatsa_auth_token, instance_id, custom_msg, to, self.partner_id)
    #     else:
    #         confirmation_date = datetime.strftime(pytz.utc.localize(datetime.strptime(str(self.confirmation_date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), "%d/%m/%Y %H:%M:%S")
    #         custom_msg += "Hello *{}*,\n your Sale Order Number *{}* with amount *{} {}* is Confirmed. \n\nYour Sale Order date and time is:\n *{}*.\n\n  If you have any questions, please feel free to contact us.\n\n Please check the link below for more details:{}\n".format(str(self.partner_id.name),str(self.name),str(self.currency_id.symbol),str(self.amount_total),confirmation_date,self.get_base_url()+self.get_portal_url())
    #         order_whts_msg = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.order_whts_msg')
    #         if self.state in ['sale','done']:
    #             if order_whts_msg:
    #                 order_whts_msg= "Hello " + self.partner_id.name + "\n" +order_whts_msg
    #                 self.whatsapp_send_msg(whatsa_auth_token, instance_id, order_whts_msg, to,self.partner_id)
    #             else:
    #                 self.whatsapp_send_msg(whatsa_auth_token,instance_id,custom_msg,to,self.partner_id)


    def quotation_whatsapp(self):
        for rec in self:
            qt_message_template = rec.company_id.qt_message_template_message
            body_message = str(self.env['mail.template']._render_template((qt_message_template), 'sale.order', rec.id) or '')
            whatsa_auth_token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
            instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
            to=None
            if rec.partner_id.mobile:
                to = rec.phone_format(rec.partner_id.mobile)
            if rec.state in['draft','sent']:
                qt_whts_msg = str(self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.qt_whts_msg') or '')
                body_message+="\n"+qt_whts_msg
                rec.whatsapp_send_msg(whatsa_auth_token, instance_id, body_message, to,rec.partner_id)
            else:
                order_message_template_message = rec.company_id.order_message_template_message
                if rec.state in ['sale','done']:
                    body_message_order = self.env['mail.template']._render_template((order_message_template_message), 'sale.order',rec.id)
                    order_whts_msg = str(self.env['ir.config_parameter'].sudo().get_param( 'mast_odoo_whatsapp_integration.order_whts_msg') or '')
                    body_message_order += "\n\n" + order_whts_msg
                    rec.whatsapp_send_msg(whatsa_auth_token,instance_id,body_message_order,to,rec.partner_id)




    def quotation_whatsapp_contacts(self):
        for rec in self:
            body_message=''
            if rec.state in ['draft','sent']:
                qt_message_template = rec.company_id.qt_message_template_message
                body_message = str(self.env['mail.template']._render_template((qt_message_template), 'sale.order', rec.id)or '')
                qt_whts_msg = str(self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.qt_whts_msg') or '')
                body_message += "\n" + qt_whts_msg
            else:
                order_message_template_message = rec.company_id.order_message_template_message
                body_message = str(self.env['mail.template']._render_template((order_message_template_message), 'sale.order', rec.id) or '')
                order_whts_msg = str(self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.order_whts_msg')or '')
                body_message += "\n" + order_whts_msg

            contact_wizard=self.env['whatsapp.quotation.multiple.contact'].sudo().search([]).unlink()
            return {'type': 'ir.actions.act_window',
                    'name': _('Whatsapp to contacts'),
                    'res_model': 'whatsapp.quotation.multiple.contact',
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {
                        'default_customer_id': rec.partner_id.id,
                        'default_message':str(tools.html2plaintext(body_message)),
                        'default_sale_order_id': rec.id,
                        },
                    }



    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.state in ['sale','done']:
            order_whts_available = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.order_whts_available')
            order_whts_send_type = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.order_whts_send_type')
            if order_whts_available and order_whts_send_type=='auto':
                self.quotation_whatsapp()
        return  res

    # def _run_check_quotation_followup(self):
    #     print("_run_check_quotation_followup")
    #     is_qt_whts_flwup = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.qt_whts_flwup')
    #     is_qt_whts_available=self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.qt_whts_available')
    #     whatsa_auth_token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
    #     instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
    #     if is_qt_whts_available and is_qt_whts_flwup:
    #         sale_order_obj=self.env['sale.order'].sudo().search([('state','in',['draft','sent'])])
    #         if sale_order_obj:
    #             if whatsa_auth_token and  instance_id:
    #                 qt_flwp_msg = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.qt_flwp_msg')
    #                 for rec in sale_order_obj:
    #                     if rec.partner_id.mobile:
    #                         to = rec.phone_format(rec.partner_id.mobile)
    #                         res=rec.whatsapp_send_msg(whatsa_auth_token, instance_id, qt_flwp_msg, to,rec.partner_id)
    #                         # if res and res.get('sent') == 'true':
    #                         #     rec.message_post_with_view("mast_odoo_whatsapp_integration.whatsapp_message_template",
    #                         #     values={
    #                         #             "message": qt_flwp_msg,
    #                         #     },
    #                         #     subtype_id=self.env.ref("mail.mt_note").id,
    #                         # )
    #             else:
    #                 _logger.error("Token or Instance Id not set!.Set It In Settings First")

    # def _run_check_order_followup(self):
    #     is_order_whts_flwup = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.order_whts_flwup')
    #     is_order_whts_available=self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.order_whts_available')
    #     whatsa_auth_token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
    #     instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
    #     if is_order_whts_available and  is_order_whts_flwup:
    #         sale_order_obj=self.env['sale.order'].sudo().search([('state','in',['sale','done'])])
    #         if sale_order_obj:
    #             if  whatsa_auth_token and instance_id:
    #                 order_flwp_msg = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.order_flwp_msg')
    #                 for rec in sale_order_obj:
    #                     if rec.partner_id.mobile:
    #                         to = rec.phone_format(rec.partner_id.mobile)
    #                         res=rec.whatsapp_send_msg(whatsa_auth_token, instance_id, order_flwp_msg, to,rec.partner_id)
    #             else:
    #                 _logger.error("Token or Instance Id not set!.Set It In Settings First")


    def _run_check_quotation_followup(self):
        is_qt_whts_flwup = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.qt_whts_flwup')
        is_qt_whts_available = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.qt_whts_available')
        if is_qt_whts_available and is_qt_whts_flwup:
            sale_order_obj = self.env['sale.order'].sudo().search([('state', 'in', ['draft', 'sent'])])
            qt_flwp_msg = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.qt_flwp_msg')
            whatsa_auth_token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
            instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
            if sale_order_obj:
                for so in sale_order_obj:
                    to=so.partner_id.mobile
                    if so.partner_id.mobile:
                        to = so.phone_format(so.partner_id.mobile)
                    so.whatsapp_send_msg(whatsa_auth_token, instance_id, qt_flwp_msg, to,so.partner_id)


    def _run_check_order_followup(self):
        is_order_whts_flwup = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.order_whts_flwup')
        is_order_whts_available = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.order_whts_available')
        whatsa_auth_token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
        instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
        if is_order_whts_available and  is_order_whts_flwup:
            sale_order_obj=self.env['sale.order'].sudo().search([('state','in',['sale','done'])])
            order_flwp_msg = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.order_flwp_msg')
            if sale_order_obj:
                for so in sale_order_obj:
                    to = so.partner_id.mobile
                    if so.partner_id.mobile:
                        to = so.phone_format(so.partner_id.mobile)
                    so.whatsapp_send_msg(whatsa_auth_token, instance_id, order_flwp_msg, to, so.partner_id)



    # def onchange_template_id(self, template_id, model, res_id):
    #     if template_id:
    #         values = self.generate_email_for_composer(template_id, [res_id])[res_id]
    #     else:
    #         default_values = self.with_context(default_model=model, default_res_id=res_id).default_get(['model', 'res_id', 'partner_ids', 'message'])
    #         values = dict((key, default_values[key]) for key in['body', 'partner_ids'] if key in default_values)
    #     #values = self._convert_to_write(values)
    #     print("values",values)
    #     return {'value': values}




    # def generate_email_for_composer(self, template_id, res_ids, fields=None):
    #     multi_mode = True
    #     if isinstance(res_ids, int):
    #         multi_mode = False
    #         res_ids = [res_ids]
    #     if fields is None:
    #         fields = ['body_html']
    #     returned_fields = fields + ['partner_ids']
    #     values = dict.fromkeys(res_ids, False)
    #     template_values = self.env['mail.template'].with_context(tpl_partners_only=True).browse(template_id).generate_email(res_ids, fields=fields)
    #     for res_id in res_ids:
    #         res_id_values = dict((field, template_values[res_id][field]) for field in returned_fields if template_values[res_id].get(field))
    #         res_id_values['message'] =(res_id_values.pop('body_html', ''))
    #         print(" res_id_values['message']", res_id_values['message'])
    #         values[res_id] = res_id_values
    #     print("values",values)
    #     return multi_mode and values or values[res_ids[0]]














