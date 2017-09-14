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

####################################################################################################

    
class nstda_bst_bosslevel(models.Model):   
        
    _name = 'nstda.bst.bosslevel'
 
    boss_level = fields.Integer('Boss Level', readonly=True)
    start_amount = fields.Float('วงเงินเริ่มต้น', readonly=True, store=True, compute='set_start_amount')
    approve_amount = fields.Float('จำนวนเงินที่สามารถอนุมัติ')

    
    @api.one
    @api.depends('approve_amount')
    @api.onchange('approve_amount')
    def set_start_amount(self):
        if self.boss_level == 1:
            self.start_amount = 1
        elif self.boss_level == 3:
            level = 2
            find_amount = self.env['nstda.bst.bosslevel'].search([('boss_level','=',level)], limit=1).start_amount
            self.start_amount = find_amount
        else :
            level = self.boss_level - 1
            find_amount = self.env['nstda.bst.bosslevel'].search([('boss_level','=',level)], limit=1).approve_amount
            self.start_amount = find_amount + 1


nstda_bst_bosslevel()
