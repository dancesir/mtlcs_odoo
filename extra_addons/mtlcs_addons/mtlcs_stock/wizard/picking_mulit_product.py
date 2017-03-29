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
        if context.get('active_model') == 'stock.picking':
            self.add_moves(cr, uid, ids, context=context)
        return res

    def add_moves(self, cr, uid, ids, context=None):
        pdt_obj = self.pool.get('product.product')
        pick_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')

        picking_id = context.get('active_id')
        pick = pick_obj.browse(cr, uid, picking_id, context=context)

        wizard = self.browse(cr, uid, ids[0], context=context)
        pdt_ids = [x.id for x in wizard.product_ids]
        move_data = []
        location_id =  pick.picking_type_id.default_location_src_id.id
        location_dest_id = pick.picking_type_id.default_location_dest_id.id

        for p in pdt_obj.browse(cr, uid, pdt_ids, context=context):
            data = move_obj.onchange_product_id(cr, uid, ids, prod_id=p.id, loc_id=location_id, loc_dest_id=location_dest_id, partner_id=False)
            data['value']['product_id'] = p.id
            move_data.append((0, 0, data['value'] ))

        pick_obj.write(cr, uid, [picking_id,], {'move_lines': move_data}, context=context)
