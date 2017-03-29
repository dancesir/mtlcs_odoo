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


class stock_inventory_excel_importor(osv.osv_memory):
    _inherit = 'excel.importor'

    def apply(self, cr, uid, ids, context=None):
        mod = super(stock_inventory_excel_importor, self).apply(cr, uid, ids, context=context)
        if mod == "stock.inventory":
            wizard = self.browse(cr, uid, ids[0], context=context)
            datas = self._Parse(file_contents=base64.decodestring(wizard.file), sheet_index=wizard.sheet_index)
            self.add_inventory_line(cr, uid, datas, context=context, strict=wizard.strict, )

        else:
            return mod

    def add_inventory_line(self, cr, uid, datas, context=None, strict=True):
        pdt_obj = self.pool.get('product.product')
        inv_obj = self.pool.get('stock.inventory')
        inv_line_obj = self.pool.get('stock.inventory.line')

        inventory_id = context.get('active_id')
        inventory_ids = context.get('active_ids')

        location_id = inv_obj.read(cr, uid, inventory_id, ['location_id', ], context=context, load='_classic_write')['location_id']

        line_datas = []
        for data in datas['data']:
            _logger.info('add_inventory_line %s ' % data)

            default_code = data['product_code']
            qty = data['product_qty']
            product_ids = pdt_obj.search(cr, uid, [('default_code', '=', default_code)], limit=1)
            product_id = product_ids and product_ids[0] or None

            if product_id:
                if qty > 0:
                    res = inv_line_obj.onchange_createline(cr, uid, inventory_ids, location_id=location_id, product_id=product_id, uom_id=False,
                                                           package_id=False, prod_lot_id=False, partner_id=False, company_id=False, context=context)
                    line_data = res['value']
                    line_data.update({'product_id': product_id, 'product_qty': qty, 'location_id': location_id})

                    _logger.info('line_data %s ' % line_data)
                    line_datas.append((0, 0, line_data))
                else:
                    self._Log_Raise(u'数量不能小于0', strict=strict)

            else:
                self._Log_Raise(_(u'找不到对应的产品 %s' % data), strict=strict)

        _logger.info(u'添加明细数量 %s ' % len(data))
        inv_obj.write(cr, uid, inventory_id, {'line_ids': line_datas}, context=context)

        return True
