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
from openerp.exceptions import Warning
from openerp.tools.translate import _
import logging
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from xlrd import xldate_as_tuple

_logger = logging.getLogger(__name__)


class procurement_excel_importor(osv.osv_memory):
    _inherit = 'excel.importor'

    def apply(self, cr, uid, ids, context=None):
        mod = super(procurement_excel_importor, self).apply(cr, uid, ids, context=context)
        if mod == "preparation.order":
            wizard = self.browse(cr, uid, ids[0], context=context)
            datas = self._Parse(file_contents=base64.decodestring(wizard.file), sheet_index=wizard.sheet_index)
            preparation_id = context.get('active_id')
            procurement_ids = self.make_procurement_order(cr, uid, datas, preparation_id, context=context, strict=wizard.strict)
            return {}
        else:
            return mod

    def _prepare_procurement_order(self, cr, uid, row,  preparation_id, context=None, strict=True):
        product_obj = self.pool.get('product.product')

        # ==========1123
        preparation_obj = self.pool.get('preparation.order')
        data = preparation_obj.default_get(cr, uid, {}, context=context)
        origin = preparation_obj.read(cr, uid, preparation_id, ['name'], load='_classic_write')['name']
        if row['date_planned']:
            row['date_planned'] = datetime(*xldate_as_tuple(row['date_planned'],0))
        data.update({
            'name': False,
            'product_id': False,
            'product_qty': float(row['product_qty']) or 0.0,
            'date_planned': row['date_planned'] or False,
            'product_uom': False,
            'state': 'draft',

            'origin': origin,
        })

        # data = {
        #     'name': False,
        #     'product_id': False,
        #     'product_qty': float(row['product_qty']) or 0.0,
        #     'date_planned': row['date_planned'] or False,
        #     'product_uom': False,
        #     'state': 'draft',
        # }
        default_code = row['default_code']

        if default_code:
            product_ids = product_obj.search(cr, uid, [('default_code','=',default_code)], limit=1)

            if product_ids:
                data['product_id'] = product_ids[0]
                data['product_uom'] = product_obj.read(cr, uid, product_ids[0], ['uom_id'], load='_classic_write')['uom_id']
                data['name'] = default_code

                # ==========1123
                if not data['date_planned']:
                    purchase_period = product_obj.read(cr, uid, product_ids[0], ['purchase_period'], load='_classic_write')['purchase_period']
                    data['date_planned'] = (datetime.now() + timedelta(days=purchase_period)).strftime(DTF)

        return data

    def make_procurement_order(self, cr, uid, datas, preparation_id, context=None, strict=True):
        product_obj = self.pool.get('product.product')
        procurement_obj = self.pool.get('procurement.order')

        procurement_ids = []
        for row in datas['data']:
            _logger.info('make_procurement_order %s' % row)
            data = self._prepare_procurement_order(cr, uid, row, preparation_id, context=context, strict=strict)
            if not data['product_id']:
                raise Warning(u'没有对应的物料' % row['line_number'])
            if not data['product_qty']:
                raise Warning(u'数量错误' % row['line_number'])

            data.update({'preparation_id': preparation_id})
            new_id = procurement_obj.create(cr, uid, data, context=context)

            # ==========1123
            procurement_obj.rouding_product_qty(cr, uid, new_id, context=context)

            procurement_ids.append(new_id)
            _logger.info(u'需求创建成功ID:%s' % new_id)

        return procurement_ids






