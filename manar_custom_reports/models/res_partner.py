# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#from datetime import timedelta
from odoo import api, fields, models, _
#from odoo.tools.misc import format_date

#_FOLLOWUP_STATUS = [('in_need_of_action', 'In need of action'), ('with_overdue_invoices', 'With overdue invoices'), ('no_action_needed', 'No action needed')]

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    partner_total_due = fields.Monetary(compute='_compute_for_partner_total_due', store=False, readonly=True)
    is_outstanding_hide = fields.Boolean(string='Hide Partner Outstanding', help='Hide total outstanding in invoice report')

    def _compute_for_partner_total_due(self):
        """
        Compute the fields 'total_due'
        """
        today = fields.Date.today()
        field_names = ['amount_residual:sum']
        groupby = ['partner_id']

        domain_due = [
            ('partner_id', 'in', self.ids),
            ('reconciled', '=', False),
            ('account_id.deprecated', '=', False),
            ('account_id.internal_type', '=', 'receivable'),
        ]
        total_due_all = self.env['account.move.line'].read_group(
            domain_due,
            field_names,
            groupby,
        )
        total_due_all = dict(
            (res['partner_id'][0], res['amount_residual'])
            for res in total_due_all
        )
        for record in self:
            total_due = total_due_all.get(record.id, 0)
            record.partner_total_due = total_due


