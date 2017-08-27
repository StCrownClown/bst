# -*- coding: utf-8 -*-
from openerp import tools, models, fields, api, exceptions, _
from pickle import TRUE
from _ctypes import sizeof
from docutils.parsers import null
from pychart.tick_mark import Null
from dateutil import parser
from datetime import datetime,timedelta
from datetime import datetime
#from openerp.tools.translate import _
#from email import _name
#from bsddb.dbtables import _columns
#from openerp import tools
#import re
#from openerp import SUPERUSER_ID
#from docutils.parsers import null


####################################################################################################

    
class nstda_bst_discount(models.Model):   
    
    
    @api.one
    @api.onchange('discount')
    def set_discount(self):  
        res = self.env['nstda.bst.discount'].search([],limit=1,order="id DESC")
        if(res.discount):
            self.discount = res.discount  
        else:
            self.discount = 0
    
    _name = 'nstda.bst.discount'
    _inherit = 'res.config.settings'
    
    
    id = fields.Integer('id')
    discount = fields.Integer('ส่วนลด')
