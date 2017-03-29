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
    'name': 'MTLCS_Quality',
    'version': '1.1',
    'author': 'Jon <alangwansui@qq.com>',
    'category': '',
    'description': """
      MTLCS_Quality
    """,
    'website': '',
    'depends': ['base', 'stock', 'mtlcs_base', 'mtlcs_stock', 'quality_control', 'stock_quick_entry'],
    'data': [
        #
        'security/ir.model.access.csv',
        'security/multi_company_control_security.xml',
        'quality_inspection.xml',
        'stock_picking.xml',

        #report
        'report/action_report.xml',
        'report/iqc_report.xml',

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
