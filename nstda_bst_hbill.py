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
import collections

# from openerp.tools.translate import _
# from email import _name
# from openerp import tools
# from openerp import SUPERUSER_ID

    
####################################################################################################


class nstda_bst_hbill(models.Model):
    
    
    @api.model
    def create(self, values):
        seq_code = "nstda.bst.hbill"
        values['docno'] = self.env['ir.sequence'].get(seq_code) or ''
        res_id = super(nstda_bst_hbill, self).create(values)
        return res_id


    def _needaction_count(self, cr, uid, domain=None, context=None):
        """ Get the number of actions uid has to perform. """
        dom = []
        if not domain:
            dom = self._needaction_domain_get(cr, uid, context=context)
        else:
            dom = domain
 
        if not dom:
            return 0
        res = self.search(cr, uid, (domain or []) + dom, limit=100, order='id DESC', context=context)
        return len(res)
        
        
    @api.one
    @api.depends('d_bill_ids','t_bill_ids')
    @api.onchange('d_bill_ids','t_bill_ids')
    def _compute_amount_rightside(self):
        if self.status == 'draft':
            self.amount_before_discount_right = sum((line.qty * line.unitprice) for line in self.d_bill_ids)
            self.discount_value_right = (self.amount_before_discount_right * self.discount) / 100
            self.amount_after_discount = self.amount_before_discount_right - self.discount_value_right
        else:
            self.amount_before_discount_right = sum((line.qty_res * line.unitprice) for line in self.t_bill_ids)
            self.discount_value_right = (self.amount_before_discount_right * self.discount) / 100
            self.amount_after_discount = self.amount_before_discount_right - self.discount_value_right
            
            
    @api.one
    @api.depends('d_bill_ids','t_bill_ids')
    @api.onchange('d_bill_ids','t_bill_ids')
    def _compute_amount_leftside(self):
        if self.status == 'draft':
            self.amount_before_discount = sum((line.qty * line.unitprice) for line in self.d_bill_ids)
            self.discount_value = (self.amount_before_discount * self.discount) / 100
            self.amount_before_approve = self.amount_before_discount - self.discount_value
        elif self.status in ['wait_boss','wait_prjm']:
            self.amount_before_discount = sum((line.qty_res * line.unitprice) for line in self.t_bill_ids)
            self.discount_value = (self.amount_before_discount * self.discount) / 100
            self.amount_before_approve = self.amount_before_discount - self.discount_value
        else:
            self.amount_before_discount = sum((line.qty * line.unitprice) for line in self.t_bill_ids)
            self.discount_value = (self.amount_before_discount * self.discount) / 100
            self.amount_before_approve = self.amount_before_discount - self.discount_value


    @api.one
    @api.depends('empid','costct_prjno_selection','prjno')
    @api.onchange('empid','costct_prjno_selection')
    def _set_prj_cct(self):
        try:
            if self.costct_prjno_selection == 'costct':
                self.costct = self.empid.emp_dpm_id.dpm_cct_id.id
            elif self.costct_prjno_selection == 'prjno':
                pjboss_obj = self.env['nstdamas.projectmember'].search([('prjm_prj_id','=',self.prjno.id),('prjm_position','=','00')]).prjm_emp_id
                self.costct = pjboss_obj.emp_dpm_id.dpm_cct_id.id
        except:
            pass

    
    @api.one
    @api.depends('costct')
    @api.onchange('costct')
    def _set_cct_group(self):
        self.cct_group = self.env['nstdamas.costcenter'].search([('id','=',self.empid.emp_dpm_id.dpm_cct_id.id)]).cct_groupcost
        
    
    @api.one
    @api.depends('costct','prjno')
    def _set_prj_cct_name(self):
        if self.costct_prjno_selection == 'costct':
            self.prj_cct = self.costct.cct_id + ' - '  + self.costct.cct_name
        
        elif self.costct_prjno_selection == 'prjno':
            self.prj_cct = self.prjno.prj_name
            
            
    @api.one
    @api.depends('empid')
    def _set_emp_info(self):
        if(self.empid):
            self.emp_code = self.empid.emp_id
            self.emp_email = self.empid.emp_email
            self.empname = self.empid.emp_fname + ' ' + self.empid.emp_lname
            self.org = self.empid.emp_org_id
            self.division = self.empid.emp_dvs_id
            self.dept = self.empid.emp_dpm_id

            
    @api.one
    @api.depends('cr_user_id')
    def _set_create_user_info(self):
        if(self.cr_user_id):
            self.cr_user_name = self.cr_user_id.emp_fname + ' ' + self.cr_user_id.emp_lname
        
        
    @api.one
    @api.depends('boss_id')
    @api.onchange('boss_id')
    def _set_boss_info(self):
        if(self.boss_id):
            self.boss_emp_id = self.env['nstdamas.employee'].search([('emp_rusers_id','=',self.boss_id.id)]).id
            if(self.boss_emp_id):
                self.bossname = self.boss_emp_id.emp_fname + ' ' + self.boss_emp_id.emp_lname
            else:
                self.bossname = 'ไม่พบข้อมูล'
                
                
    @api.one
    @api.depends('prsd_id')
    @api.onchange('prsd_id')
    def _set_prsd_info(self):
        if(self.prsd_id):
            self.prsd_emp_id = self.env['nstdamas.employee'].search([('emp_rusers_id','=',self.prsd_id.id)]).id
            if(self.prsd_emp_id):
                self.prsdname = self.prsd_emp_id.emp_fname + ' ' + self.prsd_emp_id.emp_lname
            else:
                self.prsdname = 'ไม่พบข้อมูล'
        
        
    @api.one
    @api.depends('prjm_id')
    @api.onchange('prjm_id','costct')
    def _set_prjm_info(self):
        if(self.prjm_id):
            self.prjm_emp_id = self.env['nstdamas.employee'].search([('emp_rusers_id','=',self.prjm_id.id)]).id
            if(self.prjm_emp_id):
                self.prjmname = self.prjm_emp_id.emp_fname + ' ' + self.prjm_emp_id.emp_lname
            else:
                self.prjmname = 'ไม่พบข้อมูล'
        
        
    @api.one
    @api.depends('approver')
    @api.onchange('approver')
    def _set_approve_info(self):   
        if(self.approver):
            self.approver_id = self.env['nstdamas.employee'].search([('emp_rusers_id','=',self.approver.id)]).id
            if(self.approver_id):
                self.approvername = self.approver_id.emp_fname + ' ' + self.approver_id.emp_lname
            else:
                self.approvername = 'ไม่พบข้อมูล'
                
                
    @api.one
    @api.depends('bss_lv4_id')
    @api.onchange('bss_lv4_id')
    def _set_bss_lv4_info(self):
        if(self.bss_lv4_id):
            self.bss_lv4_emp_id = self.env['nstdamas.employee'].search([('emp_rusers_id','=',self.bss_lv4_id.id)]).id
            if(self.bss_lv4_emp_id):
                self.bss_lv4name = self.bss_lv4_emp_id.emp_fname + ' ' + self.bss_lv4_emp_id.emp_lname
            else:
                self.bss_lv4name = 'ไม่พบข้อมูล'
                
                
    @api.one
    @api.depends('bss_lv5_id')
    @api.onchange('bss_lv5_id')
    def _set_bss_lv5_info(self):
        if(self.bss_lv5_id):
            self.bss_lv5_emp_id = self.env['nstdamas.employee'].search([('emp_rusers_id','=',self.bss_lv5_id.id)]).id
            if(self.bss_lv5_emp_id):
                self.bss_lv5name = self.bss_lv5_emp_id.emp_fname + ' ' + self.bss_lv5_emp_id.emp_lname
            else:
                self.bss_lv5name = 'ไม่พบข้อมูล'
            
                
    @api.one
    @api.depends('bss_lv6_id')
    @api.onchange('bss_lv6_id')
    def _set_bss_lv6_info(self):
        if(self.bss_lv6_id):
            self.bss_lv6_emp_id = self.env['nstdamas.employee'].search([('emp_rusers_id','=',self.bss_lv6_id.id)]).id
            if(self.bss_lv6_emp_id):
                self.bss_lv6name = self.bss_lv6_emp_id.emp_fname + ' ' + self.bss_lv6_emp_id.emp_lname
            else:
                self.bss_lv6name = 'ไม่พบข้อมูล'
            
            
    @api.one
    @api.depends('pick_emp_id')
    def _set_pick_assign_emp(self):
        if(self.pick_emp_id):
            self.pick_emp_name = self.pick_emp_id.emp_fname + ' ' + self.pick_emp_id.emp_lname


    @api.one
    @api.depends('assign_emp_id')
    def _set_assign_emp(self):
        if(self.assign_emp_id):
            self.assign_emp_name = self.assign_emp_id.emp_fname + ' ' + self.assign_emp_id.emp_lname


    @api.one
    @api.depends('receive_emp_id')
    def _set_receive_emp(self):
        if(self.receive_emp_id):
            self.receive_emp_name = self.receive_emp_id.emp_fname + ' ' + self.receive_emp_id.emp_lname
            
            
    @api.one
    @api.onchange('cr_user_id','status')
    @api.depends('cr_user_id','status')
    def _check_prjm(self):
        if self.status == 'wait_prjm':
            if self.prjm_id.id == self._uid or self.env['res.users'].has_group('base.group_nstda_bst_authorities') or self.env['res.users'].has_group('base.group_nstda_bst_admin'):
                self.inv_p = True
            else:
                self.inv_p = False


    @api.one
    @api.onchange('cr_user_id','status')
    @api.depends('cr_user_id','status')
    def _check_boss(self):
        if self.status == 'wait_boss':
            if self.boss_id.id == self._uid or self.env['res.users'].has_group('base.group_nstda_bst_authorities') or self.env['res.users'].has_group('base.group_nstda_bst_admin'):
                self.inv_b = True
            else:
                self.inv_b = False


    @api.one
    @api.onchange('cr_user_id','status')
    @api.depends('cr_user_id','status')
    def _check_approver(self):
        if self.status == 'wait_approvers':
            if self.env['res.users'].has_group('base.group_nstda_bst_authorities') or self.env['res.users'].has_group('base.group_nstda_bst_admin'):
                self.inv_a = True
            else:
                self.inv_a = False


    @api.one
    @api.onchange('cr_user_id','status')
    @api.depends('cr_user_id','status')
    def _check_pick(self):
        if self.status == 'pick':
            if self.env['res.users'].has_group('base.group_nstda_bst_authorities') or self.env['res.users'].has_group('base.group_nstda_bst_admin'):
                self.inv_k = True
            else:
                self.inv_k = False
                
                
    @api.one
    @api.onchange('cr_user_id','status')
    @api.depends('cr_user_id','status')
    def _check_ready(self):
        if self.status == 'ready':
            if self.env['res.users'].has_group('base.group_nstda_bst_authorities') or self.env['res.users'].has_group('base.group_nstda_bst_admin'):
                self.inv_r = True
            else:
                self.inv_r = False


    @api.one
    @api.onchange('cr_user_id','status')
    @api.depends('cr_user_id','status')
    def _check_user(self):
        if self.status == 'draft':
            cr_user = self.cr_user_id.emp_rusers_id.id
            emp_user = self.empid.emp_rusers_id.id
            if cr_user == self._uid or emp_user == self._uid:
                self.inv_c = True
            else:
                self.inv_c = False


    @api.one
    @api.onchange('user_id')
    def _check_prj_member(self):
        user_id = self.env['nstdamas.employee'].search([('emp_rusers_id', '=', self._uid)]).id
        if self.costct_prjno_selection == 'prjno':
            pj_mem = self.env['nstdamas.projectmember'].search([('prjm_prj_id','=',self.prjno.id)])
            for emp in pj_mem:
                if emp.prjm_emp_id == user_id:
                    self.inv_j = True
                else:
                    self.inv_j = False
        else:
            self.inv_j = False
            
            
    @api.one
    @api.onchange('user_id')
    def _check_cct_member(self):
        user_id = self.env['nstdamas.employee'].search([('emp_rusers_id', '=', self._uid)])
        if self.costct_prjno_selection == 'costct':
            if (user_id):
                user_cct = user_id.emp_dpm_id.dpm_cct_id.id
                if self.costct.id == user_cct:
                    self.inv_t = True
                else:
                    self.inv_t = False
            else:
                self.inv_t = False

            
    @api.one
    @api.onchange('t_bill_ids','status')
    @api.depends('t_bill_ids','status')
    def _check_qty_less_than_stock(self):
        for v in self.t_bill_ids:
            if v.matno.qty - v.qty < 0:
                self.qty_check = False
            else:
                self.qty_check = True
                
                
    @api.constrains('amount_after_discount')
    def _check_amount_limit(self):
        if self.status not in ['draft','wait_boss','wait_prjm']:
            if self.amount_after_discount > self.amount_before_approve:
                raise ValidationError("ไม่สามารถแก้ไขรายการเบิกได้ เนื่องจากจำนวนเงินสุทธิเกินวงเงินที่อนุมัติ")
            

    _name = 'nstda.bst.hbill'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'docno DESC'
    _rec_name = 'docno'
    
    docno = fields.Char('เลขที่เอกสาร', size=10, readonly=True)
    empid = fields.Many2one('nstdamas.employee', 'พนักงานผู้เบิก', required=True, default=lambda self:self.env['nstdamas.employee'].search([('emp_rusers_id', '=', self._uid)]))
    emp_code = fields.Char('รหัสผู้เบิก', readonly=True, compute='_set_emp_info')
    empname = fields.Char('พนักงานผู้เบิก', readonly=True, compute='_set_emp_info')
    emp_email = fields.Char(string='Email', store=True, compute='_set_emp_info')
    cr_user_id = fields.Many2one('nstdamas.employee', 'พนักงานผู้บันทึก', readonly=True, required=True, default=lambda self:self.env['nstdamas.employee'].search([('emp_rusers_id', '=', self._uid)]))
    cr_user_name = fields.Char('ผู้บันทึก', readonly=True, compute='_set_create_user_info')
       
    prjm_id = fields.Many2one('res.users', 'หัวหน้าโครงการ', readonly=True)
    boss_id = fields.Many2one('res.users', 'ผู้อนุมัติเบิกจ่าย', readonly=True)
    prsd_id = fields.Many2one('res.users', 'ผู้อนุมัติ', readonly=True)
    approver = fields.Many2one('res.users', 'เจ้าหน้าที่ศูนย์หนังสือ', readonly=True)
    
    boss_emp_id = fields.Many2one('nstdamas.employee', 'ผู้อนุมัติเบิกจ่าย', readonly=True, store=False, compute='_set_boss_info')
    prjm_emp_id = fields.Many2one('nstdamas.employee', 'หัวหน้าโครงการ', readonly=True, store=False, compute='_set_prjm_info')
    prsd_emp_id = fields.Many2one('nstdamas.employee', 'ผู้อนุมัติ', readonly=True, store=False, compute='_set_prsd_info')
    approver_id = fields.Many2one('nstdamas.employee', 'เจ้าหน้าที่ศูนย์หนังสือ', readonly=True, compute='_set_approve_info')
    
    bossname = fields.Char('ผู้อนุมัติเบิกจ่าย', readonly=True, store=False, compute='_set_boss_info')
    prjmname = fields.Char('หัวหน้าโครงการ', readonly=True, store=False, compute='_set_prjm_info')
    prsdname = fields.Char('ผู้อนุมัติ', readonly=True, store=False, compute='_set_prsd_info')
    approvername = fields.Char('เจ้าหน้าที่ศูนย์หนังสือ', readonly=True, store=False, compute='_set_approve_info')
    
    bss_lv4_id = fields.Many2one('res.users', 'ผู้อนุมัติ', readonly=True)
    bss_lv5_id = fields.Many2one('res.users', 'ผู้อนุมัติ', readonly=True)
    bss_lv6_id = fields.Many2one('res.users', 'ผู้อนุมัติ', readonly=True)
    
    bss_lv4_emp_id = fields.Many2one('nstdamas.employee', 'ผู้อนุมัติ', readonly=True, store=False, compute='_set_bss_lv4_info')
    bss_lv5_emp_id = fields.Many2one('nstdamas.employee', 'ผู้อนุมัติ', readonly=True, store=False, compute='_set_bss_lv5_info')
    bss_lv6_epm_id = fields.Many2one('nstdamas.employee', 'ผู้อนุมัติ', readonly=True, store=False, compute='_set_bss_lv6_info')
    
    bss_lv4name = fields.Char('ผู้อนุมัติ', readonly=True, store=False, compute='_set_bss_lv4_info')
    bss_lv5name = fields.Char('ผู้อนุมัติ', readonly=True, store=False, compute='_set_bss_lv5_info')
    bss_lv6name = fields.Char('ผู้อนุมัติ', readonly=True, store=False, compute='_set_bss_lv6_info')

    org = fields.Many2one('nstdamas.org', 'ศูนย์ที่สังกัด', readonly=True, store=True, compute='_set_emp_info')
    division = fields.Many2one('nstdamas.division', 'ฝ่ายที่สังกัด', readonly=True, store=True, compute='_set_emp_info')
    dept = fields.Many2one('nstdamas.department', 'งานที่สังกัด', readonly=True, store=True, compute='_set_emp_info')
    costct_prjno_selection = fields.Selection([
                                               ('costct', 'หน่วยงาน'),
                                               ('prjno', 'โครงการ')], 'ประเภทเบิก', required=True)
    costct = fields.Many2one(
                             'nstdamas.costcenter',
                             'หน่วยงานที่เบิก', store=True, compute=_set_prj_cct)
    cct_group = fields.Char('cctgroup', compute=_set_cct_group)
    
    prjno = fields.Many2one('nstdamas.project', 'โครงการที่เบิก', domain=[('prj_end', '>=', datetime.now().strftime('%Y-%m-%d'))])
    prj_cct = fields.Char('หน่วยงาน/โครงการ', readonly=True, compute='_set_prj_cct_name', store=True)
    
    objdesc = fields.Text('วัตถุประสงค์ในการเบิก', required=True)
    
    pick_emp_id = fields.Many2one('nstdamas.employee', 'ผู้จัดเตรียมสินค้า', readonly=True)
    assign_emp_id = fields.Many2one('nstdamas.employee', 'ผู้จ่ายสินค้า', readonly=True)
    receive_emp_id = fields.Many2one('nstdamas.employee', 'ผู้รับสินค้า')
    pick_emp_name = fields.Char('ผู้จัดเตรียมสินค้า', readonly=True, compute='_set_pick_assign_emp')
    assign_emp_name = fields.Char('ผู้จ่ายสินค้า', readonly=True, compute='_set_assign_emp')
    receive_emp_name = fields.Char('ผู้รับสินค้า', readonly=True, compute='_set_receive_emp')
    
    book_date = fields.Datetime('วันที่ยืนยันการเบิก', readonly=True)
    boss_adate = fields.Datetime('วันที่อนุมัติเบิกจ่าย', readonly=True)
    prjm_adate = fields.Datetime('วันที่อนุมัติเบิกจ่าย', readonly=True)
    prsd_adate = fields.Datetime('วันที่อนุมัติ', readonly=True)
    approver_adate = fields.Datetime('วันที่เจ้าหน้าที่อนุมัติ', readonly=True)
    bss_lv4_adate = fields.Datetime('วันที่อนุมัติ', readonly=True)
    bss_lv5_adate = fields.Datetime('วันที่อนุมัติ', readonly=True)
    bss_lv6_adate = fields.Datetime('วันที่อนุมัติ', readonly=True)
    pick_date = fields.Datetime('วันที่เบิกสินค้า', readonly=True)
    post_date = fields.Datetime('วันที่ทำรายการสำเร็จ', readonly=True)
   
    icno_intf = fields.Char('เลขที่เอกสาร Internal Charge', readonly=True) 
    docno_intf = fields.Char('เลขที่เอกสารการตัด Stock', readonly=True)
    fiscalyear_docno_intf = fields.Char('ปีงบประมาณของเลขที่เอกสาร Internal Charge', readonly=True)
    fiscalyear_icno_intf = fields.Char('ปีงบประมาณของเลขที่เอกสารการตัด Stock', readonly=True)
    
    bst_quicknote = fields.Char('หมายเหตุ')
    bst_note = fields.Text('Note', track_visibility='onchange')
    bst_cancel_uid = fields.Many2one('nstdamas.employee', 'Cancel', readonly=True, track_visibility='onchange')
    bst_cancel_date = fields.Datetime('Cancel Date')
    
    status = fields.Selection([('reject', 'ยกเลิก'),
                               ('draft', 'ร่าง'),
                               ('wait_prjm', 'รออนุมัติ'),
                               ('wait_boss', 'รออนุมัติ'),
                               ('wait_prsd', 'รออนุมัติ'),
                               ('wait_bss_lv4', 'LV4'),
                               ('wait_bss_lv5', 'LV5'),
                               ('wait_bss_lv6', 'LV6'),
                               ('wait_approvers', 'รอเบิก'),
                               ('pick', 'รอจัดเตรียมสินค้า'),
                               ('ready', 'รอรับสินค้า'),
                               ('success', 'รับสินค้าแล้ว')], 'สถานะ', default='draft')
    
    status_pj = fields.Selection([], 'สถานะ', related='status')
                  
    discount = fields.Float('ส่วนลด(%)', store=True, default=lambda self:self.env['nstda.bst.discount'].search([], limit=1, order="id DESC").discount) 

    discount_value = fields.Float('ส่วนลด', store=False, readonly=True, compute='_compute_amount_leftside')
    amount_before_discount = fields.Float(string='รวม', store=False, readonly=True, compute='_compute_amount_leftside')
    amount_before_approve = fields.Float(string='ยอดเบิกสุทธิ', store=True, readonly=True, compute='_compute_amount_leftside')   
    
    discount_value_right = fields.Float('ส่วนลด', store=False, readonly=True, compute='_compute_amount_rightside')
    amount_before_discount_right = fields.Float(string='รวม', store=False, readonly=True, compute='_compute_amount_rightside')
    amount_after_discount = fields.Float(string='ราคารวมสุทธิ', store=True, readonly=True, compute='_compute_amount_rightside')

    discount_t = fields.Float('ส่วนลด', store=False, related='discount_value')
    amount_before_t = fields.Float(string='รวม', store=False, readonly=True, related='amount_before_discount')
    amount_after_t = fields.Float(string='ราคารวมสุทธิ', store=False, readonly=True, related='amount_before_approve')
    
    d_bill_ids = fields.One2many('nstda.bst.dbill', 'hbill_ids', 'รายละเอียดสินค้า')
    t_bill_ids = fields.One2many('nstda.bst.dbill', 'tbill_ids', 'รายละเอียดสินค้า')
    
    qty_check = fields.Boolean('Check qty', readonly=True, compute='_check_qty_less_than_stock')
    should_reworkflow = fields.Boolean('is should reworkflow ?', readonly=True, compute='_is_should_reworkflow')
    is_success_sap = fields.Boolean('SAP to Odoo', default=False, store=True)
    is_mail_approved = fields.Boolean('Is mail approved', default=False)
    
    inv_c = fields.Boolean('Check user', readonly=True, compute='_check_user')
    inv_p = fields.Boolean('Check prjm', readonly=True, compute='_check_prjm')
    inv_b = fields.Boolean('Check boss', readonly=True, compute='_check_boss')
    inv_a = fields.Boolean('Check approver', readonly=True, compute='_check_approver')
    inv_k = fields.Boolean('Check pick', readonly=True, compute='_check_pick')
    inv_r = fields.Boolean('Check ready', readonly=True, compute='_check_ready')
    inv_j = fields.Boolean('Check prj member', readonly=True, compute='_check_prj_member')
    inv_t = fields.Boolean('Check cct member', readonly=True, compute='_check_cct_member')

    
    @api.one
    def bst_sum_record(self):
        res = ""
        
        if self.t_bill_ids:
            for id in self.t_bill_ids:
                if id:
                    bid = str(id.id)
                    res += "nstda_bst_dbill.id=" + bid + " OR "
            res = res[:-4]
        else:
            raise Warning('ไม่สามารถทำรายการได้เนื่องจากไม่มีรายการสินค้า หรือรายละเอียดสินค้าไม่ถูกต้อง')
            
