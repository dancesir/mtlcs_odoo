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


class employee_excel_importor(osv.osv_memory):
    _inherit = 'excel.importor'

    def apply(self, cr, uid, ids, context=None):
        mod = super(employee_excel_importor, self).apply(cr, uid, ids, context=context)
        if mod == "hr.employee":
            wizard = self.browse(cr, uid, ids[0], context=context)
            datas = self._Parse(file_contents=base64.decodestring(wizard.file), sheet_index=wizard.sheet_index)
            if wizard.type == 'create':
                employee_ids = self.create_employee(cr, uid, datas, context=context, strict=wizard.strict)
            elif wizard.type == 'update':
                employee_ids = self.update_employee(cr, uid, datas, context=context, strict=wizard.strict)

            return {
                'type': 'ir.actions.act_window',
                'name': u'职员信息',
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': mod,
                "domain": [('id', 'in', employee_ids)],
            }
        else:
            return mod

    def _prepare_employee_info(self, cr, uid, datas, context=None, strict=True):
        infos = []
        for row in datas['data']:
            data = {
                'line_number': row['line_number'],
                'active':True,
                'code': row.get('code') or '',
                'name': row.get('name') or '',
                'department_code': row.get('department_code') or '',
            }
            if not data['name'] or not data['code'] or not data['department_code']:
                raise Warning(u'职员的数据不全 %s' % row)

            infos.append(data)
        return infos

    def create_employee(self, cr, uid, datas, context=None, strict=True):
        employee_obj = self.pool.get('hr.employee')
        department_obj = self.pool.get('hr.department')
        infos = self._prepare_employee_info(cr, uid, datas, context=context, strict=strict)
        employee_ids = []
        for info in infos:
            emp_ids = employee_obj.search(cr, uid, [('code', '=', info['code'])], limit=1)
            emp_id = emp_ids and emp_ids[0] or None
            dpt_ids  = department_obj.search(cr, uid, [('ref', '=', info['department_code'])], limit=1)
            dpt_id = dpt_ids and dpt_ids[0] or None
            info.update({'department_id': dpt_id})
            if not dpt_id:
                raise Warning(u'没有找到对应的部门 %s' % info)
            _logger.info('create_employee %s ' % info)
            if not emp_ids:
                new_id = employee_obj.create(cr, uid, info, context=context)
                _logger.info(u'职员创建成功 ID:%s' % (new_id))
                employee_ids.append(new_id)
            else:
                _logger.info(u'职员已经存在 %s %s' % (info['code'], info['line_number']))

        return employee_ids


    def update_employee(self,  cr, uid, datas, context=None, strict=True):
        employee_obj = self.pool.get('hr.employee')
        department_obj = self.pool.get('hr.department')
        infos = self._prepare_employee_info(cr, uid, datas, context=context, strict=strict)
        employee_ids = []
        for info in infos:
            emp_ids  = employee_obj.search(cr, uid, [('code', '=', info['code'])], limit=1)
            emp_id = emp_ids and emp_ids[0] or None
            dpt_ids  = department_obj.search(cr, uid, [('ref', '=', info['department_code'])], limit=1)
            dpt_id = dpt_ids and dpt_ids[0] or None
            info.update({'department_id': dpt_id})
            _logger.info('update_employee %s ' % info)
            if emp_id:
                employee_obj.write(cr, uid, emp_id, info, context=context)
                employee_ids.append(emp_id)
            else:
                _logger.info('Not found product %s' % info['code'])
