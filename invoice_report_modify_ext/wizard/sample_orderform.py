# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import re

from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.tools import pycompat
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

class MailComposer(models.TransientModel):
    _name = 'sample.order.form.wizard'
    _description = 'Sample Order Form  wizard'
    
    def _defaul_domain_values(self):
        #print("context",self._context)
        p1 = self.env.context.get('active_id')
        #p1 = self.env.context.get('default_insur_company_id')
        insur_comp = []
        if p1:
            order = self.env['insurance.policy'].browse(p1)
            for line in order.order_line:
                if line.insur_company_id.id not in insur_comp:
                    insur_comp.append(line.insur_company_id.id)
        return [('id', 'in', insur_comp)]
    
    def _default_value2(self):
        print("kkklll")
        p1 = self.env.context.get('active_id')
        #p1 = self.env.context.get('default_insur_company_id')
        insur_comp = []
        if p1:
            order = self.env['insurance.policy'].browse(p1)
            for line in order.order_line:
                if line.insur_company_id.id not in insur_comp:
                    insur_comp.append(line.insur_company_id.id)
        print("insur_comp",insur_comp)
        if insur_comp:
            if len(insur_comp) == 1:
                return insur_comp[0]
                    
        
    insur_company_id = fields.Many2one('res.partner', string='Insurance Company', default=_default_value2, domain=_defaul_domain_values, required=True)
    policy_order_id = fields.Integer(string="Order")
    policy_order_name = fields.Char(string="Policy name")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('sample.order.form.wizard'))
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, track_visibility='onchange', track_sequence=2, default=lambda self: self.env.user)
    
    
    
    @api.multi
    def print_sample_orderform(self, data):
        p1 = self.env.context.get('default_insur_company_id')
        p2 = self.env.context.get('default_policy_order_id')
        print("print_sample_orderform",p1,p2)
        data=[]
        #data = self.pre_print_report(data)
        #data['order_id'] = self.env.context.get('active_ids', [])
        #data['order_id'] = self.policy_order_id
        #data['form'].update({'order_id': p2})
        #print("dddd",data['order_id'])
        return self.env.ref('invoice_report_modify_ext.action_report_insurance_orderform').report_action(self, data=data)
    
    def get_policy_obj(self):
        p2 = self.policy_order_id
        policy = self.env['insurance.policy'].browse(p2)
        print("policy",p2,p2)
        flag = False
        for line in policy.order_line:
            if line.insur_company_id:
                flag = True
        if flag:
            return policy
        else:
            raise UserError(_('Policy order %s must contains insurance company') % (policy.name,))
    
    def action_orderform_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('invoice_report_modify_ext', 'email_template_edi_policy_orderform')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        lang = self.env.context.get('lang')
        template = template_id and self.env['mail.template'].browse(template_id)
        if template and template.lang:
            lang = template._render_template(template.lang, 'sample.order.form.wizard', self.ids[0])
        ctx = {
            'default_model': 'sample.order.form.wizard',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }  
        
    @api.multi
    def get_base_url(self):
        """When using multi-website, we want the user to be redirected to the
        most appropriate website if possible."""
        #res = super(SaleOrder, self).get_base_url()
        return []