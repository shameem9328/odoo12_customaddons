from odoo import  fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    notes = fields.Text("Notes")