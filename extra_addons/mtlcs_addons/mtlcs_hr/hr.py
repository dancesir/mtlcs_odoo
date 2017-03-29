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

from openerp.osv import fields, osv, expression
from openerp import SUPERUSER_ID
from openerp.tools.translate import _

class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _columns = {

    }

    def create_user(self, cr, uid, ids, context=None):
        user_obj = self.pool.get('res.users')
        employees = self.browse(cr, uid, ids, context=context)

        defualt_passwd = '123456'

        for emp in employees:
            if not emp.user_id:
                user_id = user_obj.create(cr, uid, {
                    'login': emp.code,
                    'name': emp.name,
                    'password': defualt_passwd,
                }, context=context)
                self.write(cr, uid, emp.id, {'user_id': user_id}, context=context)
        return True
