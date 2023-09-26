from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class KSResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ks_enable_discount = fields.Boolean(string="Activate Discount")
    ks_policy_discount_account = fields.Many2one('account.account', string="Insurance Discount Account")
    ks_accounting_present = fields.Boolean(compute='ks_check_charts_of_accounts')

    def get_values(self):
        ks_res = super(KSResConfigSettings, self).get_values()
        ks_res.update(
            ks_enable_discount=self.env['ir.config_parameter'].sudo().get_param('ks_enable_discount'),
            ks_policy_discount_account=int(self.env['ir.config_parameter'].sudo().get_param('ks_policy_discount_account')),
            
        )
        return ks_res

    def set_values(self):
        super(KSResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('ks_enable_discount', self.ks_enable_discount)
        if self.ks_enable_discount:
            self.env['ir.config_parameter'].set_param('ks_policy_discount_account', self.ks_policy_discount_account.id)
            