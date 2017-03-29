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
    'name': 'MTLCS_All',
    'version': '1.1',
    'author': 'Jon <alangwansui@gmail.com>',
    'category': '',
    'description': """
      MTLCS ALL, used to add MTL base_daeas.
    """,
    'website': '',
    'depends': ['base', 'mtlcs_base','mtlcs_hr','mtlcs_product','mtlcs_eng',
                'mtlcs_stock','mtlcs_account',
                ],
    'data': [
        #access
        'security/ir.model.access.csv',
        # 'security/multi_company_control_security.xml',

        #data
        'data/soft.version.csv',
        'data/base_data.xml',
        'data/acceptance.standard.csv',
        'data/mark.mark.csv',
        'data/special.technic.csv',
        'data/product.attribute.csv',
        'data/product.attribute.value.csv',
        'data/process.technic.csv',
        'data/mrp.workcenter.csv',
        'data/technic.attribute.csv',
        'data/technic.tag.csv',
        'data/pcb.misc.parts.csv',

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
