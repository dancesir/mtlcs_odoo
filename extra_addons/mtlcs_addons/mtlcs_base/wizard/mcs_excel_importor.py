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


class mcs_excle_importor(osv.osv_memory):
    _inherit = 'excel.importor'

    def apply(self, cr, uid, ids, context=None):
        mod = super(mcs_excle_importor, self).apply(cr, uid, ids, context=context)
        if mod == "material.consumption.standard":
            wizard = self.browse(cr, uid, ids[0], context=context)
            datas = self._Parse(file_contents=base64.decodestring(wizard.file), sheet_index=wizard.sheet_index)
            if wizard.type == 'create':
                mcs_ids = self.make_mcs(cr, uid, datas, context=context, strict=wizard.strict)
            elif wizard.type == 'update':
                mcs_ids = self.update_mcs(cr, uid, datas, context=context, strict=wizard.strict)

            return {
                'type': 'ir.actions.act_window',
                'name': u'物料消耗标准',
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': mod,
                "domain": [('id', 'in', mcs_ids)],
            }
        else:
            return mod

    def make_mcs(self, cr, uid, datas, context=None, strict=True):
        pdt_obj = self.pool.get('product.product')
        dpt_obj = self.pool.get('hr.department')
        mcs_obj = self.pool.get('material.consumption.standard')
        mcs_ids = []
        for row in datas['data']:
            _logger.info(row)

            value = float(row['value'] or 0)
            type = row['type'] or 'area'
            product_ids = pdt_obj.search(cr, uid, [('default_code', '=', row['product_code'])], limit=1)
            product_id = product_ids and product_ids[0] or None
            department_ids = dpt_obj.search(cr, uid, [('name', '=', row['department_name'])], limit=1)
            department_id = department_ids and department_ids[0] or None

            if not product_id:
                self._Log_Raise(u'第%s行 物料 错误 ' % row['line_number'], strict=strict)
                continue
            if not department_id:
                self._Log_Raise(u'第%s行 部门 错误 ' % row['line_number'], strict=strict)
                continue
            if not value:
                self._Log_Raise(u'第%s行 标准值 错误 ' % row['line_number'], strict=strict)
                continue

            exist_ids = mcs_obj.search(cr, uid, [('product_id', '=', product_id),('department_id', '=', department_id)],limit=1, context=context)
            if not exist_ids:
                new_id = mcs_obj.create(cr, uid, {
                    'department_id': department_id,
                    'product_id': product_id,
                    'value': value,
                    'type': type,
                    'state': 'normal',
                }, context=context)
                _logger.info('Crete a new material.consumption.standard ID:%s' % new_id)
                mcs_ids.append(new_id)
            else:
                _logger.info(u'第%s行 数据已经存在 ' % row['line_number'])
        return mcs_ids

    def update_mcs(self, cr, uid, datas, context=None, strict=True):
        pdt_obj = self.pool.get('product.product')
        dpt_obj = self.pool.get('hr.department')
        mcs_obj = self.pool.get('material.consumption.standard')
        mcs_ids = []
        for row in datas['data']:
            _logger.info(row)

            value = float(row['value'])
            type = row['type'] or 'area'
            product_ids = pdt_obj.search(cr, uid, [('default_code', '=', row['product_code'])], limit=1)
            product_id = product_ids and product_ids[0] or None
            department_ids = dpt_obj.search(cr, uid, [('name', '=', row['department_name'])], limit=1)
            department_id = department_ids and department_ids[0] or None

            if not product_id:
                self._Log_Raise(u'第%s行 物料 错误 ' % row['line_number'], strict=strict)
                continue
            if not department_id:
                self._Log_Raise(u'第%s行 部门 错误 ' % row['line_number'], strict=strict)
                continue
            if not value:
                self._Log_Raise(u'第%s行 标准值 错误 ' % row['line_number'], strict=strict)
                continue

            exist_ids = mcs_obj.search(cr, uid, [('product_id', '=', product_id),('department_id', '=', department_id)],limit=1, context=context)
            if not exist_ids:
                _logger.info('Not found MCS for %s' % row)
            else:
                mcs_obj.write(cr, uid, exist_ids[0], {
                    'value': value,
                    'type': type,
                    'state': 'normal',
                }, context=context)
                mcs_ids.append( exist_ids[0] )
                _logger.info(u'第%s行 数据更新成功 ' % row['line_number'])
        return mcs_ids



