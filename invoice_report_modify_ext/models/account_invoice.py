# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta
#from odoo.addons import decimal_precision as dp
#from .ctt_objects import currency_to_text, supported_language
#from datetime import datetime, time
from pytz import timezone, UTC
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    """def payment_made_within_days(self):
        no_days = (self.date_due-self.date_invoice).days
        return no_days"""
    @api.multi
    def check_amount_in_words(self, sum, currency):
    #    return currency_to_text(sum, currency, language)
        return currency.amount_to_text(sum)        
    def get_vehicle_details(self):
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
        for line in self.invoice_line_ids:
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
        if not vehicle:
            #print("self.policy_id",self.policy_id)
            #policy_order = self.env['insurance.policy'].search([('invoice_ids', 'in', [self.id])])
            #print("policy_order",policy_order,self.id)
            if self.policy_id:
                for line in self.policy_id.order_line:
                    if line.vehicle_id:
                        if line.vehicle_id.id not in vehicle:
                            vehicle.append(line.vehicle_id.id)
                            col_reg_no.append(line.vehicle_id.license_plate)
                            col_chasis_no.append(line.vehicle_id.chasis_no)
                            col_type_of_cover.append(line.vehicle_id.type_of_cover.name)
                            col_make.append(line.vehicle_id.model_id.brand_id.name)
                            col_model.append(line.vehicle_id.model_id.name) 
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
    def get_insured_name(self):
        insured_str = ''
        #if self.insur_bank_id.bank_id:
        #    if self.insur_bank_id.bank_id.is_customer:
        #        insured_str = self.insur_bank_id.bank_id.name
        #    else:
        #       insured_str = self.insured_person.name+"-"+self.insur_bank_id.bank_id.name
        if self.insur_bank_id:
            if self.insur_bank_id.is_customer:
                insured_str = self.insur_bank_id.name
            else:
                insured_str = self.insured_person.name+"-"+self.insur_bank_id.name
        else:
            insured_str = self.insured_person.name
        return insured_str
    def get_insured_person_vat(self):
        vat_str = ''
        if self.insur_bank_id:
            if not self.insur_bank_id.is_customer:
                vat_str = self.insured_person.vat
        else:
            vat_str = self.insured_person.vat
        return vat_str    

    def get_vendor_insured_name(self):
        insured_str = ''
        purchase_order = self.env['purchase.order'].search([('invoice_ids', 'in', [self.id])])
        if len(purchase_order) == 1:
            policy_order = self.env['insurance.policy'].search([('purchase_ids', 'in', [purchase_order.id])])
            if len(policy_order) == 1:
                #if policy_order.partner_bank_id.bank_id:
                #    if policy_order.partner_bank_id.bank_id.is_customer:
                #        insured_str = policy_order.partner_bank_id.bank_id.name
                #    else:
                #        insured_str = policy_order.insured_person.name+"-"+policy_order.partner_bank_id.bank_id.name
                if policy_order.bank_id:
                    if policy_order.bank_id.is_customer:
                        insured_str = policy_order.bank_id.name
                    else:
                        insured_str = policy_order.insured_person.name+"-"+policy_order.bank_id.name
                else:
                    insured_str = self.insured_person.name
        return insured_str
    def get_vendor_cpr_or_cr(self):
        print("kkkk")
        cpr_cr = ""
        value =""
        purchase_order = self.env['purchase.order'].search([('invoice_ids', 'in', [self.id])])
        if len(purchase_order) == 1:
            policy_order = self.env['insurance.policy'].search([('purchase_ids', 'in', [purchase_order.id])])
            if len(policy_order) == 1:
                if policy_order.bank_id:
                    if not policy_order.bank_id.is_customer:
                        if self.insured_person.company_type == 'company':
                            cpr_cr="CR"
                            value=self.insured_person.cr_no
                        if self.insured_person.company_type == 'person':
                            cpr_cr="CPR"
                            value=self.insured_person.cpr_no
                    else:
                        cpr_cr="CR"
                        value=policy_order.bank_id.cr_no
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
        
    def get_vendor_insured_address(self):
        insur_street = []
        insur_city =[]
        insur_country =[]
        insur_phone = []
        insur_email = []
        purchase_order = self.env['purchase.order'].search([('invoice_ids', 'in', [self.id])])
        if len(purchase_order) == 1:
            policy_order = self.env['insurance.policy'].search([('purchase_ids', 'in', [purchase_order.id])])
            if len(policy_order) == 1:
                if policy_order.bank_id:
                    if policy_order.bank_id.is_customer:
                        if policy_order.bank_id.street:
                            insur_street.append(policy_order.bank_id.street)
                        if policy_order.bank_id.street2:
                            insur_street.append(policy_order.bank_id.street2)
                        if policy_order.bank_id.city:
                            insur_city.append(policy_order.bank_id.city)
                        if policy_order.bank_id.state:
                            insur_city.append(policy_order.bank_id.state.name)
                        if policy_order.bank_id.zip:
                            insur_city.append(policy_order.bank_id.zip)
                        if policy_order.bank_id.country:
                            insur_country.append(policy_order.bank_id.country.name)
                        if policy_order.bank_id.phone:
                            insur_phone.append(policy_order.bank_id.phone)
                        if policy_order.bank_id.email:
                            insur_email.append(policy_order.bank_id.email)
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
                    #return self.insured_person
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
        #print("insured_str",insured_str)
        return {'insur_street':insur_street,
                'insur_city':insur_city,
                'insur_country':insur_country,
                'insur_phone':insur_phone,
                'insur_email':insur_email,
                }
        #return insured_str,insur_city,insur_country,insur_phone,insur_email
    
    def get_sum_insured_details(self):
        col_sum_insured = []
        col_description = []
        col_value = []
        col_periode = []
        col_sub_total = []
        col_total = 0.00
        row_count=0
        purchase_order = self.env['purchase.order'].search([('invoice_ids', 'in', [self.id])])
        print("self.id",self.id,purchase_order)
        policy_order = self.env['insurance.policy'].search([('purchase_ids', 'in', [purchase_order.id])])
        print("policy_order",policy_order)
        for line in policy_order.sum_insured_line:
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
    def get_vendor_remark(self):
        remark_str = ''
        purchase_order = self.env['purchase.order'].search([('invoice_ids', 'in', [self.id])])
        if len(purchase_order) == 1:
            if purchase_order.remarks:
                remark_str = purchase_order.remarks
        #print("remark_str",remark_str)
        return remark_str
    def get_bank_lender(self):
        bank_str = ''
        purchase_order = self.env['purchase.order'].search([('invoice_ids', 'in', [self.id])])
        policy_order = self.env['insurance.policy'].search([('purchase_ids', 'in', [purchase_order.id])])
        if policy_order.bank_lender_id:
            bank_str = policy_order.bank_lender_id.name
        return bank_str

    def get_policy_type(self):
        remark_str = ''
        purchase_order = self.env['purchase.order'].search([('invoice_ids', 'in', [self.id])])
        policy_order = self.env['insurance.policy'].search([('purchase_ids', 'in', [purchase_order.id])])
        if policy_order.policy_type:
            remark_str = dict(policy_order._fields['policy_type'].selection).get(policy_order.policy_type)
        return remark_str
    def get_previous_policy(self):
        remark_str = ''
        purchase_order = self.env['purchase.order'].search([('invoice_ids', 'in', [self.id])])
        policy_order = self.env['insurance.policy'].search([('purchase_ids', 'in', [purchase_order.id])])
        if policy_order.previous_policy:
            remark_str = policy_order.previous_policy
        return remark_str
    def get_sum_insured(self):
        value = 0
        #purchase_order = self.env['purchase.order'].search([('invoice_ids', 'in', [self.id])])
        #policy_order = self.env['insurance.policy'].search([('purchase_ids', 'in', [purchase_order.id])])
        #if policy_order.sum_insured:
        #    value = policy_order.sum_insured
        for invoice in self:
            if invoice.insurance_type=='motor':
                for line in invoice.invoice_line_ids:
                    if line.vehicle_id:
                        value += line.vehicle_id.value
        print("value",value)
        return value
    def get_road_assist(self):
        value_str = ''
        purchase_order = self.env['purchase.order'].search([('invoice_ids', 'in', [self.id])])
        policy_order = self.env['insurance.policy'].search([('purchase_ids', 'in', [purchase_order.id])])
        if policy_order.assistance_terms.name:
            value_str = policy_order.assistance_terms.name
        return value_str
    def get_date_now(self):
        date_now =  datetime.now()
        user_tz = self.env.user.tz
        if user_tz:
            local = pytz.timezone(user_tz)
        else:
            local = pytz.timezone("Asia/Bahrain")
        print("local",local)
        return date_now.astimezone(local).strftime("%d-%b-%Y %I:%M:%S %p")
    def get_type_of_cover(self):
        col_type_of_cover = ""
        vehicle = []
        type_cover = []
        for line in self.invoice_line_ids:
            if line.vehicle_id:
                if line.vehicle_id.id not in vehicle:
                    vehicle.append(line.vehicle_id.id)
                    if line.vehicle_id.type_of_cover and line.vehicle_id.type_of_cover.id not in type_cover:
                        type_cover.append(line.vehicle_id.type_of_cover.id)
                        col_type_of_cover = col_type_of_cover+line.vehicle_id.type_of_cover.name + ", "
                    
        if not vehicle:
            if self.policy_id:
                for line in self.policy_id.order_line:
                    if line.vehicle_id:
                        if line.vehicle_id.id not in vehicle:
                            vehicle.append(line.vehicle_id.id)
                            if line.vehicle_id.type_of_cover and line.vehicle_id.type_of_cover.id not in type_cover:
                                type_cover.append(line.vehicle_id.type_of_cover.id)
                                col_type_of_cover = col_type_of_cover+line.vehicle_id.type_of_cover.name + ", "
        return col_type_of_cover
    def get_policy_order(self):
        value_str = ''
        purchase_order = self.env['purchase.order'].search([('invoice_ids', 'in', [self.id])])
        if purchase_order.origin:
            value_str = purchase_order.origin
        return value_str
    def get_care_of(self):
        value_str = ''
        if self.policy_id:
            print("self.policy_id",self.policy_id)
            if self.policy_id.partner_id:
                value_str = self.policy_id.partner_id.name
        return value_str
    
    def get_insurance_company(self):
        company_str = ''
        insur_comp = []
        if self.policy_id:
            for line in self.policy_id.order_line:
                if line.insur_company_id:
                    if line.insur_company_id.id not in insur_comp:
                        insur_comp.append(line.insur_company_id.id)
                        company_str += line.insur_company_id.name + ', '
        return company_str
    
    def get_insur_company_bank_info(self):
        company_str = ''
        insur_comp = []
        bank_name = []
        acc_no = []
        iban = []
        row_count = 0
        if self.policy_id:
            for line in self.policy_id.order_line:
                if line.insur_company_id:
                    if line.insur_company_id.id not in insur_comp:
                        insur_comp.append(line.insur_company_id.id)
            for i in insur_comp:
                partner = self.env['res.partner'].browse(i)
                for bank in partner.bank_ids:
                    bank_name.append(bank.bank_id.name)
                    acc_no.append(bank.acc_number)
                    iban.append(bank.iban) 
                    row_count += 1 
        return [row_count,bank_name,acc_no,iban]
    
    def get_property_insured_details(self):
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
        purchase_order = self.env['purchase.order'].search([('invoice_ids', 'in', [self.id])])
        #print("self.id",self.id,purchase_order)
        policy_order = self.env['insurance.policy'].search([('purchase_ids', 'in', [purchase_order.id])])
        #print("policy_order",policy_order)
        if policy_order.building_line:
            obj_line=policy_order.building_line[-1]
            for line in policy_order.building_line:
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
        if policy_order.insured_other_details:
            obj_line=policy_order.insured_other_details[-1]
            for line in policy_order.insured_other_details:
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
        print("row_section",row_section)    
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