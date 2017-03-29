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


class department_excel_importor(osv.osv_memory):
    _inherit = 'excel.importor'

    def apply(self, cr, uid, ids, context=None):
        mod = super(department_excel_importor, self).apply(cr, uid, ids, context=context)
        if mod == "hr.department":
            wizard = self.browse(cr, uid, ids[0], context=context)
            datas = self._Parse(file_contents=base64.decodestring(wizard.file), sheet_index=wizard.sheet_index)
            if wizard.type == 'create':
                department_ids = self.create_department(cr, uid, datas, context=context, strict=wizard.strict)
            elif wizard.type == 'update':
                department_ids = self.update_department(cr, uid, datas, context=context, strict=wizard.strict)

            return {
                'type': 'ir.actions.act_window',
                'name': u'部门信息',
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': mod,
                "domain": [('id', 'in', department_ids)],
            }
        else:
            return mod

    def _prepare_department_info(self, cr, uid, datas, context=None, strict=True):
        infos = []
        for row in datas['data']:
            _logger.info('%s' % row)

            data = {
                'line_number': row['line_number'],
                'active':True,
                'name': row['name'] or '',
                'ref':  str(row['code']) or '',
                'parent_code': str(row['parent_code']) or '',
            }
            if not data['name'] or not data['ref']:
                raise Warning(u'部门的名称或者编码不能为空')

            infos.append(data)
        return infos

    def create_department(self, cr, uid, datas, context=None, strict=True):
        department_obj = self.pool.get('hr.department')
        infos = self._prepare_department_info(cr, uid, datas, context=context, strict=strict)
        department_ids = []
        for info in infos:
            dpt_ids  = department_obj.search(cr, uid, [('ref', '=', info['ref'])], limit=1)
            dpt_id = dpt_ids and dpt_ids[0] or None
            parent_id = False
            if info['parent_code']:
                parent_ids = department_obj.search(cr, uid, [('ref', '=', info['parent_code'])], limit=1)
                parent_id = parent_ids and parent_ids[0] or None
                if parent_id:
                    info.update({'parent_id': parent_id})
                else:
                    raise Warning(u'没有发现上级部门代码 %s' % info['parent_code'])

            if not dpt_id:
                new_id = department_obj.create(cr, uid, info, context=context)
                _logger.info(u'部门创建成功 ID:%s' % (new_id))
                department_ids.append(new_id)
            else:
                _logger.info(u'部门已经存在 %s %s' % (info['code'], info['line_number']))
        return department_ids


    def update_department_____(self,  cr, uid, datas, context=None, strict=True):
        department_obj = self.pool.get('hr.department')
        infos = self._prepare_department_info(cr, uid, datas, context=context, strict=strict)
        department_ids = []
        for info in infos:
            emp_ids  = department_obj.search(cr, uid, [('code', '=', info['code'])], limit=1)
            emp_id = emp_ids and emp_ids[0] or None
            _logger.info('update_department %s ' % info)
            if emp_id:
                department_obj.write(cr, uid, emp_id, info, context=context)
                department_ids.append(emp_id)
            else:
                _logger.info('Not found product %s' % info['code'])
