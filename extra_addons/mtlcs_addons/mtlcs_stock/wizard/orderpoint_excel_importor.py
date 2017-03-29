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


class orderpoint_excel_importor(osv.osv_memory):
    _inherit = 'excel.importor'

    def apply(self, cr, uid, ids, context=None):
        mod = super(orderpoint_excel_importor, self).apply(cr, uid, ids, context=context)
        if mod == "stock.warehouse.orderpoint":
            wizard = self.browse(cr, uid, ids[0], context=context)
            datas = self._Parse(file_contents=base64.decodestring(wizard.file), sheet_index=wizard.sheet_index)
            orderpoint_ids = []
            if wizard.type == 'create':
                orderpoint_ids = self.create_orderpoint(cr, uid, datas, context=context, strict=wizard.strict, )
            elif wizard.type == 'update':
                orderpoint_ids = self.update_orderpoint(cr, uid, datas, context=context, strict=wizard.strict, )
            return {
                'type': 'ir.actions.act_window',
                'name': u'安全库存',
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': mod,
                "domain": [('id', 'in', orderpoint_ids)],
            }
        else:
            return mod

    def create_orderpoint(self, cr, uid, datas, context=None, strict=True):
        pdt_obj = self.pool.get('product.product')
        orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')
        location_obj = self.pool.get('stock.location')
        orderpoint_ids = []
        for data in datas['data']:
            _logger.info('create_orderpoint %s ' % data)

            default_code = data['product_code']
            product_min_qty = int(data['product_min_qty'])
            loc_barcode = data['loc_barcode']

            product_ids = pdt_obj.search(cr, uid, [('default_code', '=', default_code)], limit=1)
            product_id = product_ids and product_ids[0] or None
            location_ids = location_obj.search(cr, uid, [('loc_barcode','=',loc_barcode)], limit=1)
            location_id = location_ids and location_ids[0] or None

            if not product_id:
                self._Log_Rais(u'找不到对应的产品 %s' % data, strict=strict)
                continue
            if product_min_qty <= 0:
                self._Log_Rais(u'安全库存数量错误 %s' % data, strict=strict)
                continue
            if not location_id:
                self._Log_Rais(u'库位错误 %s' % data, strict=strict)
                continue

            exist_ids = orderpoint_obj.search(cr, uid, [('product_id','=',product_id)], limit=1)
            if exist_ids:
                self._Log_Rais(u'安全库存已经存在 %s' % data, strict=strict)
                continue

            new_id = orderpoint_obj.create(cr, uid, {
                'product_id': product_id,
                'product_min_qty':product_min_qty,
                'product_max_qty': product_min_qty,
                'location_id': location_id,
            }, context=context)
            orderpoint_ids.append(new_id)
        return orderpoint_ids
