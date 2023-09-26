# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
from itertools import groupby
import json
import http.client
import http.client
import base64
import urllib.parse
import requests
import babel.dates
import collections
import datetime
from datetime import timedelta, MAXYEAR
from dateutil import rrule
from dateutil.relativedelta import relativedelta
import logging
from operator import itemgetter
import pytz
import re
import time
import uuid
from datetime import datetime
from odoo import api, fields, models
from odoo import tools
from odoo.osv import expression
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
from odoo.exceptions import UserError, ValidationError

from datetime import datetime
from datetime import date

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import requests

_logger = logging.getLogger(__name__)


class Alarm(models.Model):
    _inherit = 'calendar.alarm'

    type = fields.Selection(selection_add=[('whatsapp', 'WhatsApp')])


class MeetingCustom(models.Model):
    _inherit = 'calendar.event'

    is_visible_whatsapp = fields.Boolean(string="Is Visible Whastapp", compute="_compute_whatsapp_calendar_visibility")

    def _compute_whatsapp_calendar_visibility(self):
        for rec in self:
            rec.is_visible_whatsapp = rec.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.appointment_whts_available')

    def action_confirm(self):
        res = super().action_confirm()
        calendar_whts_available = self.env['ir.config_parameter'].sudo().get_param(
            'mast_odoo_whatsapp_integration.appointment_whts_available')
        appointment_whts_send_type = self.env['ir.config_parameter'].sudo().get_param(
            'mast_odoo_whatsapp_integration.appointment_whts_send_type')
        for rec in self:
            if calendar_whts_available and appointment_whts_send_type == 'auto':
                rec.action_whatsapp()
        return res

    def action_done(self):
        res = super().action_done()
        calendar_whts_available = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.appointment_whts_available')
        appointment_whts_send_type = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.appointment_whts_send_type')
        for rec in self:
            if calendar_whts_available and appointment_whts_send_type == 'auto':
                rec.action_whatsapp()
        return res

    def action_cancel(self):
        res = super().action_cancel()
        calendar_whts_available = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.appointment_whts_available')
        appointment_whts_send_type = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.appointment_whts_send_type')
        for rec in self:
            if calendar_whts_available and appointment_whts_send_type == 'auto':
                rec.action_whatsapp()
        return res

    def action_whatsapp(self):
        for rec in self:
            if rec.attendee_ids:
                participants = rec.mapped('attendee_ids').filtered(lambda att: att.state != 'declined')
                for attendies in participants:
                    attendies.action_send_whatsapp_appointments()
                    #attendies.action_send_whatsapp_remainder_appointments()

    def action_send_whatsapp_appointments(self, message, to, employee):
        token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
        instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
        calendar_whts_available = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.appointment_whts_available')
        conn_calendar_msg = http.client.HTTPSConnection("api.ultramsg.com")
        headers = {'content-type': "application/x-www-form-urlencoded"}
        if calendar_whts_available:
            for rec in self:
                if calendar_whts_available:
                    custom_message = str(tools.html2plaintext(message))
                    payload_calendar_msg = f"token={token}&to={to}&body={str(urllib.parse.quote(custom_message))}&priority=10&referenceId=".format(token=token, number=to, message_body=custom_message)
                    payload_calendar_msg = payload_calendar_msg.encode('utf8').decode('iso-8859-1')
                    pst_url_calendar_msg = "/{instance_id}/messages/chat".format(instance_id=instance_id)
                    conn_calendar_msg.request("POST", pst_url_calendar_msg, payload_calendar_msg, headers)
                    res_inv_msg = conn_calendar_msg.getresponse()
                    data_doc = res_inv_msg.read()
                    msg_sent_status = data_doc.decode("utf-8")
                    result_dict = eval(msg_sent_status)
                    if result_dict.get('sent') == 'true':
                        time.sleep(2)
                        msg_id = int(result_dict.get('id'))
                        msg_status_url = "https://api.ultramsg.com/{instance_id}/messages".format(
                            instance_id=instance_id)
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
                        res = json.loads(response.text)
                        if res.get('messages')[0].get('status') == 'invalid':
                            msg = (_('Failure reason:Whatsapp Message not send.Check mobile %s or check with integration api provider.') % employee.mobile)
                            rec.message_post(body="Whatsapp message to :" + employee.name + "<br/>" + res.get('messages')[0].get('status') + "<br/>" + msg + "<br/>" + custom_message)
                        elif res.get('messages')[0].get('status') == 'queue':
                            rec.message_post(body="Whatsapp message to :" + employee.name + "<br/>" + res.get('messages')[0].get('status') + "<br/>" + custom_message)
                        else:
                            rec.message_post(body="Whatsapp message to :" + "<br/>" + employee.name + "<br/>" + res.get('messages')[0].get('status') + "<br/>" + custom_message)
                    if result_dict.get('error'):
                        rec.message_post(body="Whatsapp message to :" + "<br/>" + employee.name + "<br/>" + str(
                            result_dict.get('error')))

    @api.model
    def today_appointments_whatsapp(self):
        today = date.today()
        employees = self.env['res.partner'].search([('employee', '=', True)])
        for employee in employees:
            events = self.env['calendar.attendee'].search([('start_date', '=', today), ('partner_id', '=', employee.id), ('status', '=', 'open')], order='start_datetime asc')
            message = "Today Meetings:\n\n"
            first = True
            if not events:
                continue
            x = 1
            for event in events:
                if not event.event_id.appointment_type_id:
                    continue
                if x != 1:
                    message += "\n\n"
                message += str(x) + ") Subject: " + event.event_id.name + "\n" + "Location: " + event.event_id.location + "\n" + "Time: " + event.start_time
                x = x + 1
            if employee.mobile:
                partner_mobile = employee.phone_format(employee.mobile)
                token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
                instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
                calendar_whts_available = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.appointment_whts_available')
                appointment_whts_send_type = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.appointment_whts_send_type')
                conn_calendar_msg = http.client.HTTPSConnection("api.ultramsg.com")
                headers = {'content-type': "application/x-www-form-urlencoded"}
                if calendar_whts_available and appointment_whts_send_type == 'auto':
                    if calendar_whts_available:
                        custom_message = message
                        custom_message=tools.html2plaintext(custom_message)
                        payload_calendar_msg = f"token={token}&to={partner_mobile}&body={str(urllib.parse.quote(custom_message))}&priority=10&referenceId=".format(token=token, number=partner_mobile, message_body=str(custom_message))
                        payload_calendar_msg = payload_calendar_msg.encode('utf8').decode('iso-8859-1')
                        pst_url_calendar_msg = "/{instance_id}/messages/chat".format(instance_id=instance_id)
                        conn_calendar_msg.request("POST", pst_url_calendar_msg, payload_calendar_msg, headers)
                        res_inv_msg = conn_calendar_msg.getresponse()
                        data_doc = res_inv_msg.read()
                        msg_sent_status = data_doc.decode("utf-8")
                        result_dict = eval(msg_sent_status)
                        if result_dict.get('sent') == 'true':
                            time.sleep(2)
                            msg_id = int(result_dict.get('id'))
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
                            res = json.loads(response.text)
                            if res.get('messages')[0].get('status') == 'invalid':
                                msg = (_('Failure reason:Whatsapp Message not send.Check mobile %s or check with integration api provider.') % employee.mobile)
                                #employee.message_post(body="Whatsapp message to :" + employee.name + "<br/>" + res.get('messages')[0].get('status') + "<br/>" + msg + "<br/>" + custom_message)
                                employee.message_post(body="Whatsapp message to: " + str(employee.name or '') + "<br/>" + "Mobile:" + str(partner_mobile or '') + "<br/>" + str(res.get('messages')[0].get('status') or '') + "<br/>" + str(msg or ''))

                            elif res.get('messages')[0].get('status') == 'queue':
                                employee.message_post(body="Whatsapp message to: " + str(employee.name or '') + "<br/>" + "Mobile:" + str(partner_mobile or '') + "<br/>" + str( res.get('messages')[0].get('status') or '') + "<br/>" + str(custom_message or ''))
                            else:
                                employee.message_post(body="Whatsapp message to: " + str(employee.name or '') + "<br/>" + "Mobile:" + str(partner_mobile or '') + "<br/>" + str( res.get('messages')[0].get('status') or '') + "<br/>" + str(custom_message or ''))
                        if result_dict.get('error'):
                            #employee.message_post(body="Whatsapp message to :" + "<br/>" + employee.name + "<br/>" + str(result_dict.get('error')))
                            employee.message_post(body="Whatsapp message to: " + str(employee.name or '') + "<br/>" + "Mobile:" + str(partner_mobile or '') + "<br/>" + str( str(result_dict.get('error')) or '') + "<br/>" + str(custom_message or ''))
            else:
                employee.message_post(body="Whatsapp message to: " + str(employee.name or '')  + "<br/>" + "Mobile Number does not exist")


