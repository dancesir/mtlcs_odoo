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
    'name': 'MTLCS_Stock',
    'version': '1.1',
    'author': 'Jon <alangwansui@gmail.com>',
    'category': '',
    'description': """
      MTL PCB extra
    """,
    'website': '',
    'depends': ['base','stock','mtlcs_base', 'mtlcs_report', 'stock_quick_entry', 'approve_log',
                'picking_transfer_all_once','stock_picking_type_ref', 'stock_return_picking_extend'],
    'data': [
        ##csv
        'security/ir.model.access.csv',
        'security/security.xml',
        'security/multi_company_control_security.xml',
        ##data
        'data/ir_sequence.xml',

        'data/stock_location.xml',
        'data/stock_data.yml',
        'data/stock_location2.xml',

        #'data/stock_location_sz.xml',
        #'data/stock_data_sz.yml',
        #'data/stock_location2_sz.xml',

        'data/mail_message_subtype.xml',
         #report
        'report/stock_report.xml',

        'report/picking_slip.xml',
        'report/picking_purchase_receive.xml',
        ##view
        'stock.xml',
        'stock_quant.xml',
        # views

        #wizard
        'wizard/inventory_excel_importor.xml',
        'wizard/orderpoint_excel_importor.xml',
        'wizard/picking_move_excel_importor.xml',
        'wizard/slow_move_product.xml',

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
