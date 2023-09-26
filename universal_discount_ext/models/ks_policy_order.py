# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class KsGlobalDiscountSales(models.Model):
    _inherit = "insurance.policy"

    #ks_global_discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')],
    #                                           string='Universal Discount Type',
    #                                           readonly=True,
    #                                           states={'draft': [('readonly', False)]},
    #                                           default='percent')
    ks_global_discount_rate = fields.Float('Dhaif Discount',
                                           readonly=True,
                                           states={'draft': [('readonly', False)]})
    ks_amount_discount = fields.Monetary(string='Discount', readonly=True, compute='_amount_all', store=True,
                                         track_visibility='always')
    ks_enable_discount = fields.Boolean(compute='ks_verify_discount')

    @api.depends('name')
    def ks_verify_discount(self):
        self.ks_enable_discount = self.env['ir.config_parameter'].sudo().get_param('ks_enable_discount')

    @api.depends('order_line.price_total', 'ks_global_discount_rate')
    def _amount_all(self):
        for rec in self:
            res = super(KsGlobalDiscountSales, rec)._amount_all()
            #if not ('ks_global_tax_rate' in rec):
            rec.ks_calculate_discount()
        return res

    ##KPL##
    @api.multi
    def create_invoices(self):
        self.ensure_one()
        self.check_policy_no()
        obj_inv = self.env['account.invoice']
        obj_inv_line = self.env['account.invoice.line']
        
        inv_vals = self._prepare_invoice()
        inv_vals['invoice_line_ids'] = []
        inv_vals['policy_no'] = self.policy_no
        inv_vals['insurance_type'] = self.insurance_type
        
        inv_vals['insur_bank_id'] = self.bank_id.id
        #inv_vals['insur_bank_id'] = self.partner_bank_id.id
        
        inv_vals['date_from'] = self.date_from
        inv_vals['date_to'] = self.date_to 
        inv_vals['excess_amt'] = self.excess_amt.id
        #inv_vals['type_of_cover'] = self.type_of_cover.id
        inv_vals['insured_person'] = self.insured_person.id
        if self.agent_id:    
            inv_vals['agent_id'] = self.agent_id.id
        inv_vals['comment'] = self.note
        #inv_vals['ks_global_discount_type'] = self.ks_global_discount_type
        inv_vals['ks_global_discount_rate'] = self.ks_global_discount_rate
        
        inv_id = obj_inv.create(inv_vals)
        for line in self.order_line:
            inv_line_vals = line._prepare_invoice_line()
            inv_line_vals['invoice_id'] = inv_id.id
            inv_line_vals['insurance_line_ids'] = [(6, 0, [line.id])]
            
            inv_line_vals['vehicle_id'] = line.vehicle_id.id
            #inv_line_vals['insur_company_id'] = line.insur_company_id.id
            obj_inv_line.create(inv_line_vals) 
        
        self.is_customer_invoice=True
        inv_id.is_tax_hide = True
        inv_id.compute_taxes()
        inv_id.policy_id=self.id
        return self.action_view_invoices(inv_id)
    #####
    @api.multi
    def ks_calculate_discount(self):
        for rec in self:
            if rec.ks_global_discount_rate:
                rec.ks_amount_discount = rec.ks_global_discount_rate if rec.amount_untaxed > 0 else 0
            else:
                rec.ks_amount_discount = 0
            #elif rec.ks_global_discount_type == "percent":
            #    if rec.ks_global_discount_rate != 0.0:
            #        rec.ks_amount_discount = (rec.amount_untaxed + rec.amount_tax) * rec.ks_global_discount_rate / 100
            
            rec.amount_total = rec.amount_untaxed + rec.amount_tax - rec.ks_amount_discount

    #@api.constrains('ks_global_discount_rate')
    #def ks_check_discount_value(self):
    #    if self.ks_global_discount_type == "percent":
    #        if self.ks_global_discount_rate > 100 or self.ks_global_discount_rate < 0:
    #            raise ValidationError('You cannot enter percentage value greater than 100.')
    #    else:
    #        if self.ks_global_discount_rate < 0 or self.ks_global_discount_rate > self.amount_untaxed:
    #            raise ValidationError(
    #               'You cannot enter discount amount greater than actual cost or value lower than 0.')
