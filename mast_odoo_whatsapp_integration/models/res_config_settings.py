# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import ast

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsa_auth_token = fields.Char(string="Token")
    instance_id = fields.Char(string='Instance Id')

    #Quotation
    qt_whts_available=fields.Boolean(string="Available")
    qt_whts_flwup = fields.Boolean(string="Follow Up")
    #qt_whts_lang = fields.Selection([('arabic', 'Arabic'),('english', 'English'),('both', 'Both')],default='english',string='Language',)
    qt_whts_every = fields.Integer(string='Every',default=1)
    qt_whts_interval_type = fields.Selection([('days', 'Days'),('weeks', 'Weeks'),('months', 'Months')], string='Interval Unit', default='months')
    qt_whts_send_type = fields.Selection([('manual', 'Manual')],default='manual',string='Send')

    qt_whts_msg = fields.Text(string="Message")
    qt_flwp_msg = fields.Text(string="Message")
    qt_message_template_message=fields.Text(related='company_id.qt_message_template_message',string="Quotation Message",readonly=False)

    #Oreders
    order_whts_available = fields.Boolean(string="Available")
    order_whts_flwup = fields.Boolean(string="Follow Up")
    order_whts_every = fields.Integer(string='Every',default=1)
    order_whts_interval_type = fields.Selection([('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')],string='Interval Unit', default='months')
    order_whts_send_type = fields.Selection([('manual', 'Manual'),('auto', 'Automate')], default='manual', string='Send')
    order_message_template_message=fields.Text(related='company_id.order_message_template_message',string="Sale Order Message",readonly=False)
    order_whts_msg = fields.Text(string="Message")
    order_flwp_msg = fields.Text(string="Message")

    #Invoice
    inv_whts_available = fields.Boolean(string="Available")
    inv_whts_flwup = fields.Boolean(string="Follow Up")
    inv_whts_msg = fields.Text(string="Message")
    inv_whts_send_type = fields.Selection([('manual', 'Manual'),('auto', 'Automate')], default='manual', string='Send',)
    inv_template_id=fields.Many2one('ir.actions.report',domain=[('model','=','account.invoice')],string="Document Template")
    invoice_message_template_message=fields.Text(related='company_id.invoice_message_template_message',string="Invoice Message",readonly=False)


    #Payments
    payments_whts_available = fields.Boolean(string="Available")
    payments_whts_send_type = fields.Selection([('manual', 'Manual'),('auto', 'Automate')], default='manual', string='Send',)
    payment_template_id=fields.Many2one('ir.actions.report',domain=[('model','=','account.payment')],string="Document Template")
    payment_whts_msg = fields.Text(string="Message")
    payment_message_template_message=fields.Text(related='company_id.payment_message_template_message',string="Payment Message",readonly=False)

    #Delivery Note
    do_whts_available = fields.Boolean(string="Available")
    do_whts_send_type = fields.Selection([('manual', 'Manual'),('auto', 'Automate')], default='manual', string='Send',)
    do_template_id=fields.Many2one('ir.actions.report',domain=[('model','=','stock.picking')],string="Document Template")
    do_whts_msg = fields.Text(string="Message")
    delivery_message_template_message=fields.Text(related='company_id.delivery_message_template_message',string="Do Message",readonly=False)

    #Calender&Appointments
    appointment_whts_available = fields.Boolean(string="Available")
    appointment_whts_send_type = fields.Selection([('manual', 'Manual'),('auto', 'Automate')], default='manual', string='Send',)
    appointment_message_template_message=fields.Text(string="Appointment Message",related='company_id.appointment_message_template_message',readonly=False)
    appointment_remainder_template_message=fields.Text(string="Appointment Remainder Message",related='company_id.appointment_remainder_template_message',readonly=False)

    #Customer Followup
    customer_flwup_whts_available = fields.Boolean(string="Available")
    customer_flwup_whts_send_type = fields.Selection([('manual', 'Manual'),('auto', 'Automate')], default='manual', string='Send',)
    remainder_days=fields.Integer(string="Remaind")
    statement_whts_interval_type = fields.Selection([('minutes', 'Minutes'),('hours', 'Hours'),('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')],string='Interval Unit', default='months')
    statment_whts_flwup = fields.Boolean(string="Statement Follow Up Auto",compute='_compute_statement_followup')
    statement_whts_msg = fields.Text(string="Message")
    statement_whts_overdue_msg = fields.Text(string="OverDue Message",related='company_id.overdue_msg',readonly=False)

    # Helpdesk
    help_desk_whts_available = fields.Boolean(related='company_id.help_desk_whts_available',string="Available",readonly=False)
    help_desk_whts_send_type = fields.Selection(related='company_id.help_desk_whts_send_type',readonly=False)
    helpdesk_stage_ids=fields.Many2many(related='company_id.helpdesk_stage_ids',string="Stages",readonly=False)
    helpdesk_team_ids=fields.Many2many(related='company_id.helpdesk_team_ids',string="Teams",readonly=False)

    @api.onchange("helpdesk_team_ids")
    def _onchange_helpdesk_team_ids(self):
        data = self.env['helpdesk.stage'].search([('team_ids', 'in', self.helpdesk_team_ids.ids)])
        ids = list(data.ids)
        stage_ids=self.helpdesk_stage_ids.ids
        for stage in stage_ids:
            if stage not in ids:
                self.helpdesk_stage_ids=[(2, stage)]







    @api.onchange('customer_flwup_whts_send_type')
    def _compute_statement_followup(self):
        if self.customer_flwup_whts_send_type=='auto':
            self.statment_whts_flwup=True
        else:
            self.statment_whts_flwup = False





        
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()

        #Quotations
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('mast_odoo_whatsapp_integration.whatsa_auth_token', self.whatsa_auth_token)
        set_param('mast_odoo_whatsapp_integration.instance_id', self.instance_id)
        set_param('mast_odoo_whatsapp_integration.qt_whts_available', self.qt_whts_available)
        set_param('mast_odoo_whatsapp_integration.qt_whts_flwup', self.qt_whts_flwup)
        set_param('mast_odoo_whatsapp_integration.qt_whts_every', self.qt_whts_every)
        set_param('mast_odoo_whatsapp_integration.qt_whts_interval_type', self.qt_whts_interval_type)
        set_param('mast_odoo_whatsapp_integration.qt_whts_send_type', self.qt_whts_send_type)
        set_param('mast_odoo_whatsapp_integration.qt_whts_msg', self.qt_whts_msg)
        set_param('mast_odoo_whatsapp_integration.qt_flwp_msg', self.qt_flwp_msg)

        #Orders
        set_param('mast_odoo_whatsapp_integration.order_whts_available', self.order_whts_available)
        set_param('mast_odoo_whatsapp_integration.order_whts_flwup', self.order_whts_flwup)
        set_param('mast_odoo_whatsapp_integration.order_whts_every', self.order_whts_every)
        set_param('mast_odoo_whatsapp_integration.order_whts_interval_type', self.order_whts_interval_type)
        set_param('mast_odoo_whatsapp_integration.order_whts_send_type', self.order_whts_send_type)
        set_param('mast_odoo_whatsapp_integration.order_whts_msg', self.order_whts_msg)
        set_param('mast_odoo_whatsapp_integration.order_flwp_msg', self.order_flwp_msg)
        ir_cron_order_followup = self.env.ref('mast_odoo_whatsapp_integration.ir_cron_order_followup', False)
        ir_cron_order_followup.write({
            'interval_number': self.order_whts_every,
            'interval_type': self.order_whts_interval_type,
            'active': self.order_whts_flwup,
        })
        ir_cron_quotation_followup = self.env.ref('mast_odoo_whatsapp_integration.ir_cron_quotation_followup', False)
        ir_cron_quotation_followup.write({
            'interval_number': self.qt_whts_every,
            'interval_type': self.qt_whts_interval_type,
            'active':self.qt_whts_flwup,
        })

        #Invoices
        set_param('mast_odoo_whatsapp_integration.inv_whts_available', self.inv_whts_available)
        set_param('mast_odoo_whatsapp_integration.inv_whts_msg', self.inv_whts_msg)
        set_param('mast_odoo_whatsapp_integration.inv_whts_send_type', self.inv_whts_send_type)
        set_param('mast_odoo_whatsapp_integration.inv_template_id', self.inv_template_id.id)

        #Payments
        set_param('mast_odoo_whatsapp_integration.payments_whts_available', self.payments_whts_available)
        set_param('mast_odoo_whatsapp_integration.payments_whts_send_type', self.payments_whts_send_type)
        set_param('mast_odoo_whatsapp_integration.payment_whts_msg', self.payment_whts_msg)
        set_param('mast_odoo_whatsapp_integration.payment_template_id', self.payment_template_id.id)


        #Delivery Note
        set_param('mast_odoo_whatsapp_integration.do_whts_available', self.do_whts_available)
        set_param('mast_odoo_whatsapp_integration.do_whts_send_type', self.do_whts_send_type)
        set_param('mast_odoo_whatsapp_integration.do_template_id', self.do_template_id.id)
        set_param('mast_odoo_whatsapp_integration.do_whts_msg', self.do_whts_msg)


        #Appointments
        set_param('mast_odoo_whatsapp_integration.appointment_whts_available', self.appointment_whts_available)
        set_param('mast_odoo_whatsapp_integration.appointment_whts_send_type', self.appointment_whts_send_type)

        # Customer Followup
        set_param('mast_odoo_whatsapp_integration.customer_flwup_whts_available', self.customer_flwup_whts_available)
        set_param('mast_odoo_whatsapp_integration.customer_flwup_whts_send_type', self.customer_flwup_whts_send_type)
        set_param('mast_odoo_whatsapp_integration.remainder_days', self.remainder_days)
        set_param('mast_odoo_whatsapp_integration.statement_whts_interval_type', self.statement_whts_interval_type)
        set_param('mast_odoo_whatsapp_integration.statment_whts_flwup', self.statment_whts_flwup)
        ir_cron_statement_followup = self.env.ref('mast_odoo_whatsapp_integration.ir_cron_customerstatement_followup', False)
        ir_cron_statement_followup.write({
            'interval_number': self.remainder_days,
            'interval_type': self.statement_whts_interval_type,
            'active': self.statment_whts_flwup,
        })
        set_param('mast_odoo_whatsapp_integration.statement_whts_msg', self.statement_whts_msg)




    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param

        #Quotations
        res['whatsa_auth_token'] = get_param('mast_odoo_whatsapp_integration.whatsa_auth_token')
        res['instance_id'] = get_param('mast_odoo_whatsapp_integration.instance_id')
        res['qt_whts_available'] = get_param('mast_odoo_whatsapp_integration.qt_whts_available')
        res['qt_whts_flwup'] = get_param('mast_odoo_whatsapp_integration.qt_whts_flwup')
        res['qt_whts_every'] = int(get_param('mast_odoo_whatsapp_integration.qt_whts_every'))
        res['qt_whts_interval_type'] = get_param('mast_odoo_whatsapp_integration.qt_whts_interval_type')
        res['qt_whts_send_type'] = get_param('mast_odoo_whatsapp_integration.qt_whts_send_type')
        res['qt_whts_msg'] = get_param('mast_odoo_whatsapp_integration.qt_whts_msg')
        res['qt_flwp_msg'] = get_param('mast_odoo_whatsapp_integration.qt_flwp_msg')


        #Orders
        res['order_whts_available'] = get_param('mast_odoo_whatsapp_integration.order_whts_available')
        res['order_whts_flwup'] = get_param('mast_odoo_whatsapp_integration.order_whts_flwup')
        res['order_whts_every'] = int(get_param('mast_odoo_whatsapp_integration.order_whts_every'))
        res['order_whts_interval_type'] = get_param('mast_odoo_whatsapp_integration.order_whts_interval_type')
        res['order_whts_send_type'] = get_param('mast_odoo_whatsapp_integration.order_whts_send_type')
        res['order_whts_msg'] = get_param('mast_odoo_whatsapp_integration.order_whts_msg')
        res['order_flwp_msg'] = get_param('mast_odoo_whatsapp_integration.order_flwp_msg')


        #Invoices
        res['inv_whts_available'] = get_param('mast_odoo_whatsapp_integration.inv_whts_available')
        res['inv_whts_msg'] = get_param('mast_odoo_whatsapp_integration.inv_whts_msg')
        res['inv_whts_send_type'] = get_param('mast_odoo_whatsapp_integration.inv_whts_send_type')
        invoice_template_id= get_param('mast_odoo_whatsapp_integration.inv_template_id')
        res.update(
            inv_template_id=int(invoice_template_id),
        )
        #Payments
        res['payments_whts_available'] = get_param('mast_odoo_whatsapp_integration.payments_whts_available')
        res['payments_whts_send_type'] = get_param('mast_odoo_whatsapp_integration.payments_whts_send_type')
        res['payment_whts_msg'] = get_param('mast_odoo_whatsapp_integration.payment_whts_msg')
        payment_template_id= get_param('mast_odoo_whatsapp_integration.payment_template_id')
        res.update(
            payment_template_id=int(payment_template_id),
        )
        #Delivery Note
        res['do_whts_available'] = get_param('mast_odoo_whatsapp_integration.do_whts_available')
        res['do_whts_send_type'] = get_param('mast_odoo_whatsapp_integration.do_whts_send_type')
        res['do_whts_msg'] = get_param('mast_odoo_whatsapp_integration.do_whts_msg')
        do_template_id= get_param('mast_odoo_whatsapp_integration.do_template_id')
        res.update(
            do_template_id=int(do_template_id),
        )


        #Calender&Appointments
        res['appointment_whts_available'] = get_param('mast_odoo_whatsapp_integration.appointment_whts_available')
        res['appointment_whts_send_type'] = get_param('mast_odoo_whatsapp_integration.appointment_whts_send_type')

        # Customer Followup
        res['customer_flwup_whts_available'] = get_param('mast_odoo_whatsapp_integration.customer_flwup_whts_available')
        res['customer_flwup_whts_send_type'] = get_param('mast_odoo_whatsapp_integration.customer_flwup_whts_send_type')
        res.update(
            remainder_days=int(get_param('mast_odoo_whatsapp_integration.remainder_days',)),
            statement_whts_interval_type=(get_param('mast_odoo_whatsapp_integration.statement_whts_interval_type')),
        )
        res['statment_whts_flwup'] = get_param('mast_odoo_whatsapp_integration.statment_whts_flwup')
        res['statement_whts_msg'] = get_param('mast_odoo_whatsapp_integration.statement_whts_msg')


        return res