# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models, _
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class account_payment(models.Model):
    _inherit = "account.payment"
    _description = "Payments"
    
    cheque_no = fields.Char(string="Cheque No")
    cheque_date = fields.Date(string="Cheque Date")
    is_cleared = fields.Boolean(string="Is Cleared")
    note = fields.Text('Remark')