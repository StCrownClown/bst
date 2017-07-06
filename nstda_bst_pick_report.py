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
    status = fields.Char(string="สถานะ", readonly=True)
    matno = fields.Char(string="รหัสสินค้า", readonly=True)
    matdesc = fields.Char(string="ชื่อสินค้า", readonly=True)
    unitprice = fields.Float(string="ราคา", readonly=True)
    qty = fields.Integer(string="จำนวน", readonly=True)
    uom = fields.Char(string="หน่วยนับ", readonly=True)
        
        
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'nstda_bst_pick_report')
        cr.execute("""
            create or replace view nstda_bst_pick_report as (
            SELECT 
                tb.id,
                tb.status,
                tb.matno,
                tb.matdesc,
                tb.unitprice,
                SUM(tb.qty) as qty,
                tb.uom
            FROM(
                SELECT
                    dbill.status,
                    stock.id,
                    stock.matno,
                    stock.matdesc,
                    stock.unitprice,
                    dbill.qty,
                    stock.uom,
                    dbill.hbill_ids
                FROM nstda_bst_dbill dbill
                left join nstda_bst_stock stock on dbill.matno = stock.id
                WHERE dbill.status = 'pick'
                AND dbill.qty != 0
                AND dbill.hbill_ids != 0
                GROUP BY dbill.status,stock.id,stock.matno,stock.matdesc,stock.unitprice,dbill.qty,stock.uom,dbill.hbill_ids
                ORDER BY matno ASC
            ) tb
            GROUP BY tb.id,tb.matno,tb.matdesc,tb.status,tb.unitprice,tb.uom
        )""")
