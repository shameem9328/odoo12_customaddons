from datetime import datetime,timedelta
from odoo import models
import pytz

def get_tz_date_time_str(self,dtm,user_id=False):
    tz_str = get_timezone(self,user_id)
    tz = pytz.timezone(tz_str)
    return dtm.astimezone(tz).strftime(get_date_time_format(self,user_id))

def get_date_str(self,dt,user_id=False):
    return dt.strftime(get_date_format(self,user_id))

def get_language(self,user_id=False):
    if user_id:
        self = self.sudo(user_id)
    print('get_language = ',self.env.user)
    lang_code = self.env.user.lang or 'en_US'
    return self.env['res.lang'].sudo().search([('code','=',lang_code)])
    
def get_date_format(self,user_id=False):
    langauge_id = get_language(self,user_id)
    return langauge_id.date_format

def get_time_format(self,user_id=False):
    langauge_id = get_language(self,user_id)
    return langauge_id.time_format
    
def get_date_time_format(self,user_id=False):
    langauge_id = get_language(self,user_id)
    return f"{langauge_id.date_format} {langauge_id.time_format}"
    
def get_timezone(self,user_id=False):
    if user_id:
        self = self.sudo(user_id)
    tz =  self.env.user.tz or 'Asia/Bahrain'
    return tz
    
def get_tz_dtm_detals(self,user_id=False):
    return {'timezone':get_timezone(self,user_id),
            'date_format':get_date_format(self,user_id),
            'time_format':get_time_format(self,user_id),
            'date_time_format':get_date_time_format(self,user_id),
            'langauge':get_language(self,user_id)
            }


    
        