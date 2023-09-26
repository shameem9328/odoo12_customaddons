# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Repair(models.Model):
    _inherit = 'repair.order'
    

    @api.multi
    def action_send_mail(self):
        self.ensure_one()
        template_id = self.env.ref('repair.mail_template_repair_quotation').id
        if template_id:
            template_id = self.env['mail.template'].sudo().browse(template_id)
            report_with_letter_head = self.env.ref('refacs_custom_reports.action_report_repair_order')
            if template_id.report_template.id != report_with_letter_head.id:
                template_id.report_template = report_with_letter_head.id
        return super(Repair, self).action_send_mail()
    @api.multi
    def print_repair_order(self):
        return self.env.ref('refacs_custom_reports.action_report_repair_order').report_action(self)

    