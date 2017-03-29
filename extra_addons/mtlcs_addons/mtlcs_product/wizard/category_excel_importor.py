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
import re
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)


class product_category_excel_importor(osv.osv_memory):
    _inherit = 'excel.importor'

    def apply(self, cr, uid, ids, context=None):
        mod = super(product_category_excel_importor, self).apply(cr, uid, ids, context=context)
        if mod == "product.category.code":
            wizard = self.browse(cr, uid, ids[0], context=context)
            datas = self._Parse(file_contents=base64.decodestring(wizard.file), sheet_index=wizard.sheet_index)
            product_ids = []

            if wizard.type == 'create':
                categ_ids = self.create_product_category(cr, uid, datas, context=context, strict=wizard.strict, )
            elif wizard.type == 'update':
                categ_ids = self.update_product_category(cr, uid, datas, context=context, strict=wizard.strict, )
            return {
                'type': 'ir.actions.act_window',
                'name': u'物料分类',
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': mod,
                "domain": [('id', 'in', categ_ids)],
            }
        else:
            return mod

    def _prepare_category_info(self, cr, uid, datas, context=None, strict=True):
        infos = []
        for row in datas['data']:
            _logger.info('_prepare_info %s' % row)
            data = {}
            code = str(row.get('code'))
            parent_code = str(row.get('parent_code'))
            name = row.get('name')

            if not re.match('^\d+$', code) or (parent_code and not re.match('^\d+$', parent_code)):
                raise Warning(u'格式错误, 第%s行: %s' %  (row['line_number'], row))

            data.update({'name': name,'code':code, 'parent_code':parent_code})
            infos.append(data)
        return infos

    def update_product_category(self, cr, uid, datas, context=None, strict=True):
        return

    def create_product_category(self, cr, uid, datas, context=None, strict=True):
        category_obj = self.pool.get('product.category.code')
        infos = self._prepare_category_info(cr, uid, datas, context=context, strict=strict)

        categ_ids = []
        count = 0
        for info in infos:
            _logger.info(info)
            code, parent_code, name = (info['code'], info['parent_code'], info['name'])
            parent_id = False
            if parent_code:
                parent_id = category_obj.search(cr, uid, [('complete_code', '=', parent_code)], limit=1)
                if parent_id:
                    parent_id = parent_id[0]
                else:
                    raise Warning('not found parent category by parent_code:%s' % parent_code)

            domain = [('code','=',code),('parent_id', '=', parent_id)]
            old_id = category_obj.search(cr, uid, domain, limit=1)
            if not old_id:
                new_id =category_obj.create(cr, uid, {'code':code, 'name':name, 'parent_id': parent_id}, context=context)
                count += 1
                if count == 50:
                    cr.commit()
                    count = 0

                _logger.info(u'建成功 ID:%s' % (new_id))
                categ_ids.append(new_id)
            else:
                _logger.info(u'分类 code:%s parent_code:%s 已经存在%s ' % (code,parent_code,old_id))

        return categ_ids






#################################################