# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import math
from odoo import api, fields, models, _
#from odoo.addons import decimal_precision as dp
#from odoo.tools import float_round
#import datetime
#from datetime import datetime
import pytz
dt_tm_format = "%d/%m/%Y %H:%M %p"
dt_format = "%d/%m/%Y"
from . import user_tz_dtm

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def amount_disc_calculation(self):
        discount = 0
        for line in self.invoice_line_ids:
            if line.product_id == self.env.ref('sale_discount_ext.discount_pdt'):
                discount += abs(line.price_unit)
        return discount

    def discount_pdt_id(self):
        return self.env.ref('sale_discount_ext.discount_pdt') or False

    def invoice_datetime(self):
        date_day = self.date_invoice
        if date_day:
            #user_tz = self.env.user.tz
            #if user_tz:
            #    local = pytz.timezone(user_tz)
            #else:
            #    local = pytz.timezone("Asia/Bahrain")
            obj_pos = self.env['pos.order'].sudo()
            if obj_pos.search([('invoice_id', 'in', self.ids)]):
                inv_datetime = self.create_date
                #date_day = inv_datetime.astimezone(local).strftime(dt_tm_format)
                date_day = user_tz_dtm.get_tz_date_time_str(self, inv_datetime, self.env.user)
            else:
                #date_day = date_day.strftime(dt_format)
                date_day = user_tz_dtm.get_date_str(self, date_day, self.env.user)
            return date_day
        else:
            return ""

    def get_doc_ref_number(self):
        obj_pos = self.env['pos.order'].sudo()
        doc_ref = self.number
        if obj_pos.search([('invoice_id', 'in', self.ids)]):
            ref = obj_pos.search([('invoice_id', 'in', self.ids)])[0].config_id.name
            doc_ref = ref + ' - ' + doc_ref
        return doc_ref

