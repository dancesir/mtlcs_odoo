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
from openerp.tools.translate import _
from openerp.osv import fields, osv


class slow_move_product(osv.osv_memory):
    _name = 'slow.move.product'
    _columns = {
        'date_start':  fields.datetime(u'开始日期'),
        #'date_end': fields.date(u'结束日期'),
        #'purchased': fields.boolean(u'有采购记录的'),
    }
    _defaults = {
        'date_start': fields.datetime.now(),
    }

    def apply(self, cr, uid, ids, context=None):
        w = self.browse(cr, uid, ids[0], context=context)
        sql_str = """
          select
            PP.id
          from
            product_product as pp
          where
            pp.id not in (select product_id from stock_move where date > '%s' group by product_id)
        """ % (w.date_start)
        cr.execute(sql_str)
        slow_product_ids = [x[0] for x in cr.fetchall()]
        return {
            'type': 'ir.actions.act_window',
            'name': u'呆滞物料',
            'view_type': 'form',
            "view_mode": 'tree,form',
            'res_model': 'product.product',
            "domain": [('id', 'in', slow_product_ids)],
        }
