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
    
    
#     @api.multi
#     def write(self, values):
#         res_id = super(nstda_bst_hbill, self).write(values)
#         return res_id


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


    def sendmail_alert(self, cr, uid, ids, context=None):
        env_refs = self.browse(cr, uid, ids)
        email_template_obj = self.pool.get('email.template')
        email_template_name = 'nstda_bst_mail_alert'
        template_ids = email_template_obj.search(cr, uid, [('model_id.model','=','nstda.bst.hbill'), ('name','=',email_template_name)], context=context)
        if template_ids:
            values = email_template_obj.generate_email(cr, uid, template_ids[0], env_refs.id, context=context)
            
            values['body_html'] = values['body_html'].replace("{to}", env_refs.empid.emp_email)
            
            mail_mail_obj = self.pool.get('mail.mail')
            uid = 1
            msg_id = mail_mail_obj.create(cr, uid, values, context=context)
            if msg_id:
                mail_mail_obj.send(cr, uid, [msg_id], context=context)
                self.write(cr, uid, env_refs.id, {'is_mail_approved':True}, context=context)
        return True
    
    
    def sendmail_approve(self, cr, uid, ids, context=None):
        env_refs = self.browse(cr, uid, ids)
        email_template_obj = self.pool.get('email.template')
        email_template_name = 'nstda_bst_mail_approval'
        template_ids = email_template_obj.search(cr, uid, [('model_id.model','=','nstda.bst.hbill'), ('name','=',email_template_name)], context=context)
        if template_ids:
            values = email_template_obj.generate_email(cr, uid, template_ids[0], env_refs.id, context=context)
            
            url_rec = str(request.httprequest.host_url) + ':8069/web#id=' + str(env_refs.id) + '&model=nstda.bst.hbill'
            
            values['body_html'] = values['body_html'].replace("{to}", env_refs.boss_emp_id.emp_email)
            values['body_html'] = values['body_html'].replace("{dear}", env_refs.bossname)
            values['body_html'] = values['body_html'].replace("{bst_id}", url_rec)
            
            mail_mail_obj = self.pool.get('mail.mail')
            uid = 1
            msg_id = mail_mail_obj.create(cr, uid, values, context=context)
            if msg_id:
                mail_mail_obj.send(cr, uid, [msg_id], context=context)
                self.write(cr, uid, env_refs.id, {'is_mail_approved':True}, context=context)
        return True
    
    
    @api.one
    @api.depends('d_bill_ids')
    def _set_discount(self):
        if self.discount == False :
            res = self.env['nstda.bst.discount'].search([], limit=1, order="id DESC")
            if(res.discount):
                self.discount = res.discount       
            else:
                self.discount = 0
        
        
    @api.one
    @api.depends('d_bill_ids')
    @api.onchange('d_bill_ids')
    def _compute_amount_right(self):
        self.amount_before_discount_right = sum((line.qty * line.unitprice) for line in self.d_bill_ids)
        self.discount_value_right = (self.amount_before_discount_right * self.discount) / 100
        self.amount_after_discount = self.amount_before_discount_right - self.discount_value_right
            
            
    @api.one
    @api.depends('t_bill_ids')
    @api.onchange('t_bill_ids')
    def _compute_amount_last(self):
        self.amount_before_t = sum((line.qty_res * line.unitprice) for line in self.t_bill_ids)
        self.discount_t = (self.amount_before_t * self.discount) / 100
        self.amount_after_t = self.amount_before_t - self.discount_t


    @api.one
    @api.depends('empid','costct_prjno_selection')
    @api.onchange('empid','costct_prjno_selection')
    def _set_prj_cct(self):
        try:
            if self.costct_prjno_selection == 'costct':
                self.costct = self.empid.emp_dpm_id.dpm_cct_id.id
        except:
            pass
        
        
    @api.one
    @api.depends('prjm_emp_id')
    @api.onchange('prjm_emp_id')
    def _set_prjm_cct(self):
        try:
            if self.costct_prjno_selection == 'prjno':
                self.costct = self.prjm_emp_id.emp_dpm_id.dpm_cct_id.id
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
    def _set_cr_info(self):
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
    @api.depends('prjm_id')
    @api.onchange('prjm_id')
    def _set_prjm_info(self):
        if(self.prjm_id):
            self.prjm_emp_id = self.env['nstdamas.employee'].search([('emp_rusers_id','=',self.prjm_id.id)]).id
            
            self._set_prjm_cct()
            
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
    def _inv_p(self):
        if self.status == 'wait_prjm':
            if self.prjm_id.id == self._uid or self.env['res.users'].has_group('base.group_nstda_bst_authorities') or self.env['res.users'].has_group('base.group_nstda_bst_admin'):
                self.inv_p = True
            else:
                self.inv_p = False
