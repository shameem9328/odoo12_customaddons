from odoo import models,api,fields
from odoo.exceptions import UserError
class BugFix(models.TransientModel):
    _name='bug.fix'

    passwd = fields.Char('Password 111')
    
    def update_inv_del_date(self):
        sales = self.env['sale.order'].search([('inv_updated','=',False),
                                               ('invoice_status','=','invoiced'),
                                               ('commitment_date','!=',False)],limit=100,order='id desc')
        for sale in sales:
            #print(sale)
            sale.invoice_ids.filtered(lambda r: not r.del_date).write({'del_date':sale.commitment_date})
            sale.inv_updated = True
    
    @api.multi
    def btn_change(self):
        if self._uid not in [1,2]:
            raise UserError("Only Administrator can do this operation")
        if self.passwd != '1454':
            raise UserError("Authentication Failed")
        
        
        
        return True
        for rec in self.env['account.payment'].search([('is_from_pos','=',False),
                                                       ('name','ilike','POS/2020/'),
                                                       ('invoice_ids','!=',False)]):
            rec.is_from_pos = True
        
        """
        for rec in self.env['account.payment'].search([('create_uid','!=',1),
                                                       ('team_id','=',1)]):
            team_id = self.env['crm.team']._get_default_team_id(rec.create_uid.id)
            if team_id:
                rec.team_id = team_id
        """
        
        
        
