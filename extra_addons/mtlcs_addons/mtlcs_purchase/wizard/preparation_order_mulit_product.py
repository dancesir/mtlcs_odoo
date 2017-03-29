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

from openerp.osv import fields, osv
from openerp.tools.translate import _


class preparation_order_product_selection(osv.osv_memory):
    _inherit = 'multi.product.selection'

    def apply(self, cr, uid, ids, context=None, ):
        res = super(preparation_order_product_selection, self).apply(cr, uid, ids, context=context)
        if context.get('active_model') == 'preparation.order':
            self.add_preparation_order_line(cr, uid, ids, context=context)
        return res

    def add_preparation_order_line(self, cr, uid, ids, context=None):
        po_obj = self.pool.get('preparation.order')

        po_id = context.get('active_id')
        wizard = self.browse(cr, uid, ids[0], context=context)
        pdt_ids = [x.id for x in wizard.product_ids]
        line_data = []
        for pdt_id in pdt_ids:
            line_data.append((0, 0, {
                'product_id': pdt_id,
                'plan_qty': 0,
                'product_qty': 0,
            }))
        po_obj.write(cr, uid, po_id, {'order_lines': line_data}, context=context)