class Attendee(models.Model):
    _inherit = 'calendar.attendee'

    # def action_send_whatsapp_appointments(self):
    #     token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
    #     instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
    #     calendar_whts_available = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.appointment_whts_available')
    #     conn_calendar_msg = http.client.HTTPSConnection("api.ultramsg.com")
    #     headers = {'content-type': "application/x-www-form-urlencoded"}
    #     if calendar_whts_available:
    #         for rec in self:
    #             attendencies = []
    #             state = dict(rec.event_id._fields['state'].selection).get(rec.event_id.state)
    #             for att in rec.event_id.attendee_ids:
    #                 if att.common_name != rec.common_name:
    #                     attendencies.append("\n" + "-" + str(att.common_name) or '')
    #                 else:
    #                     attendencies.insert(0, "-" + "You")
    #             if calendar_whts_available:
    #                 for partner in rec:
    #                     day = partner.start_date and (datetime.strptime(str(partner.start_date), '%Y-%m-%d').date()).strftime('%A') or ''
    #                     custom_message = "Dear *{}*,\nThis is to inform you that your meeting on {} {} at {} has been {}.\nSubject:{}\nLocation:{}\nAttendees:\n {}\n\n Best Regards,\n\n Mast Team".format(
    #                         str(partner.common_name), str(day), str(partner.start_date), str(partner.start_time),
    #                         str(state),
    #                         str(rec.event_id.name), str(rec.event_id.location if rec.event_id.location else ''),
    #                         str(''.join(attendencies)))
    #                     if partner.partner_id.mobile:
    #                         partner_mobile = partner.partner_id.phone_format(partner.partner_id.mobile)
    #                         payload_calendar_msg = f"token={token}&to={partner_mobile}&body={custom_message}&priority=10&referenceId=".format(token=token, number=partner_mobile, message_body=custom_message)
    #                         pst_url_calendar_msg = "/{instance_id}/messages/chat".format(instance_id=instance_id)
    #                         conn_calendar_msg.request("POST", pst_url_calendar_msg, payload_calendar_msg, headers)
    #                         res_inv_msg = conn_calendar_msg.getresponse()
    #                         data_doc = res_inv_msg.read()
    #                         msg_sent_status = data_doc.decode("utf-8")
    #                         result_dict = eval(msg_sent_status)
    #                         if result_dict.get('sent') == 'true':
    #                             time.sleep(2)
    #                             msg_id = int(result_dict.get('id'))
    #                             msg_status_url = "https://api.ultramsg.com/{instance_id}/messages".format(
    #                                 instance_id=instance_id)
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
    #                             # time.sleep(2)
    #                             response = requests.request("GET", msg_status_url, headers=headers, params=querystring)
    #                             res = json.loads(response.text)
    #                             if res.get('messages')[0].get('status') == 'invalid':
    #                                 msg = (_('Failure reason:Whatsapp Message not send.Check mobile %s or check with integration api provider.') % partner_mobile)
    #                                 rec.event_id.message_post(body="Whatsapp message to :" + partner.common_name + "<br/>" +res.get('messages')[0].get('status') + "<br/>" + msg + "<br/>" + custom_message)
    #                             elif res.get('messages')[0].get('status') == 'queue':
    #                                 rec.event_id.message_post(body="Whatsapp message to :" + partner.common_name + "<br/>" +res.get('messages')[0].get('status') + "<br/>" + custom_message)
    #                             else:
    #                                 rec.event_id.message_post(body="Whatsapp message to :" + "<br/>" + partner.common_name + "<br/>" +res.get('messages')[0].get('status') + "<br/>" + custom_message)
    #                         if result_dict.get('error'):
    #                             rec.event_id.message_post(body="Whatsapp message to :" + "<br/>" + partner.common_name + "<br/>" + str(result_dict.get('error')))
    @api.model
    def get_event_state(self):
        for rec in self:
            if rec.event_id:
                return dict(rec.event_id._fields['state'].selection).get(rec.event_id.state)
            return

    def get_event_day(self):
        for rec in self:
            if rec.start_date:
                return str(rec.start_date and (datetime.strptime(str(rec.start_date), '%Y-%m-%d').date()).strftime('%A') or '')
            return ''

    def get_attendencies(self):
        for rec in self:
            attendencies = []
            for att in rec.event_id.attendee_ids:
                if att.common_name != rec.common_name:
                    attendencies.append("\n" + "-" + str(att.common_name) or '')
                else:
                    attendencies.insert(0, "-" + "You")
            return   str(''.join(attendencies))

    def get_event_name(self):
        for rec in self:
            if rec.event_id:
                return str(rec.event_id.name)
            return

    def get_remainder_attendencies(self):
        for rec in self:
            attendencies = []
            for att in rec.event_id.attendee_ids:
                if att.common_name != rec.common_name:
                    attendencies.append("\n" + "-" + att.common_name + ("," if att.partner_id.mobile else "") + str(att.partner_id.mobile or ''))
                else:
                    attendencies.insert(0, "-" + "You")
            return str(''.join(attendencies))

    def get_remainder_hr(self):
        for rec in self:
            tz = pytz.timezone(rec.env.user.tz)
            NUMBER_OF_SECONDS = 86400  # seconds in 24 hours
            first = rec.start_datetime.astimezone(tz)
            second = datetime.now().astimezone(tz)
            event_date = rec.start_date
            today_date = date.today()
            if (second - first).total_seconds() > NUMBER_OF_SECONDS or event_date != today_date:
                return False
            else:
                return True




    # def action_send_whatsapp_remainder_appointments(self):
    #     token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
    #     instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
    #     calendar_whts_available = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.appointment_whts_available')
    #     conn_calendar_msg = http.client.HTTPSConnection("api.ultramsg.com")
    #     headers = {'content-type': "application/x-www-form-urlencoded"}
    #     if calendar_whts_available:
    #         for rec in self:
    #             attendencies = []
    #             for att in rec.event_id.attendee_ids:
    #                 if att.common_name != rec.common_name:
    #                     attendencies.append("\n" + "-" + att.common_name+ ("," if att.partner_id.mobile else "")  + str(att.partner_id.mobile or ''))
    #                 else:
    #                     attendencies.insert(0, "-" + "You")
    #             for partner in rec:
    #                 tz = pytz.timezone(partner.env.user.tz)
    #                 day = partner.start_date and (datetime.strptime(str(partner.start_date), '%Y-%m-%d').date()).strftime( '%A') or ''
    #                 NUMBER_OF_SECONDS = 86400  # seconds in 24 hours
    #                 first = partner.start_datetime.astimezone(tz)
    #                 second = datetime.now().astimezone(tz)
    #                 event_date=partner.start_date
    #                 today_date=date.today()
    #                 if (second - first).total_seconds() > NUMBER_OF_SECONDS or event_date!=today_date:
    #                     custom_message = "Dear *{}*,\nThis is to remaind  you that you have meeting on {} {} at {}.\nSubject:{}\nLocation:{}\nAttendees:\n {}".format(
    #                         str(partner.common_name), str(day), str(partner.start_date), str(partner.start_time),
    #                         str(rec.event_id.name), str(rec.event_id.location if rec.event_id.location else ''),
    #                         str(''.join(attendencies)))
    #                 else:
    #                     custom_message = "Dear *{}*,\nThis is to remaind  you that you have meeting  today at {}.\nSubject:{}\nLocation:{}\nAttendees:\n {}".format(
    #                         str(partner.common_name), str(partner.start_time),
    #                         str(rec.event_id.name), str(rec.event_id.location if rec.event_id.location else ''),
    #                         str(''.join(attendencies)))
    #                 #print("custom_message", custom_message)
    #                 if partner.partner_id.mobile:
    #                     partner_mobile = partner.partner_id.phone_format(partner.partner_id.mobile)
    #                     payload_calendar_msg = f"token={token}&to={partner_mobile}&body={custom_message}&priority=10&referenceId=".format(token=token, number=partner_mobile, message_body=custom_message)
    #                     pst_url_calendar_msg = "/{instance_id}/messages/chat".format(instance_id=instance_id)
    #                     conn_calendar_msg.request("POST", pst_url_calendar_msg, payload_calendar_msg, headers)
    #                     res_inv_msg = conn_calendar_msg.getresponse()
    #                     data_doc = res_inv_msg.read()
    #                     msg_sent_status = data_doc.decode("utf-8")
    #                     result_dict = eval(msg_sent_status)
    #                     if result_dict.get('sent') == 'true':
    #                         time.sleep(2)
    #                         msg_id = int(result_dict.get('id'))
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
    #                         # time.sleep(2)
    #                         response = requests.request("GET", msg_status_url, headers=headers, params=querystring)
    #                         res = json.loads(response.text)
    #                         if res.get('messages')[0].get('status') == 'invalid':
    #                             msg = (_('Failure reason:Whatsapp Message not send.Check mobile %s or check with integration api provider.') % partner_mobile)
    #                             rec.event_id.message_post(body="Whatsapp message to :" + partner.common_name + "<br/>" + res.get('messages')[0].get('status') + "<br/>" + msg + "<br/>" + custom_message)
    #                         elif res.get('messages')[0].get('status') == 'queue':
    #                             rec.event_id.message_post(body="Whatsapp message to :" + partner.common_name + "<br/>" + res.get('messages')[0].get('status') + "<br/>" + custom_message)
    #                         else:
    #                             rec.event_id.message_post(body="Whatsapp message to :" + "<br/>" + partner.common_name + "<br/>" +res.get('messages')[0].get('status') + "<br/>" + custom_message)
    #                     if result_dict.get('error'):
    #                         rec.event_id.message_post(body="Whatsapp message to :" + "<br/>" + partner.common_name + "<br/>" + str(result_dict.get('error')))


    def action_send_whatsapp_appointments(self):
        token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
        instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
        calendar_whts_available = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.appointment_whts_available')
        conn_calendar_msg = http.client.HTTPSConnection("api.ultramsg.com")
        headers = {'content-type': "application/x-www-form-urlencoded"}
        if calendar_whts_available:
            for rec in self:
                if calendar_whts_available:
                    for partner in rec:
                        appointment_message_template_message = (partner.partner_id.company_id.appointment_message_template_message)
                        custom_message = str(self.env['mail.template']._render_template((appointment_message_template_message),'calendar.attendee', partner.id) or '')
                        custom_message = str(tools.html2plaintext(custom_message))
                        if partner.partner_id.mobile:
                            partner_mobile = partner.partner_id.phone_format(partner.partner_id.mobile)
                            payload_calendar_msg = f"token={token}&to={partner_mobile}&body={str(urllib.parse.quote(custom_message))}&priority=10&referenceId=".format(token=token, number=partner_mobile, message_body=custom_message)
                            payload_calendar_msg = payload_calendar_msg.encode('utf8').decode('iso-8859-1')
                            pst_url_calendar_msg = "/{instance_id}/messages/chat".format(instance_id=instance_id)
                            conn_calendar_msg.request("POST", pst_url_calendar_msg, payload_calendar_msg, headers)
                            res_inv_msg = conn_calendar_msg.getresponse()
                            data_doc = res_inv_msg.read()
                            msg_sent_status = data_doc.decode("utf-8")
                            result_dict = eval(msg_sent_status)
                            if result_dict.get('sent') == 'true':
                                time.sleep(2)
                                msg_id = int(result_dict.get('id'))
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
                                # time.sleep(2)
                                response = requests.request("GET", msg_status_url, headers=headers, params=querystring)
                                res = json.loads(response.text)
                                if res.get('messages')[0].get('status') == 'invalid':
                                    msg = (_('Failure reason:Whatsapp Message not send.Check mobile %s or check with integration api provider.') % partner_mobile)
                                    # rec.event_id.message_post(body="Whatsapp message to :" + partner.common_name + "<br/>" +res.get('messages')[0].get('status') + "<br/>" + msg + "<br/>" + custom_message)
                                    rec.event_id.message_post(body="Whatsapp message to: " + str(partner.common_name or '') + "<br/>" + "Mobile:" + str(partner_mobile or '') + "<br/>" + str(res.get('messages')[0].get('status') or '') +"<br/>"+ str(msg or ''))
                                elif res.get('messages')[0].get('status') == 'queue':
                                    rec.event_id.message_post(body="Whatsapp message to: " + str(partner.common_name or '') + "<br/>" + "Mobile:" + str(partner_mobile or '') + "<br/>" + str(res.get('messages')[0].get('status') or '') + "<br/>" + str(custom_message or ''))
                                else:
                                    rec.event_id.message_post(body="Whatsapp message to: " + str(partner.common_name or '') + "<br/>" + "Mobile:" + str(partner_mobile or '') + "<br/>" + str(res.get('messages')[0].get('status') or '') + "<br/>" + str(custom_message or ''))
                            if result_dict.get('error'):
                                #rec.event_id.message_post(body="Whatsapp message to :" + "<br/>" + partner.common_name + "<br/>" + str(result_dict.get('error')))
                                rec.event_id.message_post(body="Whatsapp message to: " + str(partner.common_name or '') + "<br/>" + "Mobile:" + str(partner_mobile or '') + "<br/>" + str(str(result_dict.get('error'))) + "<br/>" + str(custom_message or ''))
                        else:
                            rec.event_id.message_post(body="Whatsapp message to: " + str( partner.common_name or '') + "<br/>"+"Mobile Number does not exist")

    def action_send_whatsapp_remainder_appointments(self):
        token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
        instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
        calendar_whts_available = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.appointment_whts_available')
        conn_calendar_msg = http.client.HTTPSConnection("api.ultramsg.com")
        headers = {'content-type': "application/x-www-form-urlencoded"}
        if calendar_whts_available:
            for rec in self:
                for partner in rec:
                    appointment_remainder_template_message = (partner.partner_id.company_id.appointment_remainder_template_message)
                    custom_message = str(self.env['mail.template']._render_template((appointment_remainder_template_message),   'calendar.attendee', partner.id) or '')
                    custom_message = str(tools.html2plaintext(custom_message))
                    if partner.partner_id.mobile:
                        partner_mobile = partner.partner_id.phone_format(partner.partner_id.mobile)
                        payload_calendar_msg = f"token={token}&to={partner_mobile}&body={str(urllib.parse.quote(custom_message))}&priority=10&referenceId=".format(token=token, number=partner_mobile, message_body=custom_message)
                        payload_calendar_msg = payload_calendar_msg.encode('utf8').decode('iso-8859-1')
                        pst_url_calendar_msg = "/{instance_id}/messages/chat".format(instance_id=instance_id)
                        conn_calendar_msg.request("POST", pst_url_calendar_msg, payload_calendar_msg, headers)
                        res_inv_msg = conn_calendar_msg.getresponse()
                        data_doc = res_inv_msg.read()
                        msg_sent_status = data_doc.decode("utf-8")
                        result_dict = eval(msg_sent_status)
                        if result_dict.get('sent') == 'true':
                            time.sleep(2)
                            msg_id = int(result_dict.get('id'))
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
                            # time.sleep(2)
                            response = requests.request("GET", msg_status_url, headers=headers, params=querystring)
                            res = json.loads(response.text)
                            if res.get('messages')[0].get('status') == 'invalid':
                                msg = (_('Failure reason:Whatsapp Message not send.Check mobile %s or check with integration api provider.') % partner_mobile)
                                rec.event_id.message_post(body="Whatsapp message to: " + str(partner.common_name or '') + "<br/>" + "Mobile:" + str(partner_mobile or '') + "<br/>" + str(res.get('messages')[0].get('status') or '') + "<br/>" + str(msg or ''))
                            elif res.get('messages')[0].get('status') == 'queue':
                                rec.event_id.message_post(body="Whatsapp message to: " + str(partner.common_name or '') + "<br/>" + "Mobile:" + str(partner_mobile or '') + "<br/>" + str(res.get('messages')[0].get('status') or '') + "<br/>" + str(custom_message or ''))
                            else:
                                rec.event_id.message_post(body="Whatsapp message to: " + str(partner.common_name or '') + "<br/>" + "Mobile:" + str(partner_mobile or '') + "<br/>" + str(res.get('messages')[0].get('status') or '') + "<br/>" + str(custom_message or ''))
                        if result_dict.get('error'):
                            rec.event_id.message_post(body="Whatsapp message to: " + str(partner.common_name or '') + "<br/>" + "Mobile:" + str(partner_mobile or '') + "<br/>" + str(str(result_dict.get('error'))) + "<br/>" + str(custom_message or ''))
                            #rec.event_id.message_post(body="Whatsapp message to :" + "<br/>" + partner.common_name + "<br/>" + str(result_dict.get('error')))
                    else:
                        rec.event_id.message_post(body="Whatsapp message to: " + str(partner.common_name or '') + "<br/>" + "Mobile Number does not exist")


