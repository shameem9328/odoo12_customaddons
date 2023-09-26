from odoo import api,models

class Lang(models.Model):
    _inherit = 'res.lang'

    @api.model
    def set_date_format(self):
        eng_lang = self.env.ref('base.lang_en')
        if eng_lang:
            eng_lang.date_format = '%d-%b-%Y'
            eng_lang.time_format = '%I:%M:%S %p'