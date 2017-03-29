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
    'name': 'MTLCS_Sale',
    'version': '1.1',
    'author': 'Jon <alangwansui@gmail.com>',
    'category': '',
    'description': """
      MTL PCB extra
    """,
    'website': '',
    'depends': ['base','mtlcs_base','sale', 'sale_order_line_view', 'product_attribute_code', 'acceptance_standard',
                'stock_route_extend'],
    'data': [
        ##csv
         'security/ir.model.access.csv',
        ##data
        'data/unit.xml',
        'data/ir_sequence.xml',
        'data/data.xml',
        ##view
        'partner.xml',
        'soft_version.xml',
        'receive_order.xml',
        'pcb_info.xml',
        'pcb_fee_arg.xml',
        'pcb_price.xml',
        'pcb_product.xml',
        'sale_order.xml',
        'change_order.xml',
        'standard_detection.xml',
        'pcb_remind.xml',
      #  'sale_production_batch.xml',
        'sale_order_wkf.xml',
        # views
        # 'views/report_xxxxx.xml',

        #wizard
        'wizard/pcb_price_batch.xml',
        'wizard/wizard_structure_line.xml',
        'wizard/wizard_sale_order_line.xml',


        ##repart
        'report/action_report.xml',
        'report/report_pcb_price.xml',
        'report/report_pcb_info.xml',
        'report/report_pcb_info_impedance.xml',
        'report/report_sale_order.xml',

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
