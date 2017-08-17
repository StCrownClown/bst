# -*- coding: utf-8 -*-
from openerp import tools, models, fields, api, exceptions, _
from pickle import TRUE
from _ctypes import sizeof
from docutils.parsers import null
from pychart.tick_mark import Null
from dateutil import parser

from datetime import datetime, timedelta
from datetime import datetime
from dateutil import relativedelta as rdelta
from openerp.osv import osv

import time
import re

from datetime import date
from dateutil.relativedelta import relativedelta
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import http
from openerp.http import request
from openerp.exceptions import ValidationError

# from openerp.tools.translate import _
# from email import _name
# from openerp import tools
# from openerp import SUPERUSER_ID


####################################################################################################


class nstda_bst_dbill(models.Model):  
                        

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        if context is None:
            context = {}
        res = super(nstda_bst_dbill, self).read(cr, uid, ids, fields=fields, context=context, load=load)
        idx = 0
        for r in res:
            if r.has_key('no'):
                r['no'] = int(idx + 1)
            res[idx] = r
            idx = idx + 1
        return res
        
        
    @api.model
    def create(self, values):
        values['no'] = 0
        res = super(nstda_bst_dbill, self).create(values)
        return res
    
    
#     @api.multi
#     def write(self, values):
#         res_id = super(nstda_bst_dbill, self).write(values)
#         return res_id 


    def _needaction_count(self, cr, uid, domain=None, context=None):
        dom = []
        if not domain:
            dom = self._needaction_domain_get(cr, uid, context=context)
        else:
            dom = domain

        if not dom:
            return 0
        res = self.search(cr, uid, (domain or []) + dom, limit=100, order='id DESC', context=context)
        return len(res)
      
      
    _name = 'nstda.bst.dbill'
    _inherit = 'ir.needaction_mixin'
    _order = 'create_date ASC'
    
    no = fields.Integer(string="ลำดับ ", store=True, readonly=True, default=0)
    matno = fields.Many2one('nstda.bst.stock', 'รหัสสินค้า', required=True, domain=[('qty','>','0')])
    hbill_ids = fields.Many2one('nstda.bst.hbill','รายละเอียดสินค้า')
    tbill_ids = fields.Many2one('nstda.bst.hbill','รายละเอียดสินค้า', store=True)

    qty = fields.Integer('จำนวนที่ต้องการ', required=False)
    sum = fields.Float(string="ราคารวม", store=True, compute='_set_sum')
    qty_res = fields.Integer('จำนวนที่ต้องการ', store=True, readonly=False)
    sum_res = fields.Float(string="ราคารวม", store=True, compute='_set_sum_res')
    cut_stock = fields.Boolean('ตัดสต็อกสำเร็จ', store=True, default=False, compute='check_qty_more')
    return_stock = fields.Boolean('คืนสต็อกสำเร็จ', store=True, compute='check_qty_equal')
    dbill_discount_sum = fields.Float(string="ราคารวม(ส่วนลด)", store=True, compute='_set_discount')
    
    matdesc = fields.Char('รายละเอียดสินค้า', readonly=True, related='matno.matdesc') 
    balance = fields.Integer('จำนวนคงเหลือ', readonly=True, store=False, related='matno.qty')
    unitprice = fields.Float('ราคา/ชิ้น', readonly=True, store=True, compute='_set_unitprice')
    currency = fields.Char('สกุลเงิน', readonly=True, store=False, related='matno.currency')
    balance_rs = fields.Integer('จำนวนขอเบิกรออนุมัติ', readonly=True, related='matno.qty_rs')
    uom = fields.Char('หน่วยนับ', readonly=True, store=True, related='matno.uom')
    uom_1 = fields.Char('หน่วยนับ', readonly=True, store=False, related='uom')
    uom_2 = fields.Char('หน่วยนับ', readonly=True, store=False, related='uom')
    last_cs = fields.Integer('จำนวนตัดสต็อกล่าสุด', readonly=True)

    dbill_discount = fields.Float('nstda.bst.hbill', readonly=True, store=False, related='hbill_ids.discount')
    dbill_empname = fields.Char('nstda.bst.hbill', readonly=True, store=False, related='hbill_ids.empname')
    dbill_prj_cct = fields.Char('nstda.bst.hbill', readonly=True, store=False, related='hbill_ids.prj_cct')
    
    status = fields.Selection([('reject', 'ยกเลิก'),
                               ('draft', 'ร่าง'),
                               ('wait_prjm', 'รออนุมัติ'),
                               ('wait_boss', 'รออนุมัติ'),
                               ('wait_approvers', 'รอเบิก'),
                               ('pick', 'รอจัดเตรียมสินค้า'),
                               ('ready', 'รอรับสินค้า'),
                               ('success', 'รับสินค้าแล้ว')], 'สถานะ', store=True, readonly=True, related='tbill_ids.status')

    inv_b = fields.Boolean('Check boss', store=False, readonly=True, compute='_get_inv_b')
    inv_p = fields.Boolean('Check prjm', store=False, readonly=True, compute='_get_inv_p')
    inv_a = fields.Boolean('Check approve', store=False, readonly=True, compute='_get_inv_a')
    inv_k = fields.Boolean('Check approve', store=False, readonly=True, compute='_get_inv_k')
    inv_r = fields.Boolean('Check ready', store=False, readonly=True, compute='_get_inv_r')
    
