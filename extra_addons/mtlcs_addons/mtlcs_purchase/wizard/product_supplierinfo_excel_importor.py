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


class product_supplierinfo_excel_importor(osv.osv_memory):
    _inherit = 'excel.importor'

    def apply(self, cr, uid, ids, context=None):
        mod = super(product_supplierinfo_excel_importor, self).apply(cr, uid, ids, context=context)
        if mod == "product.supplierinfo":
            wizard = self.browse(cr, uid, ids[0], context=context)
            datas = self._Parse(file_contents=base64.decodestring(wizard.file), sheet_index=wizard.sheet_index)
            info_ids = self.make_supplierinfo(cr, uid, datas, context=context, strict=wizard.strict)
            return {
                'type': 'ir.actions.act_window',
                'name': u'物料信息导入',
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': mod,
                "domain": [('id', 'in', info_ids)],
            }
        else:
            return mod

    def make_supplierinfo(self, cr, uid, datas, context=None, strict=True):

        partner_obj = self.pool.get('res.partner')
        tmpl_obj = self.pool.get('product.template')
        supplierinfo_obj = self.pool.get('product.supplierinfo')

        ids = []
        for row in datas['data']:

            _logger.info('make_supplierinfo %s' % row)

            default_code = str(row['product_code']).strip()
            ref_supplier = str(row['ref_supplier']).strip()
            price = float(row['price'] or 0)

            tmpl_ids = tmpl_obj.search(cr, uid, [('default_code','=', default_code)], context=context)
            supplier_is = partner_obj.search(cr, uid, [('ref_supplier','=',ref_supplier)], context=context)
            tmpl_id = tmpl_ids and tmpl_ids[0] or None
            supplier_id =supplier_is and supplier_is[0] or None

            if not tmpl_id:
                 self._Log_Raise(u'第%s行 物料 错误 ' % row['line_number'], strict=strict)
                 continue
            if not supplier_id:
                 self._Log_Raise(u'第%s行 供应商编码 错误 ' % row['line_number'], strict=strict)
                 continue

            supplierinfo_ids = supplierinfo_obj.search(cr, uid, [('name','=',supplier_id),('product_tmpl_id','=',tmpl_id),'|',('active','=',False),('active','=',True)], context=context)
            supplierinfo_id = supplierinfo_ids and supplierinfo_ids[0] or None
            if not supplierinfo_id:
                info_data = {
                    'name': supplier_id,
                    'product_tmpl_id': tmpl_id,
                    'active': True,
                    'state': 'done',
                    'pricelist_ids': [(0,0,{'min_quantity':1, 'price': price })],
                }
                new_id = supplierinfo_obj.create(cr, uid, info_data, context=context)
                _logger.info(u'物料供应商信息创建成功ID%s' % new_id)
                ids.append(new_id)
            else:
                _logger.info(u'物料供应商信息已经存在ID:%s' % supplierinfo_id)

        return ids










            # value = float(row['value'])
            # product_ids = pdt_obj.search(cr, uid, [('default_code', '=', row['product_code'])], limit=1)
            # product_id = product_ids and product_ids[0] or None
            # department_ids = dpt_obj.search(cr, uid, [('name', '=', row['department_name'])], limit=1)
            # department_id = department_ids and department_ids[0] or None
            #
            # if not product_id:
            #     self._Log_Raise(u'第%s行 物料 错误 ' % row['line_number'], strict=strict)
            #     continue
            # if not department_id:
            #     self._Log_Raise(u'第%s行 部门 错误 ' % row['line_number'], strict=strict)
            #     continue
            # if not value:
            #     self._Log_Raise(u'第%s行 标准值 错误 ' % row['line_number'], strict=strict)
            #     continue
            #
            # exist_ids = mcs_obj.search(cr, uid, [('product_id', '=', product_id),('department_id', '=', department_id)],limit=1, context=context)
            # if not exist_ids:
            #     new_id = mcs_obj.create(cr, uid, {
            #         'department_id': department_id,
            #         'product_id': product_id,
            #         'value': value,
            #     }, context=context)
            #     _logger.info('Crete a new material.consumption.standard ID:%s' % new_id)
            #     mcs_ids.append(new_id)
            # else:
            #     _logger.info(u'第%s行 数据已经存在 ' % row['line_number'])
        return pdt_ids

