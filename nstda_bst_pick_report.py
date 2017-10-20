# -*- coding: utf-8 -*-
import datetime
from dateutil import relativedelta as rdelta
from openerp import tools, models, fields, api, exceptions, _


####################################################################################################


class nstda_bst_pick_report(models.Model):
    
    _name = 'nstda.bst.pick.report'
    _table = 'nstda_bst_pick_report'
    _order = 'matno DESC'
    _auto = False
    
    id = fields.Integer(string="ID ", readonly=True)
    book_date = fields.Date(string="วันที่", readonly=True)
    docno = fields.Char(string="เลขที่เอกสาร", readonly=True)
    emp = fields.Char(string="พนักงานผู้เบิก ", readonly=True)
    matno = fields.Char(string="รหัสสินค้า", readonly=True)
    matdesc = fields.Char(string="ชื่อสินค้า", readonly=True)
    unitprice = fields.Char(string="ราคา", readonly=True)
    qty = fields.Integer(string="จำนวน", readonly=True)
    uom = fields.Char(string="หน่วยนับ", readonly=True)
        
        
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'nstda_bst_pick_report')
        cr.execute("""
            create or replace view nstda_bst_pick_report as (
            SELECT
                stock.id,
                hbill.docno,
                hbill.book_date,
                concat(masemp.emp_id, ' - ', masemp.emp_fname, ' ', masemp.emp_lname) as emp,
                stock.matno,
                stock.matdesc,
                stock.unitprice::numeric::money,
                dbill.qty,
                stock.uom
            FROM nstda_bst_dbill dbill
            left join nstda_bst_stock stock on dbill.matno = stock.id
            left join nstda_bst_hbill hbill on dbill.tbill_ids = hbill.id
            left join nstdamas_employee masemp on hbill.empid = masemp.id
            WHERE dbill.status = 'pick'
            AND dbill.qty != 0
            AND dbill.tbill_ids != 0
            ORDER BY docno ASC
        )""")
