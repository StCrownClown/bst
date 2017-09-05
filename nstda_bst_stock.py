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
        getbill_rs = self.env['nstda.bst.dbill'].search([('matno', '=', self.id),('tbill_ids','!=',False),('status','not in',['success','reject'])])
        set_sum = sum(line.qty_res for line in getbill_rs)
        self.qty_rs = set_sum
        
        
    def _cut_stock(self, cr, uid, ids, context=None):
        getbill_rec = self.pool.get('nstda.bst.dbill').search(cr, uid, [('tbill_ids', '=', context['bst_id']),('cut_stock','=',False)], context=context)
        
        for mat_bill in self.pool.get('nstda.bst.dbill').browse(cr, uid, getbill_rec):
            find_mat = self.pool.get('nstda.bst.stock').browse(cr, uid, mat_bill.matno.id)
            find_mat.qty += mat_bill.last_cs - mat_bill.qty_res

            self.pool.get('nstda.bst.dbill').write(cr, uid, mat_bill.id, {'last_cs': mat_bill.qty_res}, context=context)
#             self.pool.get('nstda.bst.dbill').write(cr, uid, mat_bill.id, {'cut_stock': True}, context=context)


    def _return_stock(self, cr, uid, ids, context=None):
        getbill_rec = self.pool.get('nstda.bst.dbill').search(cr, uid, [('tbill_ids', '=', context['bst_id']),('return_stock','=',False)], context=context)
        
        for mat_bill in self.pool.get('nstda.bst.dbill').browse(cr, uid, getbill_rec):
            find_mat = self.pool.get('nstda.bst.stock').browse(cr, uid, mat_bill.matno.id)
            if mat_bill.status == 'reject' and mat_bill.last_cs != 0:
                
                find_mat.qty += mat_bill.last_cs
                self.pool.get('nstda.bst.dbill').write(cr, uid, mat_bill.id, {'return_stock': True}, context=context)
                self.pool.get('nstda.bst.dbill').write(cr, uid, mat_bill.id, {'last_cs': 0}, context=context)
        
    
    _name = 'nstda.bst.stock'
    _rec_name = 'matdesc'
 
    saleorg = fields.Char('รหัสหน่วยงานขาย', readonly=True)
    distribution = fields.Char('ช่องทางการขาย', readonly=True)
    matno = fields.Char('รหัสสินค้า', readonly=True)
    matdesc = fields.Char('รายละเอียดสินค้า')
    barno = fields.Char('รหัสบาร์โค้ดสินค้า', readonly=True)
    taxcode = fields.Char('รหัสสาขาผู้เสียภาษีภาษี', readonly=True)
    uom = fields.Char('หน่วยนับ', readonly=True)
    unitprice = fields.Float('ราคา/ชิ้น')
    currency = fields.Char('สกุลเงิน', readonly=True, default='บาท')
    plant = fields.Char('ศูนย์ที่จัดเก็บสินค้า', readonly=True)
    storage = fields.Char('คลังที่จัดเก็บสินค้า', readonly=True)
    qty = fields.Integer('จำนวนคงเหลือ')
    qty_rs = fields.Integer('จำนวนขอเบิกรออนุมัติ', readonly=True, store=False, compute=_set_qty)
    pacode = fields.Char('รหัสปี', readonly=True)
    is_auth_admin = fields.Boolean('Check Author or Admin', readonly=True, compute='chk_auth_admin')
    
    
    @api.one
    @api.onchange('user_id')
    def chk_auth_admin(self):
        if self.env['res.users'].has_group('base.group_nstda_bst_authorities') or self.env['res.users'].has_group('base.group_nstda_bst_admin'):
            self.is_auth_admin = True
        else:
            self.is_auth_admin = False


nstda_bst_stock()
