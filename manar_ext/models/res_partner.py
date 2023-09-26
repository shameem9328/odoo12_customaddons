from odoo import api, models,fields
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    mobile = fields.Char(required=True,track_visibility='onchange')
    name = fields.Char(track_visibility='onchange')
    
    def check_duplicate(self):
        msgs = []
        for rec in self:
            if rec.mobile:
                #print(rec.parent_id,rec.name)
                duplicates = self.search([
                                          ('mobile','=',rec.mobile),
                                          ('parent_id','!=',rec.parent_id.id),
                                          ('id','not in',[rec.id,rec.parent_id.id]+rec.child_ids.ids)
                                          ])
                suppliers = duplicates.filtered(lambda p:p.supplier)
                customers = duplicates.filtered(lambda p:p.customer)
                partner_type = 'Partner'
                if suppliers and customers:
                    partner_type = "Customer / Supplier"
                elif customers:
                    partner_type = 'Customer'
                elif suppliers:
                    partner_type = 'Supplier'
                partner_list = "\n".join(duplicates.mapped('display_name'))
                duplicates and msgs.append(f"{partner_type} already exist with this mobile number.\nMobile: {rec.mobile}\n\n" \
                                           f"{partner_type}:-\n{partner_list}")
        if msgs:
            raise UserError("\n".join(msgs))
            
    
    def check_mandatory(self):
        msgs = []
        for rec in self:
            if not rec._context.get('user_creation',False) and \
            not rec._context.get('company_creation',False) and \
            not rec.user_ids and \
            not rec.ref_company_ids and \
            (not rec.mobile or \
            rec.mobile.isspace()):
                partner_type = 'Partner'
                if rec.customer and rec.supplier:
                    partner_type = "Customer / Supplier"
                elif rec.customer:
                    partner_type = 'Customer'
                elif rec.supplier:
                    partner_type = 'Supplier'
                msgs.append(f"Mobile Number must be required.\n{partner_type}: {rec.display_name}")
        if msgs:
            raise UserError("\n\n".join(msgs))
            
    @api.model_create_multi
    def create(self, vals_list):
        partners = super(ResPartner, self).create(vals_list)
        partners.check_mandatory()
        partners.check_duplicate()
        return partners

    @api.multi
    def write(self, vals):
        result = super(ResPartner, self).write(vals)
        self.check_mandatory()
        if len(self.ids) > 1 or \
        vals.get('mobile',False):
            self.check_duplicate()
        return result
    
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        res = super(ResPartner,self).name_search(name, args, operator, limit)
        positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
        partners = self
        if operator in positive_operators:
            ids_used = [rp[0] for rp in res]
            for col in ['mobile','phone']:
                domain = [(col, operator, name),('id','not in',ids_used)] 
                partners = self.search(domain + args, limit=limit)
                ids_used += partners.ids
                res += partners.name_get()
        return res 
        