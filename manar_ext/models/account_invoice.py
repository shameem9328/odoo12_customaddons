from odoo import  fields, models

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    def _get_del_method(self):
        return [('del','Delivery'),
                ('ta','Take Away')]
        
    def _get_del_sure(self):
        return [('sure','Sure'),
                ('not_sure','Not Sure')]
        
    del_method = fields.Selection(_get_del_method,string="DEL / TA",track_visibility='onchange')
    del_date = fields.Datetime("Delivery Date",track_visibility='onchange')
    del_sure = fields.Selection(_get_del_sure,string="Del. Sure / Not",track_visibility='onchange')
    name = fields.Char(string='Reference/Description', index=True,
                       readonly=True, states={'draft': [('readonly', False)]}, copy=False,
                       help='The name that will be used on account move lines',track_visibility='onchange')
    