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

    
class nstda_bst_stock(models.Model):   
        
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        
        if name:
            recs = self.search(['|', ('matno', 'ilike', name), ('matdesc', 'ilike', name), ] + args, limit=limit)
        if not recs:
            recs = self.search(['|', ('matno', operator, name), ('matdesc', operator, name), ] + args, limit=limit)
        return recs.name_get()
        
        
    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        result = {}
        
        for partner in self.pool.get('nstda.bst.stock').browse(cr, uid,ids):
            try:
                result[partner.id] = partner.matno + " " + partner.matdesc 
            except:
                continue
        return result.items()  


    @api.one
    def _set_qty(self):
        getbill_rs = self.env['nstda.bst.dbill'].search([('matno', '=', self.id),('hbill_ids','!=',False)])
        set_sum = sum(line.qty for line in getbill_rs)
        self.qty_res = set_sum
        
           
#     @api.one
#     def _cut_stock(self):
#         getbill_rec = self.env['nstda.bst.dbill'].search([('tbill_ids','!=',False),('qty_res','!=',False),('cut_stock','!=',False)])
#         for id in getbill_rec:
#             self.qty = self.qty - id.qty_res
        
    
    _name = 'nstda.bst.stock'
    _rec_name = 'matdesc'
 
    saleorg = fields.Char('รหัสหน่วยงานขาย', readonly=True)
    distribution = fields.Char('ช่องทางการขาย', readonly=True)
    matno = fields.Char('รหัสสินค้า')
    matdesc = fields.Char('รายละเอียดสินค้า')
    barno = fields.Char('รหัสบาร์โค้ดสินค้า')
    taxcode = fields.Char('รหัสสาขาผู้เสียภาษีภาษี')
    uom = fields.Char('หน่วยนับ')
    unitprice = fields.Float('ราคา/ชิ้น')
    currency = fields.Char('สกุลเงิน', readonly=True, default='บาท')
    plant = fields.Char('ศูนย์ที่จัดเก็บสินค้า', readonly=True)
    storage = fields.Char('คลังที่จัดเก็บสินค้า', readonly=True)
    qty = fields.Integer('จำนวนคงเหลือ')
    qty_res = fields.Integer('จำนวนขอเบิกรออนุมัติ', readonly=True, store=False, compute=_set_qty)
    pacode = fields.Char('รหัสปี')

nstda_bst_stock()
