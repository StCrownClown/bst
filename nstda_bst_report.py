# -*- coding: utf-8 -*-
from openerp import tools, models, fields, api, exceptions, _
from pickle import TRUE
from _ctypes import sizeof
from docutils.parsers import null
from pychart.tick_mark import Null
from dateutil import parser
import time
from datetime import date
from dateutil.relativedelta import relativedelta

#from openerp.tools.translate import _
#from email import _name
#from bsddb.dbtables import _columns
#from openerp import tools
#import re
#from openerp import SUPERUSER_ID
#from docutils.parsers import null


####################################################################################################

    
class nstda_bst_report(models.Model):

    _name = 'nstda.bst.report'
    
    emp_name = fields.Many2one('nstdamas.employee','ชื่อพนักงาน', require=True)
#     book_date =  fields.Date('ใส่วันที่เบิก')


    @api.v7
    def report(self, cr, uid, ids, context=None):
        search_detail = self.browse(cr, uid, ids, context=context)[0]
         
        data = {}
        data['model'] = 'nstda.bst.report'
        data['parameters'] = {
                              'empid': search_detail.emp_name.id,
                              'status': 'pick',
                              }
        
#         data['parameters']['ID'] = search_detail.emp_name.id if search_detail.emp_name else 'all'
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'report_bst_2',
                'datas': data
        } 
