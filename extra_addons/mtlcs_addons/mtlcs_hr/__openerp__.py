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
{
    'name': 'MTLCS_HR',
    'version': '1.1',
    'author': 'Jon <alangwansui@gmail.com>',
    'category': '',
    'description': """
      MTL PCB extra
    """,
    'website': '',
    'depends': ['base', 'mtlcs_base', 'hr_refcodes',],
    'data': [
        ##csv
        # 'security/ir.model.access.csv',
        'security/security.xml',
        ##data
        'wizard/department_excel_importor.xml',
        'wizard/employee_excel_importor.xml',
        ##view
        'hr.xml',
        'hr_attendance_view.xml'
        #views
        #'views/report_xxxxx.xml',

    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [

    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
