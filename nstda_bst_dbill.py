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
    tbill_ids = fields.Many2one('nstda.bst.hbill','รายละเอียดสินค้า')

    qty = fields.Integer('จำนวนที่ต้องการ', required=False)
    sum = fields.Float(string="ราคารวม", store=True, compute='_set_sum')
    qty_res = fields.Integer('จำนวนที่ต้องการ', store=True, readonly=False)
    sum_res = fields.Float(string="ราคารวม", store=True, compute='_set_sum_res')
    cut_stock = fields.Boolean('ตัดสต็อกสำเร็จ', store=True, default=False)
    dbill_discount_sum = fields.Float(string="ราคารวม(ส่วนลด)", store=True, compute='_set_discount')
    
    matdesc = fields.Char('รายละเอียดสินค้า', readonly=True, related='matno.matdesc') 
    balance = fields.Integer('จำนวนคงเหลือ', readonly=True, store=False, related='matno.qty')
    unitprice = fields.Float('ราคา/ชิ้น', readonly=True, store=True, related='matno.unitprice')
    currency = fields.Char('สกุลเงิน', readonly=True, store=False, related='matno.currency')
    balance_rs = fields.Integer('จำนวนขอเบิกรออนุมัติ', readonly=True, related='matno.qty_res')
    uom = fields.Char('หน่วยนับ', readonly=True, store=True, related='matno.uom')
    uom_1 = fields.Char('หน่วยนับ', readonly=True, store=False, related='uom')
    uom_2 = fields.Char('หน่วยนับ', readonly=True, store=False, related='uom')

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
                               ('success', 'รับสินค้าแล้ว')], 'สถานะ', store=True, readonly=True, track_visibility='always', compute='_get_state')

    inv_r = fields.Boolean('Check pick', store=False, readonly=True, compute='_get_inv')
    
#     _sql_constraints = [
#                         ('_check_qty', 'กรุณาระบุจำนวนในรายละเอียดสินค้าให้ถูกต้อง(จำนวนต้องไม่น้อยกว่าหรือเท่ากับศูนย์)', ['qty'])
#     ]


    @api.constrains('qty')
    def _check_qty(self):
        if self.hbill_ids.status not in ['pick','ready','success'] or self.status != False:
            for record in self:
                if record.qty <= 0:
                    raise ValidationError("กรุณาระบุจำนวนในรายละเอียดสินค้าให้ถูกต้อง(จำนวนต้องไม่น้อยกว่าหรือเท่ากับศูนย์)")

    
    @api.one
    @api.depends('hbill_ids.status','tbill_ids.status')
    @api.onchange('hbill_ids.status','tbill_ids.status')
    def _get_state(self):
        if(self.status) == False:
            if (self.hbill_ids):
                self.status = self.hbill_ids.status
            elif (self.tbill_ids):
                self.status = self.tbill_ids.status
        
        
    @api.one
    @api.onchange('status','tbill_ids')
    @api.depends('status','hbill_ids.inv_r','tbill_ids.inv_r')
    def _get_inv(self):
        if (self.hbill_ids.status):
            self.inv_r = self.hbill_ids.inv_r
        elif (self.tbill_ids.status):
            self.inv_r = self.tbill_ids.inv_r


#     @api.one
#     @api.depends('matno')
#     @api.onchange('matno')        
#     def _onchange_uom(self):
#         self.matdesc = self.matno.matdesc
#         self.unitprice = self.matno.unitprice
#         self.balance = self.matno.qty
#         self.uom = self.matno.uom
            
       
    @api.one
    @api.onchange('qty','matno')
    @api.depends('qty','matno')
    def _set_sum(self):
        self.sum  = self.unitprice * self.qty

            
    @api.one
    @api.onchange('sum_res')
    @api.depends('sum_res')
    def _set_discount(self):
        if self.dbill_discount == False:
            res = self.env['nstda.bst.discount'].search([],limit=1,order="id DESC")
            if(res.discount):
                self.dbill_discount = res.discount  
                discount_value = (self.sum_res * self.dbill_discount)/100
                self.dbill_discount_sum = self.sum_res - discount_value
            else:
                self.dbill_discount = 0
                self.dbill_discount_sum = self.sum_res


    @api.one
    @api.depends('qty_res','tbill_ids','tbill_ids.amount_after_t')
    @api.onchange('qty_res','tbill_ids')
    def _set_sum_res(self):
        self.sum_res  = self.qty_res * self.unitprice
        
        
#     def bst_dbill_success(self, cr, uid, ids, context=None):
       
       
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
            
            self.qty_res = self.qty
        
        
    @api.multi
    @api.onchange('qty_res','matno','sum_res')      
    def _onchange_qty_res(self):
        res = {}
        limit = {}
        neg = {}
        
        if self.tbill_ids.amount_after_t > self.tbill_ids.amount_before_approve:
            limit = {'warning': {
                'title': _('Warning'),
                'message': _('ไม่สามารถแก้ไขรายการเบิกได้ เนื่องจากจำนวนเงินสุทธิเกินวงเงินที่อนุมัติ')
            },
             'value':False }
        if limit:
            self.qty_res = 0
            return limit
              
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
    