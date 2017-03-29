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
import base64
from openerp.osv import fields, osv
from openerp.tools.translate import _
import logging

_logger = logging.getLogger(__name__)

class picking_move_excel_importor(osv.osv_memory):
    _inherit = 'excel.importor'

    def apply(self, cr, uid, ids, context=None):
        mod = super(picking_move_excel_importor, self).apply(cr, uid, ids, context=context)
        if mod == "stock.picking":
            wizard = self.browse(cr, uid, ids[0], context=context)
            datas = self._Parse(file_contents=base64.decodestring(wizard.file), sheet_index=wizard.sheet_index)
            self.add_move_line(cr, uid, datas, context=context, strict=wizard.strict, )
        else:
            return mod

    def add_move_line(self, cr, uid, datas, context=None, strict=True):
        pdt_obj = self.pool.get('product.product')
        pick_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        picking_id = context.get('active_id')

        info_location = pick_obj.read(cr, uid, picking_id, ['location_id', 'location_dest_id'], context=context, load='_classic_write')
        location_id = info_location['location_id']
        location_dest_id = info_location['location_dest_id']

        move_datas = []
        for data in datas['data']:
            _logger.info('add_move_line %s' % data)
            default_code = data['product_code']
            qty = data['product_qty']
            product_ids = pdt_obj.search(cr, uid, [('default_code', '=', default_code)], limit=1)
            product_id = product_ids and product_ids[0] or None
            if not product_id:
                raise osv.except_osv(_('Error!'), _(u'找不到对应的产品 %s' % data))
            if qty <= 0:
                raise osv.except_osv(_('Error!'), _(u'数量不能小于0 %s' % data))

            res = move_obj.onchange_product_id(cr, uid, [], prod_id=product_id, loc_id=location_id, loc_dest_id=location_dest_id,
                                               partner_id=False)
            move = res['value']
            move.update({'product_uom_qty': qty, 'product_id': product_id})
            move_datas.append((0, 0, move))

        pick_obj.write(cr, uid, [picking_id, ], {'move_lines': move_datas}, context=context)
        return True
