from odoo import api, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    @api.model
    def create(self, vals_list):
        return super(ResCompany, self.with_context(company_creation=True)).create(vals_list)
    
    