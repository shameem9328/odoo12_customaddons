# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from pytz import timezone, UTC
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
    
class InsurancePolicy(models.Model):
    _inherit = "insurance.policy"
    _description = "Insurance Policy"
    
    def get_vehicle_details(self):
        col_reg_no = ""
        col_make = ""
        col_model = ""
        col_cover = ""
        col_chassis = ""
        vehicle = []
        
        for line in self.order_line:
            if line.vehicle_id:
                if line.vehicle_id.id not in vehicle:
                    vehicle.append(line.vehicle_id.id)
                    col_reg_no += line.vehicle_id.license_plate + " "
                    col_make += line.vehicle_id.model_id.brand_id.name + " "
                    col_model += line.vehicle_id.model_id.name + " "
                    col_cover += line.vehicle_id.type_of_cover.name + " "
                    col_chassis += line.vehicle_id.chasis_no + " "
        return {'col_reg_no':col_reg_no,
                'col_make':col_make,
                'col_model':col_model,
                'col_cover':col_cover,
                'col_chassis':col_chassis,
                }
    def getDateOnly(self, date_time):
        date_only = date_time.date()
        date_only = datetime.strftime(date_only, "%Y-%m-%d")
        d = datetime.strptime(date_only, '%Y-%m-%d').strftime("%d %B %Y")
        return d

        #datetime.datetime.strptime(date_string, format1).strftime(format2)
    #####KPL######
    #sample orderform report#
    def get_vendor_cpr_or_cr_sample_orderform(self):
        print("get_vendor_cpr_or_cr_sample_orderform")
        cpr_cr = ""
        value =""
        if self.bank_id:
            if not self.bank_id.is_customer:
                if self.insured_person.company_type == 'company':
                    cpr_cr="CR"
                    value=self.insured_person.cr_no
                if self.insured_person.company_type == 'person':
                    cpr_cr="CPR"
                    value=self.insured_person.cpr_no
            else:
                cpr_cr="CR"
                value=self.bank_id.cr_no
        else:
            if self.insured_person.company_type == 'company':
                cpr_cr="CR"
                value=self.insured_person.cr_no
            if self.insured_person.company_type == 'person':
                cpr_cr="CPR"
                value=self.insured_person.cpr_no
        print("cpr",cpr_cr,value)
        return {'cpr_cr':cpr_cr,
                'value':value,
                }
    
    def get_vendor_insured_name_sample_orderform(self):
        insured_str = ''
        if self.bank_id:
            if self.bank_id.is_customer:
                insured_str = self.bank_id.name
            else:
                insured_str = self.insured_person.name+"-"+self.bank_id.name
        else:
            insured_str = self.insured_person.name
        return insured_str

    def get_vendor_insured_address_sample_orderform(self):
        insur_street = []
        insur_city =[]
        insur_country =[]
        insur_phone = []
        insur_email = []
        if self.bank_id:
            if self.bank_id.is_customer:
                if self.bank_id.street:
                    insur_street.append(self.bank_id.street)
                if self.bank_id.street2:
                    insur_street.append(self.bank_id.street2)
                if self.bank_id.city:
                    insur_city.append(self.bank_id.city)
                if self.bank_id.state:
                    insur_city.append(self.bank_id.state.name)
                if self.bank_id.zip:
                    insur_city.append(self.bank_id.zip)
                if self.bank_id.country:
                    insur_country.append(self.bank_id.country.name)
                if self.bank_id.phone:
                    insur_phone.append(self.bank_id.phone)
                if self.bank_id.email:
                    insur_email.append(self.bank_id.email)
            else:
                if self.insured_person.street:
                    insur_street.append(self.insured_person.street)
                if self.insured_person.street2:
                    insur_street.append(self.insured_person.street2)
                if self.insured_person.city:
                    insur_city.append(self.insured_person.city)
                if self.insured_person.state_id:
                    insur_city.append(self.insured_person.state_id.name)
                if self.insured_person.zip:
                    insur_city.append(self.insured_person.zip)
                if self.insured_person.country_id:
                    insur_country.append(self.insured_person.country_id.name)
        else:
            if self.insured_person.street:
                insur_street.append(self.insured_person.street)
            if self.insured_person.street2:
                insur_street.append(self.insured_person.street2)
            if self.insured_person.city:
                insur_city.append(self.insured_person.city)
            if self.insured_person.state_id:
                insur_city.append(self.insured_person.state_id.name)
            if self.insured_person.zip:
                insur_city.append(self.insured_person.zip)
            if self.insured_person.country_id:
                insur_country.append(self.insured_person.country_id.name)
        return {'insur_street':insur_street,
                'insur_city':insur_city,
                'insur_country':insur_country,
                'insur_phone':insur_phone,
                'insur_email':insur_email,
                }
    
    def get_vehicle_details_sample_orderform(self):
        col_reg_no = []
        col_chasis_no = []
        col_type_of_cover = []
        col_make = []
        col_model = []
        col_cylinder = []
        col_year = []
        col_cc = []
        col_type = []
        col_plate = []
        col_value = []
        vehicle = []
        row_count=0
        for line in self.order_line:
            if line.vehicle_id:
                if line.vehicle_id.id not in vehicle:
                    vehicle.append(line.vehicle_id.id)
                    col_reg_no.append(line.vehicle_id.license_plate)
                    col_chasis_no.append(line.vehicle_id.chasis_no)
                    col_type_of_cover.append(line.vehicle_id.type_of_cover.name)
                    col_make.append(line.vehicle_id.model_id.brand_id.name)
                    col_model.append(line.vehicle_id.model_id.name)
                    
                    col_cylinder.append(line.vehicle_id.cylinder)
                    col_year.append(line.vehicle_id.year_of_make)
                    col_cc.append(line.vehicle_id.cubic_capacity_list.name)
                    col_type.append(line.vehicle_id.body_type.name)
                    col_plate.append(line.vehicle_id.plate_type)   
                    col_value.append(line.vehicle_id.value)
                    row_count+=1
        return {'row_count':row_count,
                'col_reg_no':col_reg_no,
                'col_chasis_no':col_chasis_no,
                'col_type_of_cover':col_type_of_cover,
                'col_make':col_make,
                'col_model':col_model,
                'col_cylinder':col_cylinder,
                'col_year':col_year,
                'col_cc':col_cc,
                'col_type':col_type,
                'col_plate':col_plate,
                'col_value':col_value
                }

    def get_sum_insured_details_sample_orderform(self):
        col_sum_insured = []
        col_description = []
        col_value = []
        col_periode = []
        col_sub_total = []
        col_total = 0.00
        row_count=0
        #purchase_order = self.env['purchase.order'].search([('invoice_ids', 'in', [self.id])])
        #print("self.id",self.id,purchase_order)
        #policy_order = self.env['insurance.policy'].search([('purchase_ids', 'in', [purchase_order.id])])
        #print("policy_order",policy_order)
        for line in self.sum_insured_line:
            if line:
                col_sum_insured.append(line.sum_insured_id.name)
                col_description.append(line.name)
                col_value.append(line.value)
                col_periode.append(line.periode)
                col_sub_total.append(line.sub_amt) 
                col_total+=line.sub_amt
                row_count+=1
        return {'row_count':row_count,
                'col_sum_insured':col_sum_insured,
                'col_description':col_description,
                'col_value':col_value,
                'col_periode':col_periode,
                'col_sub_total':col_sub_total,
                'col_total':col_total,
                }

    def get_property_insured_details_sample_orderform(self):
        col_name = []
        col_note = []
        col_value = []
        col_periode = []
        col_sub_total = []
        col_total = 0.00
        row_count=0
        row_section = []
        row_sub=[]
        col_sub_total = []
        sub_total=0.0
        if self.building_line:
            obj_line=self.building_line[-1]
            for line in self.building_line:
                if line:
                    if line.display_type == 'line_section':
                        if sub_total:
                            col_name.append("Subtotal")
                            col_note.append(" ")
                            col_value.append(0.0)
                            col_periode.append(0.0)
                            col_sub_total.append(sub_total) 
                            col_total+=0.0
                            row_count+=1
                            row_sub.append(row_count)
                            sub_total=0.0
                        col_name.append(line.name)
                        col_note.append(" ")
                        col_value.append(0.0)
                        col_periode.append(0.0)
                        col_sub_total.append(0.0) 
                        col_total+=0.0
                        row_count+=1
                        row_section.append(row_count)
                    else:
                        col_name.append(line.name)
                        col_note.append(line.note)
                        col_value.append(line.value)
                        col_periode.append(line.periode)
                        col_sub_total.append(line.sub_amt) 
                        sub_total+=line.sub_amt
                        col_total+=line.sub_amt
                        row_count+=1
                    if line.id == obj_line.id:
                        if sub_total:
                            col_name.append("Subtotal")
                            col_note.append(" ")
                            col_value.append(0.0)
                            col_periode.append(0.0)
                            col_sub_total.append(sub_total) 
                            col_total+=0.0
                            row_count+=1
                            row_sub.append(row_count)
                            sub_total=0.0
        if self.insured_other_details:
            obj_line=self.insured_other_details[-1]
            for line in self.insured_other_details:
                if line:
                    print("line.name",line.name)
                    if line.display_type == 'line_section':
                        if sub_total:
                            col_name.append("Subtotal")
                            col_note.append(" ")
                            col_value.append(0.0)
                            col_periode.append(0.0)
                            col_sub_total.append(sub_total) 
                            col_total+=0.0
                            row_count+=1
                            row_sub.append(row_count)
                            sub_total=0.0
                        col_name.append(line.name)
                        col_note.append(" ")
                        col_value.append(0.0)
                        col_periode.append(0.0)
                        col_sub_total.append(0.0) 
                        col_total+=0.0
                        row_count+=1
                        row_section.append(row_count)
                    else:
                        col_name.append(line.sum_insured_id.name)
                        col_note.append(line.name)
                        col_value.append(line.value)
                        col_periode.append(line.periode)
                        col_sub_total.append(line.sub_amt) 
                        sub_total+=line.sub_amt
                        col_total+=line.sub_amt
                        row_count+=1
                    if line.id == obj_line.id:
                        if sub_total:
                            col_name.append("Subtotal")
                            col_note.append(" ")
                            col_value.append(0.0)
                            col_periode.append(0.0)
                            col_sub_total.append(sub_total) 
                            col_total+=0.0
                            row_count+=1
                            row_sub.append(row_count)
                            sub_total=0.0
        return {'row_count':row_count,
                'col_name':col_name,
                'col_note':col_note,
                'col_value':col_value,
                'col_periode':col_periode,
                'col_sub_total':col_sub_total,
                'col_total':col_total,
                'row_section':row_section,
                'row_sub':row_sub,
                }

    def get_sum_insured_sample_orderform(self):
        value = 0
        for order in self:
            if order.insurance_type=='motor':
                for line in order.order_line:
                    if line.vehicle_id:
                        value += line.vehicle_id.value
        return value

    def get_type_of_cover_sample_orderform(self):
        col_type_of_cover = ""
        vehicle = []
        type_cover = []
        for line in self.order_line:
            if line.vehicle_id:
                if line.vehicle_id.id not in vehicle:
                    vehicle.append(line.vehicle_id.id)
                    if line.vehicle_id.type_of_cover and line.vehicle_id.type_of_cover.id not in type_cover:
                        type_cover.append(line.vehicle_id.type_of_cover.id)
                        col_type_of_cover = col_type_of_cover+line.vehicle_id.type_of_cover.name + ", "
                    
        if not vehicle:
            if self.order_line:
                for line in self.order_line:
                    if line.vehicle_id:
                        if line.vehicle_id.id not in vehicle:
                            vehicle.append(line.vehicle_id.id)
                            if line.vehicle_id.type_of_cover and line.vehicle_id.type_of_cover.id not in type_cover:
                                type_cover.append(line.vehicle_id.type_of_cover.id)
                                col_type_of_cover = col_type_of_cover+line.vehicle_id.type_of_cover.name + ", "
        return col_type_of_cover

    def check_amount_in_words(self, sum, currency):
        return currency.amount_to_text(sum)
    
    def get_date_now(self):
        date_now =  datetime.now()
        user_tz = self.env.user.tz
        if user_tz:
            local = pytz.timezone(user_tz)
        else:
            local = pytz.timezone("Asia/Bahrain")
        print("local",local)
        return date_now.astimezone(local).strftime("%d-%b-%Y %I:%M:%S %p")
    
    def get_bank_lender(self):
        bank_str = ''
        for order in self:
            if order.bank_lender_id:
                bank_str = order.bank_lender_id.name
        return bank_str
    def get_date_order(self, date_time):
        date_only = date_time.date()
        date_only = datetime.strftime(date_only, "%Y-%m-%d")
        d = datetime.strptime(date_only, '%Y-%m-%d').strftime("%d %B %Y")
        return d
    ##############
    
    def action_sample_orderform(self):
        self.ensure_one()
        print("action_sample_orderform")
        view_id = self.env.ref('invoice_report_modify_ext.sample_orderform_wizard_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sample Order Form',
            'view_mode': 'form',
            'res_model': 'sample.order.form.wizard',
            'target': 'new',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'context': {'default_policy_order_id': self.id,'default_policy_order_name': self.name}
        }
        
    @api.multi
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('invoice_report_modify_ext', 'email_template_edi_policy')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        lang = self.env.context.get('lang')
        template = template_id and self.env['mail.template'].browse(template_id)
        if template and template.lang:
            lang = template._render_template(template.lang, 'insurance.policy', self.ids[0])
        ctx = {
            'default_model': 'insurance.policy',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'model_description': self.with_context(lang=lang).type_name,
            'custom_layout': "mail.mail_notification_paynow",
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
        
        