# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
import ast

class ResCompany(models.Model):
    _inherit = 'res.company'
    qt_message_template_message = fields.Text(string='Quotation Message', translate=True,default=lambda s: _(
        '''Hello *${object.partner_id.name}*, 
your Quotation Number *${object.name}* with amount *${object.currency_id.symbol} ${object.amount_total}* is Ready. 
Your quotation date and time is:${object.usertimezone_order_date_time()}. 
If you have any questions, please feel free to contact us.
Please check the link below for more details:
${object.get_base_url()+object.get_portal_url()}
'''
    ))




    order_message_template_message = fields.Text(string='Sale Order Message', translate=True,default=lambda s: _(
        '''Hello *${object.partner_id.name}*, 
your Sale Order Number *${object.name}* with amount *${object.currency_id.symbol} ${object.amount_total}* is Confirmed. 
Your Sale Order date and time is:${object.user_confirmation_date_time()}. 
If you have any questions, please feel free to contact us.
Please check the link below for more details:
${object.get_base_url()+object.get_portal_url()}
'''))




    invoice_message_template_message = fields.Text(string='Invoice Message', translate=True,default=lambda s: _(
'''Hello *${object.partner_id.name}*, 
your Invoice *${object.number}* with amount *${object.currency_id.symbol} ${object.amount_total}* from ${object.company_id.name}. 
% if object.state not in['paid']:
Please remit payment at your earliest convenience. 
%elif object.state  in['cancel']:
This invoice is cancelled.
%else
This invoice is already paid.
%endif
If you have any questions, please feel free to contact us.'''
    ))



    payment_message_template_message = fields.Text(string='Payment Message', translate=True,default=lambda s: _(
        '''
Hello *${object.partner_id.name}*, 
Thank you for your payment.Here is your payment receipt *${object.name or ''}* amounting to *${object.currency_id.symbol} ${object.amount}* from ${object.company_id.name}. 
    
Do not hesitate to contact us if you have any question.
    '''
    ))





    delivery_message_template_message = fields.Text(string='DO Message', translate=True,default=lambda s: _(
'''Hello *${object.partner_id.name}*, 
Here is your order is shipped *${object.name}* from ${object.company_id.name}. 
    
Do not hesitate to contact us if you have any question.'''
    ))



    appointment_message_template_message =fields.Text(string='Appointment Message', translate=True,default=lambda s: _(
'''Dear *${object.common_name}*, 
This is to inform you that your meeting on  ${object.get_event_day()} ${object.start_date} at ${object.start_time} has been ${object.get_event_state()}.  
Subject:${object.get_event_name()}
Location:${object.event_id.location}
Attendees:
${object.get_attendencies()}

Best Regards,
Mast Team.'''
    ))



    appointment_remainder_template_message = fields.Text(string='Appointment Remainder Message', translate=True, default=lambda s: _(
'''
Dear *${object.common_name}*, 
% if object.get_remainder_hr()==True: 
This is to remaind  you that you have meeting on today at ${object.start_time}.                                  
%else
This is to remaind  you that you have meeting on                                                                                       ${object.get_event_day()} ${object.start_date} at ${object.start_time}.
%endif
Subject:${object.get_event_name()}
Location:${object.event_id.location}
Attendees:
${object.get_remainder_attendencies()}
'''
    ))


    help_desk_whts_available = fields.Boolean(string="Available")
    help_desk_whts_send_type = fields.Selection([('manual', 'Manual'),('auto', 'Automate')], default='manual', string='Send',)
    helpdesk_stage_ids=fields.Many2many('helpdesk.stage',string="Stages")
    helpdesk_team_ids=fields.Many2many('helpdesk.team',string="Teams")