#         SOLUTION
#         $[id matno tbill_ids qty qty_res]
#         0[1  2     1         1   1      ]
#         1[2  2     1         2   1      ]
#         2[3  2     1         3   1      ]

#         RESULT
#         $[id matno tbill_ids qty qty_res flag]
#         0[1  2     1         6   3       1   ]
#         1[2  2     1         1   1       0   ]
#         2[3  2     1         1   1       0   ]

        if self.status == 'draft' :
            self.env.cr.execute("""
                UPDATE nstda_bst_dbill SET qty = t2.result, qty_res = t2.result
                FROM ( SELECT matno,tbill_ids,sum(qty) result 
                FROM nstda_bst_dbill t1 GROUP BY tbill_ids,matno) t2 
                WHERE ( nstda_bst_dbill.tbill_ids = t2.tbill_ids 
                AND nstda_bst_dbill.matno = t2.matno )
                AND ( %s ); 
                """ % res)
            self.env.cr.execute("""
                DELETE FROM nstda_bst_dbill 
                WHERE id IN ( SELECT id FROM nstda_bst_dbill y1 
                WHERE EXISTS ( SELECT * FROM nstda_bst_dbill y2 
                WHERE y1.matno = y2.matno 
                AND y1.qty = y2.qty 
                AND y1.tbill_ids = y2.tbill_ids 
                AND y1.id < y2.id
                AND ( %s ))); 
                """ % res)
             
        elif self.status in ['wait_boss','wait_prjm','wait_prsd']:
            self.env.cr.execute("""
                UPDATE nstda_bst_dbill SET qty = t2.result, qty_res = t2.result
                FROM ( SELECT matno,tbill_ids,sum(qty_res) result 
                FROM nstda_bst_dbill t1 GROUP BY tbill_ids,matno) t2 
                WHERE ( nstda_bst_dbill.tbill_ids = t2.tbill_ids 
                AND nstda_bst_dbill.matno = t2.matno )
                AND ( %s ); 
                """ % res)
            self.env.cr.execute("""
                DELETE FROM nstda_bst_dbill 
                WHERE id IN ( SELECT id FROM nstda_bst_dbill y1 
                WHERE EXISTS ( SELECT * FROM nstda_bst_dbill y2 
                WHERE y1.matno = y2.matno 
                AND y1.qty_res = y2.qty_res 
                AND y1.tbill_ids = y2.tbill_ids 
                AND y1.id < y2.id
                AND ( %s ))); 
                """ % res)
               
        else:
            self.env.cr.execute("""
                UPDATE nstda_bst_dbill SET qty = t2.result, qty_res = t2.result_res
                FROM ( SELECT matno,tbill_ids,sum(qty) result,sum(qty_res) result_res
                FROM nstda_bst_dbill t1 GROUP BY tbill_ids,matno) t2 
                WHERE ( nstda_bst_dbill.tbill_ids = t2.tbill_ids 
                AND nstda_bst_dbill.matno = t2.matno )
                AND ( %s ); 
                """ % res)
            self.env.cr.execute("""
                DELETE FROM nstda_bst_dbill 
                WHERE id IN ( SELECT id FROM nstda_bst_dbill y1 
                WHERE EXISTS ( SELECT * FROM nstda_bst_dbill y2 
                WHERE y1.matno = y2.matno 
                AND y1.qty_res = y2.qty_res 
                AND y1.tbill_ids = y2.tbill_ids 
                AND y1.id > y2.id
                AND ( %s )));
                """ % res)
            
            
    @api.one
    @api.onchange('prjm_id','boss_id','prsd_id','bss_lv4_id','bss_lv5_id','bss_lv6_id')
    @api.depends('prjm_id','boss_id','prsd_id','bss_lv4_id','bss_lv5_id','bss_lv6_id')
    def _is_should_reworkflow(self):
        if self.status != 'success':
            if self.costct_prjno_selection == 'costct':
                if  self.boss_id or self.prsd_id or self.bss_lv4_id or self.bss_lv5_id or self.bss_lv6_id == None:
                    self.should_reworkflow = True
                else:
                    self.should_reworkflow = False
            elif self.costct_prjno_selection == 'prjno':
                if  self.prjm_id or self.prsd_id or self.boss_id or self.bss_lv4_id or self.bss_lv5_id or self.bss_lv6_id == None:
                    self.should_reworkflow = True
                else:
                    self.should_reworkflow = False
        else:
            self.should_reworkflow = False
            
            
    @api.one
    def cct_boss_level(self):
        get_bosslevel = self.env['nstda.bst.bosslevel']
        get_mas_boss = self.env['nstdamas.boss']
        min_boss_lv = self.env['nstda.bst.bosslevel'].search([], limit=1, order="approve_amount ASC").approve_amount
        max_amount = self.env['nstda.bst.bosslevel'].search([], limit=1, order="start_amount DESC").start_amount
        
        try:
            max_amount = self.env['nstda.bst.bosslevel'].search([], limit=1, order="start_amount DESC").start_amount
            
            if self.amount_before_approve >= max_amount:
                level = 6
            else:
                get_lv = get_bosslevel.search([('start_amount','<=',self.amount_before_approve),('approve_amount','>=',self.amount_before_approve)], order="boss_level ASC")
                for find in get_lv:
                    bss = get_mas_boss.search([('bss_level','=',find.boss_level),('bss_emp_id','=',self.empid.id)])
                    if (bss.bss_id):
                        level = find.boss_level
            
            boss_must_approve = get_mas_boss.search([('bss_level','<=',level),('bss_emp_id','=',self.empid.id),('bss_level','!=','0')])
            
            for set in boss_must_approve:
                if set.bss_level == '1':
                    if set.bss_id.id != False:
                        self.boss_id = set.bss_id.emp_rusers_id.id
                    else:
                        find_next = int(set.bss_level) + 1
                        next_boss = get_mas_boss.search([('bss_level','=',str(find_next)),('bss_emp_id','=',self.empid.id)])
                        self.boss_id = next_boss.bss_id.emp_rusers_id.id
                if set.bss_level == '2':
                    if set.bss_id.id != False:
                        self.prsd_id = set.bss_id.emp_rusers_id.id
                    else:
                        find_next = int(set.bss_level) + 2
                        next_boss = get_mas_boss.search([('bss_level','=',str(find_next)),('bss_emp_id','=',self.empid.id)])
                        self.prsd_id = next_boss.bss_id.emp_rusers_id.id
                if set.bss_level == '3':
                    if set.bss_id.id != False and self.prsd_id.id != False:
                        self.prsd_id = set.bss_id.emp_rusers_id.id
                    elif set.bss_id.id == False and self.prsd_id.id == False:
                        find_next = int(set.bss_level) + 1
                        next_boss = get_mas_boss.search([('bss_level','=',str(find_next)),('bss_emp_id','=',self.empid.id)])
                        self.prsd_id = next_boss.bss_id.emp_rusers_id.id
                if set.bss_level == '4':
                    if set.bss_id.id != False:
                        self.bss_lv4_id = set.bss_id.emp_rusers_id.id
                    else:
                        find_next = int(set.bss_level) + 1
                        next_boss = get_mas_boss.search([('bss_level','=',str(find_next)),('bss_emp_id','=',self.empid.id)])
                        self.bss_lv4_id = next_boss.bss_id.emp_rusers_id.id
                if set.bss_level == '5':
                    if set.bss_id.id != False:
                        self.bss_lv5_id = set.bss_id.emp_rusers_id.id
                    else:
                        find_next = int(set.bss_level) + 1
                        next_boss = get_mas_boss.search([('bss_level','=',str(find_next)),('bss_emp_id','=',self.empid.id)])
                        self.bss_lv5_id = next_boss.bss_id.emp_rusers_id.id
                if set.bss_level == '6':
                    if set.bss_id.id != False:
                        self.bss_lv6_id = set.bss_id.emp_rusers_id.id
                    else:
                        self.should_reworkflow = True
                        raise Warning('ไม่สามารถทำรายการต่อได้ เนื่องจากไม่พบข้อมูลผู้บังคับบัญชา')
        except:
            raise Warning('ไม่สามารถทำรายการต่อได้ เนื่องจากไม่พบข้อมูลผู้บังคับบัญชาของท่าน')

        
    @api.one
    def prj_boss_level(self):
        get_bosslevel = self.env['nstda.bst.bosslevel']
        get_mas_boss = self.env['nstdamas.boss']
        min_boss_lv = self.env['nstda.bst.bosslevel'].search([], limit=1, order="approve_amount ASC").approve_amount
        max_amount = self.env['nstda.bst.bosslevel'].search([], limit=1, order="start_amount DESC").start_amount
        
        try:
            project_id = self.prjno.id
            pjboss_obj = self.env['nstdamas.projectmember'].search([('prjm_prj_id','=',project_id),('prjm_position','=','00')]).prjm_emp_id.id
            if pjboss_obj == False:
                self.env.cr.execute("SELECT prjm_emp_id FROM nstdamas_projectmember WHERE prjm_prj_id = " + str(project_id) + " AND prjm_position = '00'")
                pjboss_obj = self.env.cr.fetchone()[0]
            get_prjm_id = self.env['nstdamas.employee'].search([['id', '=', pjboss_obj]]).emp_rusers_id.id
            self.prjm_id = get_prjm_id
            
            if self.amount_before_approve >= max_amount:
                level = 6
            else:
                get_lv = get_bosslevel.search([('start_amount','<=',self.amount_before_approve),('approve_amount','>=',self.amount_before_approve)], order="boss_level ASC")
                for find in get_lv:
                    bss = get_mas_boss.search([('bss_level','=',find.boss_level),('bss_emp_id','=',self.prjm_id.id)])
                    if (bss.bss_id):
                        level = find.boss_level
                        
            boss_must_approve = get_mas_boss.search([('bss_level','<=',level),('bss_emp_id','=',pjboss_obj),('bss_level','!=','0')])
            
            for set in boss_must_approve:
                if set.bss_level == '1':
                    try:
                        list_boss = self.env['nstdamas.boss'].get_boss(pjboss_obj)
                        i = 0
                        while True:
                            if list_boss[i].bss_id.id != False:
                                boss_id = list_boss[i].bss_id.emp_rusers_id.id
                                break
                            i += 1
                            if i == 5:
                                break
                        self.boss_id = boss_id
                    except:
                        raise Warning('ไม่สามารถทำรายการต่อได้ เนื่องจากไม่พบข้อมูลผู้บังคับบัญชาของท่าน')
                if set.bss_level == '2':
                    if set.bss_id.id != False:
                        self.prsd_id = set.bss_id.emp_rusers_id.id
                    else:
                        find_next = int(set.bss_level) + 2
                        next_boss = get_mas_boss.search([('bss_level','=',str(find_next)),('bss_emp_id','=',pjboss_obj)])
                        self.prsd_id = next_boss.bss_id.emp_rusers_id.id
                if set.bss_level == '3':
                    if set.bss_id.id != False and self.prsd_id.id != False:
                        self.prsd_id = set.bss_id.emp_rusers_id.id
                    elif set.bss_id.id == False and self.prsd_id.id == False:
                        find_next = int(set.bss_level) + 1
                        next_boss = get_mas_boss.search([('bss_level','=',str(find_next)),('bss_emp_id','=',pjboss_obj)])
                        self.prsd_id = next_boss.bss_id.emp_rusers_id.id
                elif set.bss_level == '4':
                    if set.bss_id != None:
                        self.bss_lv4_id = set.bss_id.emp_rusers_id.id
                    else:
                        find_next = int(set.bss_level) + 1
                        next_boss = get_mas_boss.search([('bss_level','=',str(find_next)),('bss_emp_id','=',pjboss_obj)])
                        self.bss_lv4_id = next_boss.bss_id.emp_rusers_id.id
                elif set.bss_level == '5':
                    if set.bss_id != None:
                        self.bss_lv5_id = set.bss_id.emp_rusers_id.id
                    else:
                        find_next = int(set.bss_level) + 1
                        next_boss = get_mas_boss.search([('bss_level','=',str(find_next)),('bss_emp_id','=',pjboss_obj)])
                        self.bss_lv5_id = next_boss.bss_id.emp_rusers_id.id
                elif set.bss_level == '6':
                    if set.bss_id != None:
                        self.bss_lv6_id = set.bss_id.emp_rusers_id.id
                    else:
                        self.should_reworkflow = True
                        raise Warning('ไม่สามารถทำรายการต่อได้ เนื่องจากไม่พบข้อมูลผู้บังคับบัญชา')
        except:
            raise Warning('ไม่สามารถทำรายการต่อได้ เนื่องจากไม่พบข้อมูลผู้บังคับบัญชาของท่าน')
    
    
    @api.one
    def btn_send_request(self):
        
        if self.amount_before_approve > 0:
  
            for v in self.t_bill_ids:
                if v.matno.qty - v.qty < 0:
                    raise Warning('จำนวนสินค้าในสต็อกไม่เพียงพอ')
                      
                else:
                    
                    try:
                        self.bst_sum_record()
                    except:
                        raise Warning('ไม่สามารถทำรายการได้เนื่องจากไม่มีรายการสินค้า หรือรายละเอียดสินค้าไม่ถูกต้อง')
                        
                    if self.costct_prjno_selection == 'costct':
                        self.book_date = datetime.now()
                        self.cct_boss_level()
                        self.status = 'wait_boss'
                    
                    elif self.costct_prjno_selection == 'prjno':
                        self.book_date = datetime.now()
                        self.prj_boss_level()
                        self.status = 'wait_prjm'              
        else:
            raise Warning('ไม่สามารถทำรายการได้เนื่องจากไม่มีรายการสินค้า หรือรายละเอียดสินค้าไม่ถูกต้อง')
        

    @api.one
    def btn_prjm_submit(self):
        
        if self.amount_before_approve > 0:
            self.prj_boss_level()
            
            if self.inv_p == True:
                for v in self.t_bill_ids:
                    if v.matno.qty - v.qty < 0:
                        raise Warning('จำนวนสินค้าในสต็อกไม่เพียงพอ')
                    else:
                        
                        try:
                            self.bst_sum_record()
                        except:
                            raise Warning('ไม่สามารถทำรายการได้เนื่องจากไม่มีรายการสินค้า หรือรายละเอียดสินค้าไม่ถูกต้อง')
                        
                        self.boss_adate = datetime.now()
                        if (self.boss_id):
                            self.status = 'wait_boss'
                            self.prjm_adate = datetime.now()
                        else:
                            self.status = 'wait_approvers'
            else:
                raise Warning('สำหรับหัวหน้าโครงการอนุมัติ')
            
        else:
            raise Warning('ไม่สามารถทำรายการได้เนื่องจากไม่มีรายการสินค้า หรือรายละเอียดสินค้าไม่ถูกต้อง')
 
 
    @api.one
    def btn_boss_submit(self):
        
        if self.amount_before_approve > 0:
            if self.costct_prjno_selection == 'costct':
                self.cct_boss_level()
            elif self.costct_prjno_selection == 'prjno':
                self.prj_boss_level()
            
            if self.inv_b == True:
                for v in self.t_bill_ids:
                    if v.matno.qty - v.qty < 0:
                        raise Warning('จำนวนสินค้าในสต็อกไม่เพียงพอ')
                    else:
                        
                        try:
                            self.bst_sum_record()
                        except:
                            pass
                        
                        self.boss_adate = datetime.now()
                        if (self.prsd_id):
                            self.status = 'wait_prsd'
                        else:
                            self.status = 'wait_approvers'
            else:
                raise Warning('สำหรับผู้บังคับบัญชาอนุมัติ')
            
        else:
            raise Warning('ไม่สามารถทำรายการได้เนื่องจากไม่มีรายการสินค้า หรือรายละเอียดสินค้าไม่ถูกต้อง')


    @api.one    
    def btn_prsd_submit(self):
        if self.prsd_id.id == self._uid or self.env['res.users'].has_group('base.group_nstda_bst_authorities') or self.env['res.users'].has_group('base.group_nstda_bst_admin'):
            
            for v in self.t_bill_ids:
                if v.matno.qty - v.qty < 0:
                    raise Warning('จำนวนสินค้าในสต็อกไม่เพียงพอ')
                else:
                    
                    try:
                        self.bst_sum_record()
                    except:
                        pass
                    
                    self.prsd_adate = datetime.now()
                    if (self.bss_lv4_id):
                        self.status = 'wait_bss_lv4'
                    else:
                        self.status = 'wait_approvers'
                    
        else:
            raise Warning('สำหรับเจ้าหน้าที่อนุมัติ')


    @api.one    
    def btn_bss_lv4_submit(self):
        if self.bss_lv4_id.id == self._uid or self.env['res.users'].has_group('base.group_nstda_bst_authorities') or self.env['res.users'].has_group('base.group_nstda_bst_admin'):
            
            for v in self.t_bill_ids:
                if v.matno.qty - v.qty < 0:
                    raise Warning('จำนวนสินค้าในสต็อกไม่เพียงพอ')
                else:
                    self.bss_lv4_adate = datetime.now()
                    if (self.bss_lv5_id):
                        self.status = 'wait_bss_lv5'
                    else:
                        self.status = 'wait_approvers'
                    
        else:
            raise Warning('สำหรับผู้บังคับบัญชาอนุมัติ')
        
        
    @api.one    
    def btn_bss_lv5_submit(self):
        if self.bss_lv5_id.id == self._uid or self.env['res.users'].has_group('base.group_nstda_bst_authorities') or self.env['res.users'].has_group('base.group_nstda_bst_admin'):
            
            for v in self.t_bill_ids:
                if v.matno.qty - v.qty < 0:
                    raise Warning('จำนวนสินค้าในสต็อกไม่เพียงพอ')
                else:
                    self.bss_lv5_adate = datetime.now()
                    if (self.bss_lv6_id):
                        self.status = 'wait_bss_lv6'
                    else:
                        self.status = 'wait_approvers'
                    
        else:
            raise Warning('สำหรับผู้บังคับบัญชาอนุมัติ')
        
        
    @api.one    
    def btn_bss_lv6_submit(self):
        if self.bss_lv6_id.id == self._uid or self.env['res.users'].has_group('base.group_nstda_bst_authorities') or self.env['res.users'].has_group('base.group_nstda_bst_admin'):
            
            for v in self.t_bill_ids:
                if v.matno.qty - v.qty < 0:
                    raise Warning('จำนวนสินค้าในสต็อกไม่เพียงพอ')
                else:
                    self.bss_lv6_adate = datetime.now()
                    self.status = 'wait_approvers'
                    
        else:
            raise Warning('สำหรับผู้บังคับบัญชาอนุมัติ')
  
  
    @api.one    
    def btn_approver_submit(self):
        if self.inv_a == True:
            
            for v in self.t_bill_ids:
                if v.matno.qty - v.qty < 0:
                    raise Warning('จำนวนสินค้าในสต็อกไม่เพียงพอ')
                else:
                    self.status = 'pick'
                    self.approver = self._uid
                    self.approver_adate = datetime.now()
                    
        else:
            raise Warning('สำหรับเจ้าหน้าที่อนุมัติ')
    
    
    @api.one     
    def btn_submit_pick(self):
        if self.inv_k == True:
            
            for v in self.t_bill_ids:
                if v.matno.qty - v.qty < 0:
                    raise Warning('จำนวนสินค้าในสต็อกไม่เพียงพอ')
                else:
                    self.status = 'ready'
                    self.pick_date = datetime.now()
                    self.pick_emp_id = self.env['nstdamas.employee'].search([('emp_rusers_id', '=', self._uid)]).id
            
        else:
            raise Warning('สำหรับเจ้าหน้าที่อนุมัติ')
        
        
    def submit_cut_stock(self, cr, uid, ids, context=None):
        self.pool.get('nstda.bst.stock')._cut_stock(cr, uid, context['bst_id'], context=context)
        
    
    def submit_return_stock(self, cr, uid, ids, context=None):
        self.pool.get('nstda.bst.stock')._return_stock(cr, uid, context['bst_id'], context=context)
        