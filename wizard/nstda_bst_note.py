# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
import datetime
from pytz import timezone


class nstda_bst_note(osv.osv_memory):
    
    _name = "nstda.bst.note"
    _description = "Bookstore Note"
    
    _columns = {
        'bst_note': fields.text('Note'),
        'receive_emp_id': fields.many2one('nstdamas.employee', 'ผู้รับสินค้า'),
    }
    
    _defaults = {
    }
    
    
    def send_ready_x(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context)
        bst_obj = self.pool.get('nstda.bst.hbill')
        ids = self.pool.get('res.users').search(cr, uid, [('id', '=', uid)], context=context)
        user = self.pool.get("res.users").browse(cr, uid, ids[0])
        emp = self.pool.get("nstdamas.employee").browse(cr, uid, (self.pool.get('nstdamas.employee').search(cr, uid, [('emp_rusers_id', '=', user.id)], context=context)))
        
        if context is None:
            context = {}
        if 'bst_id' in context:
            bst_obj.write(cr, uid, context['bst_id'], {'status': context['status'],
                                                       'receive_emp_id': wizard.receive_emp_id.id,
                                                       'assign_emp_id': emp.id,
                                                       'post_date':datetime.datetime.now(timezone('UTC')),
                                                       'fiscalyear_docno_intf':datetime.datetime.now().year,
                                                       'fiscalyear_icno_intf':datetime.datetime.now().year
                                                        })
        
        self.pool.get('nstda.bst.hbill').submit_cut_stock(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.mail.alert').sendmail_success(cr, uid, context['bst_id'], context=context)
#         self.pool.get('nstda.bst.hbill').submit_return_stock(cr, uid, context['bst_id'], context=context)
        
        return {'type': 'ir.actions.act_window_close'}
    
    
    def send_cancel_x(self, cr, uid, ids, context=None):
        emp_name = u""
        wizard = self.browse(cr, uid, ids[0], context)
        bst_obj = self.pool.get('nstda.bst.hbill')
         
        if context is None:
            context = {}
        if 'bst_id' in context:
            emp_id = self.pool.get('nstdamas.employee').get_rusers_idByUid(cr, uid, uid)
            if emp_id:
                emp_name = "(" + str(self.pool.get('nstdamas.employee').name_get(cr, uid, emp_id)[0][1])[:6] + ")"
                bst_obj.write(cr, uid, context['bst_id'], {'bst_cancel_uid': emp_id})
            bst_obj.write(cr, uid, context['bst_id'], {'status': context['status'], 'bst_cancel_date':datetime.datetime.now(timezone('UTC')), 'bst_note': wizard.bst_note + emp_name })
            
            self.pool.get('nstda.bst.hbill').submit_return_stock(cr, uid, context['bst_id'], context=context)
            
        return {'type': 'ir.actions.act_window_close'}
    
    
    def btn_send_request(self, cr, uid, ids, context=None):
        self.pool.get('nstda.bst.dbill').set_t_field(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.hbill').btn_send_request(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.mail.alert').sendmail_boss(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.mail.alert').sendmail_prjm(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.dbill').compute_sum_res(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.hbill')._compute_amount_leftside(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.hbill')._compute_amount_rightside(cr, uid, context['bst_id'], context=context)
        
        
    def btn_prjm_submit(self, cr, uid, ids, context=None):
        self.pool.get('nstda.bst.hbill').btn_prjm_submit(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.dbill').compute_sum_res(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.hbill').submit_cut_stock(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.mail.alert').sendmail_boss(cr, uid, context['bst_id'], context=context)
        
        
    def btn_boss_submit(self, cr, uid, ids, context=None):   
        self.pool.get('nstda.bst.hbill').btn_boss_submit(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.dbill').compute_sum_res(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.hbill').submit_cut_stock(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.mail.alert').sendmail_prsd(cr, uid, context['bst_id'], context=context)
    
    
    def btn_prsd_submit(self, cr, uid, ids, context=None):    
        self.pool.get('nstda.bst.hbill').btn_prsd_submit(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.mail.alert').sendmail_bss_lv4(cr, uid, context['bst_id'], context=context)
        
        
    def btn_bss_lv4_submit(self, cr, uid, ids, context=None):    
        self.pool.get('nstda.bst.hbill').btn_bss_lv4_submit(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.mail.alert').sendmail_bss_lv5(cr, uid, context['bst_id'], context=context)
        
        
    def btn_bss_lv5_submit(self, cr, uid, ids, context=None):    
        self.pool.get('nstda.bst.hbill').btn_bss_lv5_submit(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.mail.alert').sendmail_bss_lv6(cr, uid, context['bst_id'], context=context)
        
        
    def btn_bss_lv6_submit(self, cr, uid, ids, context=None):    
        self.pool.get('nstda.bst.hbill').btn_bss_lv6_submit(cr, uid, context['bst_id'], context=context)
    
        
    def btn_approver_submit(self, cr, uid, ids, context=None):   
        self.pool.get('nstda.bst.hbill').btn_approver_submit(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.hbill').submit_cut_stock(cr, uid, context['bst_id'], context=context)
        
        
    def btn_submit_pick(self, cr, uid, ids, context=None):    
        self.pool.get('nstda.bst.hbill').btn_submit_pick(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.hbill').submit_cut_stock(cr, uid, context['bst_id'], context=context)
        self.pool.get('nstda.bst.mail.alert').sendmail_ready(cr, uid, context['bst_id'], context=context)
        
        
    def btn_re_workflow(self, cr, uid, ids, context=None):    
        self.pool.get('nstda.bst.hbill').btn_send_request(cr, uid, context['bst_id'], context=context)
        

nstda_bst_note()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
