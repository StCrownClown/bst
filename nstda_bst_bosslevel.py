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
 
    boss_level = fields.Integer('Boss Level')
    approve_amount = fields.Float('จำนวนเงินที่สามารถอนุมัติ')


nstda_bst_bosslevel()