#     _sql_constraints = [
#                         ('_check_qty', 'กรุณาระบุจำนวนในรายละเอียดสินค้าให้ถูกต้อง(จำนวนต้องไม่น้อยกว่าหรือเท่ากับศูนย์)', ['qty'])
#     ]


    @api.constrains('qty')
    def _check_qty(self):
        if self.tbill_ids.status not in ['wait_boss','wait_prjm','wait_approvers','pick','ready'] or self.status != False:
            for record in self:
                if record.qty <= 0:
                    raise ValidationError("กรุณาระบุจำนวนในรายละเอียดสินค้าให้ถูกต้อง(จำนวนต้องไม่น้อยกว่าหรือเท่ากับศูนย์)")
                
                
    @api.one
    @api.onchange('matno')
    @api.depends('matno')
    def _get_inv_b(self):
        self.inv_b = self.tbill_ids.inv_b
            

    @api.one
    @api.onchange('matno')
    @api.depends('matno')
    def _get_inv_p(self):
        self.inv_p = self.tbill_ids.inv_p
        
        
    @api.one
    @api.onchange('matno')
    @api.depends('matno')
    def _get_inv_a(self):
        self.inv_a = self.tbill_ids.inv_a
        
        
    @api.one
    @api.onchange('matno')
    @api.depends('matno')
    def _get_inv_k(self):
        self.inv_k = self.tbill_ids.inv_k
        
        
    @api.one
    @api.onchange('matno')
    @api.depends('matno')
    def _get_inv_r(self):
        self.inv_r = self.tbill_ids.inv_r
        
        
    @api.one
    @api.onchange('matno')
    @api.depends('matno')
    def _set_unitprice(self):
        self.unitprice = self.matno.unitprice
                
                
    @api.one
    @api.depends('qty_res','tbill_ids')
    @api.onchange('qty_res','tbill_ids')
    def check_qty_equal(self):
        if self.status != 'success':
            if self.qty_res == self.qty:
                self.return_stock = True
            else:
                self.return_stock = False
                
                
    @api.one
    @api.depends('qty_res','tbill_ids')
    @api.onchange('qty_res','tbill_ids')
    def check_qty_more(self):
        self.cut_stock = False


    def _set_dup_tb(self, cr, uid, ids, context=None):
        getbill_rec = self.pool.get('nstda.bst.dbill').search(cr, uid, [('hbill_ids', '=', context['bst_id'])], context=context)
         
        for mat_bill in self.pool.get('nstda.bst.dbill').browse(cr, uid, getbill_rec):
            mat_bill.tbill_ids = mat_bill.hbill_ids
    
    
    def _set_res_tb(self, cr, uid, ids, context=None):
        getbill_rec = self.pool.get('nstda.bst.dbill').search(cr, uid, [('hbill_ids', '=', context['bst_id'])], context=context)
         
        for mat_bill in self.pool.get('nstda.bst.dbill').browse(cr, uid, getbill_rec):
            mat_bill.sum = mat_bill.qty * mat_bill.unitprice
            mat_bill.sum_res = mat_bill.qty_res * mat_bill.unitprice

       
    @api.one
    @api.onchange('qty','matno')
    @api.depends('qty','matno')
    def _set_sum(self):
        self.sum  = self.unitprice * self.qty


    @api.one
    @api.depends('sum','tbill_ids')
    @api.onchange('sum','tbill_ids')
    def _set_discount(self):
        if(self.dbill_discount):
            discount_value = ((self.qty_res * self.unitprice) * self.dbill_discount)/100
            self.dbill_discount_sum = (self.qty_res * self.unitprice) - discount_value
        else:
            self.dbill_discount = 0
            self.dbill_discount_sum = (self.qty_res * self.unitprice)


    @api.one
    @api.depends('qty_res','tbill_ids')
    @api.onchange('qty_res','tbill_ids')
    def _set_sum_res(self):
        self.sum_res  = self.qty_res * self.unitprice
        
        
