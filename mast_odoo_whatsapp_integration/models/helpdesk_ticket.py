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
from odoo import tools
from odoo.tools.safe_eval import safe_eval
import unicodedata
import html
import html2text
import xml.etree.ElementTree as ET

_logger = logging.getLogger(__name__)


class HelpDesk(models.Model):
    _inherit = 'helpdesk.ticket'

    is_visible_whatsapp = fields.Boolean(string="Is Visible Whastapp", compute="_compute_whatsapp_helpdesk_visibility")
    is_stage_whatsapp_visible=fields.Boolean(string="Is Stage Whastapp Visible", compute="_compute_whatsapp_helpdesk_visibility")

    @api.depends('name','team_id','partner_id')
    def _compute_whatsapp_helpdesk_visibility(self):
        for rec in self:
            if rec.company_id:
                company_id=rec.company_id
            if rec.partner_id:
                company_id = rec.partner_id.company_id
            if rec.team_id:
                company_id = rec.team_id.company_id
            else:
                company_id=rec.env.user.company_id
            rec.is_visible_whatsapp = company_id.help_desk_whts_available
            if rec.stage_id.id  in company_id.helpdesk_stage_ids.ids and rec.team_id.id  in company_id.helpdesk_team_ids.ids :
                rec.is_stage_whatsapp_visible = True
            else:
                rec.is_stage_whatsapp_visible = False


    def action_whatsapp_ticket(self):
        for rec in self:
            custom_msg = rec.stage_id.whatsapp_template_id._render_template(rec.stage_id.whatsapp_template_id.body_html,'helpdesk.ticket', rec.id)  or ''
            if not  rec.stage_id.whatsapp_template_id:
                rec.message_post(body="Set whatsapp message template for stage-"+str(rec.stage_id.name or '')+"   of helpdesk team "+str(rec.team_id.name or ''))
            if custom_msg:
                custom_msg=str(tools.html2plaintext(custom_msg))
            to=rec.partner_id.mobile
            partner_id=rec.partner_id
            bodies = self.env['mail.template']._render_template(rec.stage_id.whatsapp_template_id.body_html, 'helpdesk.ticket', rec.id, post_process=True)
            custom_msg=html2text.html2text(bodies)
            if to:
                to=rec.partner_id.phone_format(rec.partner_id.mobile)
            rec.send_helpdesk_whatsapp(custom_msg,partner_id,to)


    def send_helpdesk_whatsapp(self,custom_msg,partner_id,to):
        custom_msg=(tools.html2plaintext(custom_msg))
        token = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
        instance_id = self.env['ir.config_parameter'].sudo().get_param('mast_odoo_whatsapp_integration.instance_id')
        for rec in self:
            help_desk_whts_available =rec.company_id.help_desk_whts_available
            if help_desk_whts_available:
                if to:
                    payload = f"token={token}&to={to}&body={str(urllib.parse.quote(custom_msg))}&priority=10&referenceId=".format(token=token, number=to, message_body=custom_msg)
                    payload = payload.encode('utf8').decode('iso-8859-1')
                    pst_url = "/{instance_id}/messages/chat".format(instance_id=instance_id)
                    conn = http.client.HTTPSConnection("api.ultramsg.com")
                    headers = {'content-type': "application/x-www-form-urlencoded"}
                    conn.request("POST", pst_url, payload, headers)
                    res = conn.getresponse()
                    data = res.read()
                    msg_sent_status = data.decode("utf-8")
                    final_dictionary = eval(msg_sent_status)
                    if final_dictionary.get('error'):
                        rec.message_post(body="Whatsapp message to: " + str(partner_id.name) + "<br/>" + "Mobile:" + str(to or '') + "<br/>" + "Status:" + str(final_dictionary.get('error') or '') + "<br/>" + "Message:" + str(custom_msg or ''))
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
                        res = json.loads(response.text)
                        if res.get('messages')[0].get('status') == 'invalid':
                            msg = (_('Failure reason:Whatsapp Message not send.Check mobile  %s or check with integration api provider.') % to)
                            rec.message_post(body="Whatsapp message to: " + str(partner_id.name or partner_id.parent_id.name or '') + "<br/>" + "Mobile:" + str( to or '') + "<br/>" + str(res.get('messages')[0].get('status') or '') + "<br/>" + str(msg or ''))
                        elif res.get('messages')[0].get('status') == 'queue':
                            rec.message_post(body="Whatsapp message to: " + str(partner_id.name or partner_id.parent_id.name or '') + "<br/>" + "Mobile:" + str( to or '') + "<br/>" + str(res.get('messages')[0].get('status') or '') + "<br/>" + str(custom_msg or ''))
                        else:
                            rec.message_post(body="Whatsapp message to: " + str( partner_id.name or partner_id.parent_id.name or '') + "<br/>" + "Mobile:" + str(to or '') + "<br/>" + str(res.get('messages')[0].get('status') or '') + "<br/>" + str(custom_msg or ''))
                if not partner_id:
                    rec.message_post(body="Whatsapp to:" + str(partner_id.name or '') + "<br/>" + "Customer does not exist!!!")
                else:
                    if not to:
                        rec.message_post(body="Whatsapp to:" + str(partner_id.name or '') + "<br/>" + "Mobile number does not exist!!!")

    @api.multi
    def write(self, vals):
        res = super(HelpDesk, self).write(vals)
        if vals.get('stage_id'):
            stage=self.env['helpdesk.stage'].browse(vals.get('stage_id'))
            if stage.id in self.company_id.helpdesk_stage_ids.ids and stage.help_desk_whts_send_type == 'auto':
                if self.team_id:
                    if self.team_id in self.company_id.helpdesk_team_ids:
                        help_desk_whts_available = self.company_id.help_desk_whts_available
                        help_desk_whts_send_type=self.company_id.help_desk_whts_send_type
                        if help_desk_whts_available and help_desk_whts_send_type == 'auto':
                            self.action_whatsapp_ticket()
        return res

    @api.model
    def create(self, vals):
        res = super(HelpDesk, self).create(vals)
        if vals.get('stage_id') or res.stage_id:
            stage=self.env['helpdesk.stage'].browse(vals.get('stage_id')) or res.stage_id
            team=self.env['helpdesk.team'].browse(vals.get('team_id'))
            if res.company_id:
                company_id = res.company_id
            elif team or res.team_id:
                company_id=team.company_id or res.team_id.company_id
            elif vals.get('partner_id', False) or res.partner_id:
                partner = self.env['res.partner'].browse(vals['partner_id']) or res.partner_id
                company_id=partner.company_id
            else:
                company_id= self.env.user.company_id
            if stage.id in company_id.helpdesk_stage_ids.ids and  res.team_id.id  in company_id.helpdesk_team_ids.ids and stage.help_desk_whts_send_type == 'auto':
                res.action_whatsapp_ticket()
        return res

    def action_whatsapp_ticket_contacts(self):
        for rec in self:
            contact_wizard=self.env['whatsapp.quotation.multiple.contact'].sudo().search([]).unlink()
            custom_msg = str(rec.stage_id.whatsapp_template_id._render_template(rec.stage_id.whatsapp_template_id.body_html,'helpdesk.ticket', rec.id)  or '')
            bodies = self.env['mail.template']._render_template(rec.stage_id.whatsapp_template_id.body_html, 'helpdesk.ticket', rec.id, post_process=True)
            msg=html2text.html2text(bodies)
            message_string = custom_msg.encode('UTF-8')
            message_body = message_string.decode('unicode-escape').encode('utf-8').decode('utf8')


            return {'type': 'ir.actions.act_window',
                    'name': _('Whatsapp to contacts'),
                    'res_model': 'whatsapp.quotation.multiple.contact',
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'context': {
                        'default_customer_id':rec.partner_id.id,
                        'default_message':(message_body),
                        'default_ticket_id': rec.id,
                        },
            }


    def onchange_template_id(self, template_id, model, res_id):
        if template_id:
            values = self.generate_email_for_composer(template_id, [res_id])[res_id]
        else:
            default_values = self.with_context(default_model=model, default_res_id=res_id).default_get(
                ['model', 'res_id', 'partner_ids', 'message'])
            values = dict((key, default_values[key]) for key in
                          ['body', 'partner_ids']
                          if key in default_values)
        #values = self._convert_to_write(values)
        return {'value': values}

    def generate_email_for_composer(self, template_id, res_ids, fields=None):
        multi_mode = True
        if isinstance(res_ids, int):
            multi_mode = False
            res_ids = [res_ids]
        if fields is None:
            fields = ['body_html']
        returned_fields = fields + ['partner_ids']
        values = dict.fromkeys(res_ids, False)
        template_values = self.env['mail.template'].with_context(tpl_partners_only=True).browse(
            template_id).generate_email(res_ids, fields=fields)
        for res_id in res_ids:
            res_id_values = dict((field, template_values[res_id][field]) for field in returned_fields if template_values[res_id].get(field))
            res_id_values['message'] = html2text.html2text(res_id_values.pop('body_html', ''))
            values[res_id] = res_id_values
        return multi_mode and values or values[res_ids[0]]


class HelpDeskStage(models.Model):
    _inherit = 'helpdesk.stage'

    whatsapp_template_id=fields.Many2one('mail.template',string="WhatsApp Message Template",   domain="[('model', '=', 'helpdesk.ticket')]",)
    help_desk_whts_send_type = fields.Selection([('manual', 'Manual'),('auto', 'Automate')], default='manual', string='Send',)

