# -*- coding: utf-8 -*-
import datetime
from dateutil import relativedelta as rdelta
from openerp import tools, models, fields, api, exceptions, _


####################################################################################################


class nstda_bst_bill_report(models.Model):
    
    _name = 'nstda.bst.bill.report'
    _table = 'nstda_bst_bill_report'
    _order = 'docno DESC'
    _auto = False
    
    id = fields.Integer(string="id", readonly=True)
    docno = fields.Char(string="เลขที่เอกสาร", readonly=True)
    book_date = fields.Date(string="วันที่เบิก", readony=True)
    empid = fields.Char(string="พนักงานผู้เบิก", readonly=True)
    boss_id = fields.Char(string="ผู้อนุมัติ", readonly=True)
    org = fields.Char(string="ศูนย์", readonly=True)
    division = fields.Char(string="ฝ่าย", readonly=True)
    dept = fields.Char(string="งาน", readonly=True)
    prj_cct = fields.Char(string="หน่วยงาน/โครงการ", readonly=True)
    objdesc = fields.Char(string="วัตถุประสงค์ในการเบิก", readonly=True)
    receive_emp_id = fields.Char(string="ผู้รับสินค้า", readonly=True)
    
    matno = fields.Char(string="รหัสสินค้า", readonly=True)
    matdesc = fields.Char(string="ชื่อสินค้า", readonly=True)
    qty_res = fields.Integer(string="จำนวน", readonly=True)
    uom = fields.Char(string="หน่วยนับ", readonly=True)
    unitprice = fields.Float(string="ราคา", readonly=True)
    
    amount_after_discount = fields.Float(string="ราคารวมสุทธิ", readonly=True)
    
    
    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        if context is None:
            context = {}
        res = super(nstda_bst_bill_report, self).read(cr, uid, ids, fields=fields, context=context, load=load)
        idx = 0
        for r in res:
            if r.has_key('no'):
                r['no'] = int(idx + 1)
            res[idx] = r
            idx = idx + 1
        return res
        
        
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'nstda_bst_bill_report')
        cr.execute("""
            create or replace view nstda_bst_bill_report as (
            SELECT 
                tb.id,
                tb.docno,
                tb.book_date,
                tb.empid,
                tb.boss_id,
                tb.org,
                tb.division,
                tb.dept,
                tb.prj_cct,
                tb.objdesc,
                tb.receive_emp_id,
                tb.matno,
                tb.matdesc,
                tb.qty_res,
                tb.uom,
                tb.unitprice,
                tb.amount_after_discount
            FROM(
                SELECT
                    hbill.id as id,
                    hbill.docno as docno,
                    hbill.book_date as book_date,
                    concat(emp.emp_fname,' ',emp.emp_lname) as empid,
                    concat(rem.emp_fname,' ',rem.emp_lname) as boss_id,
                    org.org_shortname_en as org,
                    div.dvs_name as division,
                    dept.dpm_name as dept,
                    hbill.prj_cct as prj_cct,
                    hbill.objdesc as objdesc,
                    concat(receive.emp_fname,' ',receive.emp_lname) as receive_emp_id,
                    stock.matno as matno,
                    stock.matdesc as matdesc,
                    dbill.qty_res as qty_res,
                    stock.uom as uom,
                    dbill.unitprice as unitprice,
                    hbill.amount_after_discount as amount_after_discount
                FROM nstda_bst_hbill hbill
                left join nstda_bst_dbill dbill on hbill.id = dbill.hbill_ids
                left join nstdamas_employee emp on hbill.empid = emp.id
                left join res_users res on hbill.boss_id = res.id
                left join nstdamas_employee rem on res.id = rem.emp_rusers_id
                left join nstdamas_employee receive on hbill.receive_emp_id = receive.id
                left join nstdamas_org org on hbill.org = org.id
                left join nstdamas_division div on hbill.division = div.id
                left join nstdamas_department dept on hbill.dept = dept.id
                left join nstda_bst_stock stock on stock.id = dbill.matno
                WHERE hbill.status = 'success'
                ORDER BY docno DESC
            ) tb
        )""")
