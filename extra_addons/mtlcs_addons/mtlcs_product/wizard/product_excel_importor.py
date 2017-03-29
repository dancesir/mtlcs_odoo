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


class product_excel_importor(osv.osv_memory):
    _inherit = 'excel.importor'

    def apply(self, cr, uid, ids, context=None):
        mod = super(product_excel_importor, self).apply(cr, uid, ids, context=context)
        if mod == "product.product":
            wizard = self.browse(cr, uid, ids[0], context=context)
            datas = self._Parse(file_contents=base64.decodestring(wizard.file), sheet_index=wizard.sheet_index)
            product_ids = []

            if wizard.type == 'create':
                product_ids = self.create_product(cr, uid, datas, context=context, strict=wizard.strict, )
            elif wizard.type == 'update':
                product_ids = self.update_product(cr, uid, datas, context=context, strict=wizard.strict, )

            product_ids = product_ids or []
            return {
                'type': 'ir.actions.act_window',
                'name': u'物料信息导入',
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': mod,
                "domain": [('id', 'in', product_ids)],
            }
        else:
            return mod

    def _prepare_product_info(self, cr, uid, datas, context=None, strict=True):
        #pdt_obj = self.pool.get('product.product')
        unit_obj = self.pool.get('product.uom')

        infos = []
        for row in datas['data']:
            _logger.info('_prepare_info %s' % row)

            data = {'line_number': row['line_number']}
            default_code = str(row['product_code']).strip()
            if default_code:
                data.update({'default_code': default_code })
            if row.get('name'):
                data.update({'name': row.get('name') })
            if row.get('variants'):
                data.update({'variants': row.get('variants') })
            if row.get('dongshuo_code'):
                data.update({'dongshuo_code': row.get('dongshuo_code') })
            if row.get('standard_price'):
                data.update({'standard_price': float(row.get('standard_price')) })
            if row.get('abc'):
                data.update({'abc': float(row.get('abc')) })
            if row.get('unit'):
                unit_name = row.get('unit').lower()
                uom_id = unit_obj.search(cr, uid, [('name','=',unit_name)])
                uom_id = uom_id and uom_id[0] or False
                if uom_id:
                    data.update({'uom_id': uom_id, 'uom_po_id':uom_id, 'uos_id': uom_id})

            if 'length' in row:
                length = float(row['length'])
                data.update({'length': length})
            if 'width' in row:
                width = float(row['width'])
                data.update({'width': width})
            if 'height' in row:
                height = float(row['height'])
                data.update({'height': height})
            if 'cu_thick' in row:
                cu_thick = row['cu_thick'].strip()
                data.update({'cu_thick': cu_thick})
            if 'tg_value' in row:
                tg_value = int(row['tg_value'] or '0')
                data.update({'tg_value': tg_value})
            if 'diameter' in row:
                diameter = float(row['diameter'])
                data.update({'diameter': diameter})
            if 'colour' in row:
                data.update({'colour': row['colour']})
            if 'purchase_period' in row:
                period = False
                try:
                    period = int(row['purchase_period'])
                except Exception, e:
                    pass
                if period:
                    data.update({'purchase_period': period})

            infos.append(data)
        return infos

    def update_product(self, cr, uid, datas, context=None, strict=True):
        pdt_obj = self.pool.get('product.product')
        infos = self._prepare_product_info(cr, uid, datas, context=context, strict=strict)
        pdt_ids = []
        for info in infos:
            default_code = info['default_code']
            product_ids = pdt_obj.search(cr, uid, [('default_code', '=', default_code)], limit=1)
            product_id = product_ids and product_ids[0] or None

            _logger.info('update_product %s ' % info)
            if product_id:
                pdt_obj.write(cr, uid, product_id, info, context=context)
                pdt_ids.append(product_id)
            else:
                _logger.info('Not found product %s' % default_code)

        return pdt_ids

    def create_product(self, cr, uid, datas, context=None, strict=True):
        pdt_obj = self.pool.get('product.product')

        infos = self._prepare_product_info(cr, uid, datas, context=context, strict=strict)
        default_info = {
            'active': True,
            'sale_ok': False,
            'purchase_ok': True,
            'purchase_requisition': True,
            'categ_id': 1,
            'type': 'product',  # TODO
            'uom_id': 1,
            'uom_po_id': 1,
            'uos_id': 1,
        }

        pdt_ids = []
        for info in infos:
            #product default value
            for k in default_info:
                if k not in info:
                    info.update({k:default_info[k]})
            _logger.info('create_product %s' % info)

            product_ids = pdt_obj.search(cr, uid, [('default_code', '=', info['default_code'])], limit=1)
            product_id = product_ids and product_ids[0] or None
            if not product_id:
                new_id = pdt_obj.create(cr, uid, info, context=context)
                _logger.info(u'物料创建成功 ID:%s' % (new_id))
                pdt_ids.append(new_id)
            else:
                _logger.info(u'物料已经存在 %s %s' % (info['default_code'], info['line_number']))

        return pdt_ids










        for row in datas['data']:

            _logger.info('create_product_row %s' % row)

            data = {
                'active': True,
                'sale_ok': False,
                'purchase_ok': True,
                'purchase_requisition': True,
                'categ_id': 1,
                'type': 'product',  # TODO
                'uom_id': 1,
                'uom_po_id': 1,
                'uos_id': 1,

            }


            default_code = "".join(str(row['product_code']).split())
            if default_code:
                data.update({'default_code': default_code })
            if row.get('name'):
                data.update({'name': row.get('name') })
            if row.get('variants'):
                data.update({'variants': row.get('variants') })
            if row.get('dongshuo_code'):
                data.update({'dongshuo_code': row.get('dongshuo_code') })
            if row.get('standard_price'):
                data.update({'standard_price': float(row.get('standard_price')) })
            if row.get('abc'):
                data.update({'abc': float(row.get('abc')) })
            if row.get('unit'):
                unit_name = row.get('unit')
                uom_id = unit_obj.search(cr, uid, [('name','=',unit_name)])
                uom_id = uom_id and uom_id[0] or False
                if uom_id:
                    data.update({'uom_id': uom_id, 'uom_po_id':uom_id, 'uos_id': uom_id })


            product_ids = pdt_obj.search(cr, uid, [('default_code', '=', default_code)], limit=1)
            product_id = product_ids and product_ids[0] or None
            if not product_id:
                new_id = pdt_obj.create(cr, uid, data, context=context)
                _logger.info('create_product %s' % data)
                _logger.info(u'物料创建成功 %s %s ID:%s' % (default_code, row['line_number'], new_id))
                pdt_ids.append(new_id)


            else:
                _logger.info(u'物料已经存在 %s %s' % (default_code, row['line_number']))

        return pdt_ids