class AlarmManager(models.AbstractModel):
    _inherit = 'calendar.alarm_manager'

    @api.model
    def get_next_whatsapp(self):
        now = fields.Datetime.to_string(fields.Datetime.now())
        last_notif_whatsapp = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.last_notif_whatsapp', default=now)
        try:
            cron = self.env['ir.model.data'].sudo().get_object('calendar', 'ir_cron_scheduler_alarm')
        except ValueError:
            _logger.error("Cron for " + self._name + " can not be identified !")
            return False

        interval_to_second = {
            "weeks": 7 * 24 * 60 * 60,
            "days": 24 * 60 * 60,
            "hours": 60 * 60,
            "minutes": 60,
            "seconds": 1
        }

        if cron.interval_type not in interval_to_second:
            _logger.error("Cron delay can not be computed !")
            return False
        cron_interval = cron.interval_number * interval_to_second[cron.interval_type]
        all_meetings = self.get_next_potential_limit_alarm('whatsapp', seconds=cron_interval)
        for meeting in self.env['calendar.event'].browse(all_meetings):
            max_delta = all_meetings[meeting.id]['max_duration']
            if meeting.recurrency:
                at_least_one = False
                last_found = False
                for one_date in meeting._get_recurrent_date_by_event():
                    in_date_format = one_date.replace(tzinfo=None)
                    last_found = self.do_check_alarm_for_one_date(in_date_format, meeting, max_delta, 0, 'whatsapp', after=last_notif_whatsapp, missing=True)
                    for alert in last_found:
                        self.do_whatsapp_reminder(alert)
                        at_least_one = True  # if it's the first alarm for this recurrent event
                    if at_least_one and not last_found:  # if the precedent event had an alarm but not this one, we can stop the search for this event
                        break
            else:
                in_date_format = meeting.start
                last_found = self.do_check_alarm_for_one_date(in_date_format, meeting, max_delta, 0, 'whatsapp',after=last_notif_whatsapp, missing=True)
                for alert in last_found:
                    self.do_whatsapp_reminder(alert)
        self.env['ir.config_parameter'].sudo().set_param('mast_odoo_whatsapp_integration.last_notif_whatsapp', now)

    def do_whatsapp_reminder(self, alert):
        meeting = self.env['calendar.event'].browse(alert['event_id'])
        alarm = self.env['calendar.alarm'].browse(alert['alarm_id'])
        result = False
        if alarm.type == 'whatsapp' and meeting.state=='open':
            participants = meeting.attendee_ids.filtered(lambda r: r.state != 'declined')
            for att in participants:
                result = att.action_send_whatsapp_remainder_appointments()
        return result