#     def _dbill_cut_success(self, cr, uid, ids, context=None):
#         getbill_rec = self.pool.get('nstda.bst.dbill').search(cr, uid, [('tbill_ids', '=', ids)], context=context)
#         
#         for dbill in self.pool.get('nstda.bst.dbill').browse(cr, uid, ids):
#             find_dbill = self.pool.get('nstda.bst.dbill').browse(cr, uid, dbill.id)
#             find_dbill.cut_stock = True
#         
#         
#     def _dbill_return_success(self, cr, uid, ids, context=None):
#         getbill_rec = self.pool.get('nstda.bst.dbill').search(cr, uid, [('tbill_ids', '=', ids)], context=context)
#         
#         for dbill in self.pool.get('nstda.bst.dbill').browse(cr, uid, ids):
#             find_dbill = self.pool.get('nstda.bst.dbill').browse(cr, uid, dbill.id)
#             find_dbill.return_stock = True
        
       
    @api.multi
    @api.onchange('matno','qty')
    def _onchange_qty(self):
        res = {}
        neg = {}
        
        if self.matno.id != False:
            if self.qty > self.balance:
                res = {'warning': {
                    'title': _('Warning'),
                    'message': _('จำนวนสินค้าในสต็อกไม่เพียงพอ')
                },
                 'value':False }
            if res:
                self.qty = 0
                return res
              
            if self.qty < 0:
                neg = {'warning': {
                    'title': _('Warning'),
                    'message': _('กรุณาระบุจำนวนให้ถูกต้อง(จำนวนต้องไม่น้อยกว่าหรือเท่ากับศูนย์)')
                },
                 'value':False }
            if neg:
                self.qty = 0
                return neg
        
        
    @api.multi
    @api.onchange('qty_res','sum_res')      
    def _onchange_qty_res(self):
        res = {}
        limit = {}
        neg = {}
    
        if self.matno.id != False:
            if self.qty_res > self.balance:
                res = {'warning': {
                    'title': _('Warning'),
                    'message': _('จำนวนสินค้าในสต็อกไม่เพียงพอ')
                },
                 'value':False }
            if res:
                self.qty_res = 0
                return res
              
            if self.qty_res < 0:
                neg = {'warning': {
                    'title': _('Warning'),
                    'message': _('กรุณาระบุจำนวนให้ถูกต้อง')
                },
                 'value':False }
            if neg:
                self.qty_res = 0
                return neg
            
            self.hbill_ids = self.tbill_ids
