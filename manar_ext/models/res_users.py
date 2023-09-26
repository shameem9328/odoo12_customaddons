
from odoo import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsers, self.with_context(default_customer=False,user_creation=True)).create(vals_list)
        return users