#         if self._uid == 1:
#             self.inv_p = True


    @api.one
    @api.onchange('cr_user_id','status')
    @api.depends('cr_user_id','status')
    def _inv_b(self):
        if self.status == 'wait_boss':
            if self.boss_id.id == self._uid or self.env['res.users'].has_group('base.group_nstda_bst_authorities') or self.env['res.users'].has_group('base.group_nstda_bst_admin'):
                self.inv_b = True
            else:
                self.inv_b = False
#         if self._uid == 1:
#             self.inv_b = True


    @api.one
    @api.onchange('cr_user_id','status')
    @api.depends('cr_user_id','status')
    def _inv_a(self):
        if self.status == 'wait_approvers':
            if self.env['res.users'].has_group('base.group_nstda_bst_authorities') or self.env['res.users'].has_group('base.group_nstda_bst_admin'):
                self.inv_a = True
            else:
                self.inv_a = False


    @api.one
    @api.onchange('cr_user_id','status')
    @api.depends('cr_user_id','status')
    def _inv_k(self):
        if self.status == 'pick':
            if self.env['res.users'].has_group('base.group_nstda_bst_authorities') or self.env['res.users'].has_group('base.group_nstda_bst_admin'):
                self.inv_k = True
            else:
                self.inv_k = False
                
                
    @api.one
    @api.onchange('cr_user_id','status')
    @api.depends('cr_user_id','status')
    def _inv_r(self):
        if self.status == 'ready':
            if self.env['res.users'].has_group('base.group_nstda_bst_authorities') or self.env['res.users'].has_group('base.group_nstda_bst_admin'):
                self.inv_r = True
            else:
                self.inv_r = False


    @api.one
    @api.onchange('cr_user_id','status')
    @api.depends('cr_user_id','status')
    def _inv_c(self):
        if self.status == 'draft' or self.status == 'edit':
            cr_user = self.cr_user_id.emp_rusers_id.id
            emp_user = self.empid.emp_rusers_id.id
            if cr_user == self._uid or emp_user == self._uid:
                self.inv_c = True
            else:
                self.inv_c = False
                
    @api.one
    @api.depends('status')
    @api.onchange('status')
    def _set_db_state(self):
        self.env['nstda.bst.dbill']._get_state()

            
    @api.one
    @api.onchange('d_bill_ids','status')
    @api.depends('d_bill_ids','status')
    def _check(self):
        for v in self.d_bill_ids:
            if v.matno.qty - v.qty < 0:
                self.qty_check = False
            else:
                self.qty_check = True
            

    _name = 'nstda.bst.hbill'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'docno DESC'
    _rec_name = 'docno'
    
    docno = fields.Char('เลขที่เอกสาร', size=10, readonly=True)
    empid = fields.Many2one('nstdamas.employee', 'พนักงานผู้เบิก', required=True, default=lambda self:self.env['nstdamas.employee'].search([('emp_rusers_id', '=', self._uid)]))   
    prjm_id = fields.Many2one('res.users', 'หัวหน้าโครงการ', readonly=True)
    boss_id = fields.Many2one('res.users', 'ผู้อนุมัติ', readonly=True)
    approver = fields.Many2one('res.users', 'เจ้าหน้าที่ศูนย์หนังสือ', readonly=True)

    emp_code = fields.Char('รหัสผู้เบิก', readonly=True, compute='_set_emp_info')
    empname = fields.Char('พนักงานผู้เบิก', readonly=True, compute='_set_emp_info')
    
    boss_emp_id = fields.Many2one('nstdamas.employee', 'ผู้อนุมัติเบิกจ่าย', readonly=True, store=False, compute='_set_boss_info')
    prjm_emp_id = fields.Many2one('nstdamas.employee', 'หัวหน้าโครงการ', readonly=True, store=False, compute='_set_prjm_info')
    approver_id = fields.Many2one('nstdamas.employee', 'เจ้าหน้าที่ศูนย์หนังสือ', readonly=True, compute='_set_approve_info')
    bossname = fields.Char('ผู้อนุมัติ', readonly=True, store=False, compute='_set_boss_info')
    prjmname = fields.Char('ผู้อนุมัติ', readonly=True, store=False, compute='_set_prjm_info')
    approvername = fields.Char('เจ้าหน้าที่ศูนย์หนังสือ', readonly=True, store=False, compute='_set_approve_info')
    
    cr_user_id = fields.Many2one('nstdamas.employee', 'พนักงานผู้บันทึก', readonly=True, required=True, default=lambda self:self.env['nstdamas.employee'].search([('emp_rusers_id', '=', self._uid)]))
    cr_user_name = fields.Char('ผู้บันทึก', readonly=True, compute='_set_cr_info')

    org = fields.Many2one('nstdamas.org', 'ศูนย์ที่สังกัด', readonly=True, store=True, compute='_set_emp_info')
    division = fields.Many2one('nstdamas.division', 'ฝ่ายที่สังกัด', readonly=True, store=True, compute='_set_emp_info')
    dept = fields.Many2one('nstdamas.department', 'งานที่สังกัด', readonly=True, store=True, compute='_set_emp_info')
    costct_prjno_selection = fields.Selection([
                                               ('costct', 'หน่วยงาน'),
                                               ('prjno', 'โครงการ')], 'ประเภทเบิก', required=True)
    costct = fields.Many2one(
                             'nstdamas.costcenter',
                             'หน่วยงานที่เบิก', default=_set_prj_cct)
    cct_group = fields.Char('cctgroup', compute=_set_cct_group)
    
    prjno = fields.Many2one('nstdamas.project', 'โครงการที่เบิก', domain=[('prj_end', '>=', datetime.now().strftime('%Y-%m-%d'))])
    objdesc = fields.Text('วัตถุประสงค์ในการเบิก', required=True)
    dbill_desc = fields.Char('จำนวน', readonly=True)
    prj_cct = fields.Char('หน่วยงาน/โครงการ', readonly=True, compute='_set_prj_cct_name', store=True)
    
    pick_emp_id = fields.Many2one('nstdamas.employee', 'ผู้จัดเตรียมสินค้า', readonly=True)
    assign_emp_id = fields.Many2one('nstdamas.employee', 'ผู้จ่ายสินค้า', readonly=True)
    receive_emp_id = fields.Many2one('nstdamas.employee', 'ผู้รับสินค้า')
    pick_emp_name = fields.Char('ผู้จัดเตรียมสินค้า', readonly=True, compute='_set_pick_assign_emp')
    assign_emp_name = fields.Char('ผู้จ่ายสินค้า', readonly=True, compute='_set_assign_emp')
    receive_emp_name = fields.Char('ผู้รับสินค้า', readonly=True, compute='_set_receive_emp')
    
    book_date = fields.Datetime('วันที่ยืนยันการเบิก', readonly=True)
    boss_adate = fields.Datetime('วันที่อนุมัติเบิกจ่าย', readonly=True)
    adate = fields.Datetime('วันที่เจ้าหน้าที่อนุมัติ', readonly=True)
    pick_date = fields.Datetime('วันที่เบิกสินค้า', readonly=True)
    post_date = fields.Datetime('วันที่ทำรายการสำเร็จ', readonly=True)
    
    docno_intf = fields.Char('เลขที่เอกสารการตัด Stock')
    fiscalyear_docno_intf = fields.Char('ปีงบประมาณของเลขที่เอกสาร Internal Charge')
    icno_intf = fields.Char('เลขที่เอกสาร Internal Charge')
    fiscalyear_icno_intf = fields.Char('ปีงบประมาณของเลขที่เอกสารการตัด Stock')
    is_success_sap = fields.Boolean('SAP to Odoo', default=False, store=True)
    
    emp_email = fields.Char(string='Email', store=True, compute='_set_emp_info')
    is_mail_approved = fields.Boolean('Is mail approved', default=False)
    bst_note = fields.Text('Note', track_visibility='onchange')
    bst_cancel_uid = fields.Many2one('nstdamas.employee', 'Cancel', readonly=True, track_visibility='onchange')
    bst_cancel_date = fields.Datetime('Cancel Date')
    
    status = fields.Selection([('reject', 'ยกเลิก'),
                               ('draft', 'ร่าง'),
                               ('wait_prjm', 'รออนุมัติ'),
                               ('wait_boss', 'รออนุมัติ'),
                               ('wait_approvers', 'รอเบิก'),
                               ('pick', 'รอจัดเตรียมสินค้า'),
                               ('ready', 'รอรับสินค้า'),
                               ('success', 'รับสินค้าแล้ว')], 'สถานะ', default='draft')
                  
    discount = fields.Float('ส่วนลด(%)', store=True, compute='_set_discount') 
    
    discount_value = fields.Float('ส่วนลด', store=False, readonly=True, related='discount_value_right')
    amount_before_discount = fields.Float(string='รวม', store=False, readonly=True, related='amount_before_discount_right')
    amount_before_approve = fields.Float(string='ยอดเบิกสุทธิ', store=False, readonly=True, related='amount_after_discount')   
    
    discount_value_right = fields.Float('ส่วนลด', compute='_compute_amount_right')
    amount_before_discount_right = fields.Float(string='รวม', readonly=True, compute='_compute_amount_right',)
    amount_after_discount = fields.Float(string='ราคารวมสุทธิ', store=True, readonly=True, compute='_compute_amount_right')

    discount_t = fields.Float('ส่วนลด', store=False, compute='_compute_amount_last')
    amount_before_t = fields.Float(string='รวม', readonly=True, compute='_compute_amount_last',)
    amount_after_t = fields.Float(string='ราคารวมสุทธิ', store=False, readonly=True, compute='_compute_amount_last')
    
    d_bill_ids = fields.One2many('nstda.bst.dbill', 'hbill_ids', 'รายละเอียดสินค้า')
    t_bill_ids = fields.One2many('nstda.bst.dbill', 'tbill_ids', 'รายละเอียดสินค้า')
    
    qty_check = fields.Boolean('Check qty', readonly=True, compute='_check')
    
    inv_c = fields.Boolean('Check user', readonly=True, compute='_inv_c')
    inv_p = fields.Boolean('Check prjm', readonly=True, compute='_inv_p')
    inv_b = fields.Boolean('Check boss', readonly=True, compute='_inv_b')
    inv_a = fields.Boolean('Check approver', readonly=True, compute='_inv_a')
    inv_k = fields.Boolean('Check pick', readonly=True, compute='_inv_k')
    inv_r = fields.Boolean('Check ready', readonly=True, compute='_inv_r')

    
    @api.one
    def bst_sum_record(self):
        res = ""
        if self.d_bill_ids:
            for id in self.d_bill_ids:
                if id:
                    bid = str(id.id)
                    res += "nstda_bst_dbill.id=" + bid + " OR "
            res = res[:-4]
        else:
            raise Warning('ไม่สามารถทำรายการได้เนื่องจากไม่มีรายการสินค้า หรือรายละเอียดสินค้าไม่ถูกต้อง')
            
        self.env.cr.execute("""
            UPDATE nstda_bst_dbill SET qty = t2.result , qty_res = t2.result
            FROM ( SELECT matno,hbill_ids,sum(qty) result 
            FROM nstda_bst_dbill t1 GROUP BY hbill_ids,matno) t2 
            WHERE ( nstda_bst_dbill.hbill_ids = t2.hbill_ids 
            AND nstda_bst_dbill.matno = t2.matno )
            AND ( """ + res + ');')
        
        self.env.cr.execute("""
            DELETE FROM nstda_bst_dbill 
            WHERE id IN ( SELECT id FROM nstda_bst_dbill y1 
            WHERE EXISTS ( SELECT * FROM nstda_bst_dbill y2 
            WHERE y1.matno = y2.matno 
            AND y1.qty = y2.qty 
            AND y1.hbill_ids = y2.hbill_ids 
            AND y1.id < y2.id
            AND ( """ + res + ')));')
    
    
    @api.one
    def bst_send_approval(self):
        
        if self.amount_after_discount > 0:
  
            for v in self.d_bill_ids:
                if v.matno.qty - v.qty < 0:
                    return {'warning': {
                            'title': _('Warning'),
                            'message': _('จำนวนสินค้าในสต็อกไม่เพียงพอ')
                            }}
                      
                else:
                    if self.costct_prjno_selection == 'costct':
                        if self.amount_after_discount <= 10000:
                            level_ = 1
                        elif self.amount_after_discount > 10000 and self.amount_after_discount <= 60000:
                            level_ = 2
                        elif self.amount_after_discount > 60000 and self.amount_after_discount <= 150000:
                            level_ = 4
                        elif self.amount_after_discount > 150000:
                            level_ = 5
                          
                        try:
                            list_boss = self.env['nstdamas.boss'].get_boss(self.empid.id, level=level_)
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
                            return {'warning': {
                                    'title': _('Warning'),
                                    'message': _('ไม่สามารถทำรายการต่อได้ เนื่องจากไม่พบข้อมูลผู้บังคับบัญชาของท่าน')
                                    }}
                          
                    elif self.costct_prjno_selection == 'prjno':
                        Project_Leader = str(self.prjno.id)
                        self.env.cr.execute("SELECT prjm_emp_id FROM nstdamas_projectmember WHERE prjm_prj_id = " + Project_Leader + " AND prjm_position = '00'")
                        pjboss_obj = self.env.cr.fetchone()[0]
                        if pjboss_obj == False:
                            pjboss_obj = self.env['nstdamas.projectmember'].search([('prjm_prj_id','=',Project_Leader), ('prjm_position','=','00')]).prjm_emp_id
                        get_prjm_id = self.env['nstdamas.employee'].search([['id', '=', pjboss_obj]]).emp_rusers_id.id
                        self.prjm_id = get_prjm_id
                          
                        if self.amount_after_discount <= 10000:
                            self.boss_id = get_prjm_id         
                        elif self.amount_after_discount > 10000:
                            try:
                                list_boss = self.env['nstdamas.boss'].get_boss(pjboss_obj)
                                i = 1
                                while True:
                                    if list_boss[i].bss_id.id != False:
                                        boss_id = list_boss[i].bss_id.emp_rusers_id.id
                                        break
                                    i += 1
                                    if i == 6:
                                        break
                                self.boss_id = boss_id
                            except:
                                return {'warning': {
                                        'title': _('Warning'),
                                        'message': _('ไม่สามารถทำรายการต่อได้ เนื่องจากไม่พบข้อมูลผู้บังคับบัญชาของท่าน')
                                        }}
      
            self.book_date = datetime.now()
      
            try:
                self.bst_sum_record()
            except:
                raise Warning('ไม่สามารถทำรายการได้เนื่องจากไม่มีรายการสินค้า หรือรายละเอียดสินค้าไม่ถูกต้อง')
              
            try:
                self.sendmail_approve()
            except:
                pass
          
            if self.costct_prjno_selection == 'costct':
                self.status = 'wait_boss'
            elif self.costct_prjno_selection == 'prjno':
                self.status = 'wait_prjm'
                  
        else:
            raise Warning('ไม่สามารถทำรายการได้เนื่องจากไม่มีรายการสินค้า หรือรายละเอียดสินค้าไม่ถูกต้อง')
        

    @api.one
    def bst_prjm_submit(self):
        
        if self.amount_after_discount > 0:
            
            if self.amount_after_discount <= 10000:
                if self.inv_p == True:
                    self.boss_adate = datetime.now()
                    self.status = 'wait_approvers'
                else:
                    raise Warning('สำหรับหัวหน้าโครงการอนุมัติ')
                
            if self.amount_after_discount > 10000:
                if self.inv_p == True:
                    self.boss_adate = datetime.now()
                    self.status = 'wait_boss'
                else:
                    raise Warning('สำหรับหัวหน้าโครงการอนุมัติ')
                
            try:
                self.bst_sum_record()
            except:
                pass
            
        else:
            raise Warning('ไม่สามารถทำรายการได้เนื่องจากไม่มีรายการสินค้า หรือรายละเอียดสินค้าไม่ถูกต้อง')
 
 
    @api.one
    def bst_submit_limit(self):
        
        if self.amount_after_discount > 0:
            
            if self.inv_b == True:
                self.boss_adate = datetime.now()
                self.status = 'wait_approvers'
            else:
                raise Warning('สำหรับผู้บังคับบัญชาอนุมัติ')
            
            try:
                self.bst_sum_record()
            except:
                pass
            
        else:
            raise Warning('ไม่สามารถทำรายการได้เนื่องจากไม่มีรายการสินค้า หรือรายละเอียดสินค้าไม่ถูกต้อง')
  
  
    @api.one    
    def bst_submit_approval(self):
        if self.inv_a == True:
            self.approver = self._uid
            self.adate = datetime.now()
            
            for v in self.d_bill_ids:
                if v.matno.qty - v.qty < 0:
                    return {'warning': {
                            'title': _('Warning'),
                            'message': _('จำนวนสินค้าในสต็อกไม่เพียงพอ')
                            }}
            self.status = 'pick'
            
        else:
            raise Warning('สำหรับเจ้าหน้าที่อนุมัติ')
    
    
    @api.one     
    def bst_submit_pick(self):
        if self.inv_k == True:
            self.pick_date = datetime.now()
            self.pick_emp_id = self.env['nstdamas.employee'].search([('emp_rusers_id', '=', self._uid)]).id
            
            try:
                self.sendmail_alert()
            except:
                pass
            self.status = 'ready'
        else:
            raise Warning('สำหรับเจ้าหน้าที่อนุมัติ')
        
        
    def _submit_cut_stock(self, cr, uid, ids, context=None):
        self.pool.get('nstda.bst.stock')._cut_stock(cr, uid, context['bst_id'], context=context)
        
    
    def _submit_return_stock(self, cr, uid, ids, context=None):
        self.pool.get('nstda.bst.stock')._return_stock(cr, uid, context['bst_id'], context=context)
        