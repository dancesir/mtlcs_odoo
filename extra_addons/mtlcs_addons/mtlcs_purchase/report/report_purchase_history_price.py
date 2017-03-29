# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import tools
from openerp.osv import fields, osv


class report_purchase_history_price(osv.osv):
    _name = "report.purchase.history.price"
    _description = "report purchase history price"
    _auto = False
    _columns = {
        'id': fields.integer('ID'),
        'product_id': fields.many2one('product.product', u'物料名称', readonly=True),
        'partner_id': fields.many2one('res.partner', u'供应商', readonly=True),
        'price_unit': fields.float(u'采购价格',  digits=(16, 2), readonly=True),
        'create_date': fields.datetime(u'日期', readonly=True),
        'product_qty': fields.float(u'采购数量', readonly=True),
        'row_n': fields.integer(u'采购次数', readonly=True),
        'state': fields.char(u'状态', readonly=True),

    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_purchase_history_price')
        cr.execute("""
            create or replace view report_purchase_history_price as (
                 SELECT
                    id,
                    product_id,
                    partner_id,
                    price_unit,
                    create_date,
                    product_qty,
                    state,
                    row_n
                    FROM
                      ( SELECT
                          id,
                          product_id,
                          partner_id,
                          price_unit,
                          create_date,
                          product_qty,
                          state,
                          row_number() over(partition by product_id order by create_date desc) as row_n
                        FROM
                          purchase_order_line
                        WHERE state in ('confirmed', 'done')
                      ) pol
                 WHERE row_n < 7
                 GROUP BY
                    id,
                    price_unit,
                    partner_id,
                    create_date,
                    product_qty,
                    state,
                    row_n,
                    product_id
            )
        """)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
