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
    'name': 'MTLCS_Purchase',
    'version': '1.1',
    'author': 'Jon <alangwansui@gmail.com>',
    'category': '',
    'description': """
      MTL Purchase
    """,
    'website': '',
    'depends': ['mtlcs_base',
                'mtlcs_product',
                'purchase_control_supplier',
                'wizard_template',
                'purchase_order_lines',
                'mtlcs_report',
                'procurement_extend',
                'product_supplier_pricelist',
                'stock_picking_type_ref',
                'product_pricelist_history',
                'ir_export_extended_ept',
                'approve_log',
                'server_sync',
                ],
    'data': [
        ##csv
        'security/ir.model.access.csv',
        'security/security.xml',
        # 'security/multi_company_control_security.xml',

        ##data
        'data/data.xml',
        'data/ir_sequence.xml',
        'data/ir_config_parameter.xml',
        'data/mail_message_subtype.xml',
        'data/ir_exports_purchase.xml',

        ##view
        'procurement.xml',
        'purchase.xml',
        # views
        'views/procurement_report.xml',
        # 'views/account_payable_report.xml',
        'views/mtlcs_purchase.xml',

        # report
        'report/report_preparation_order.xml',
        'report/report_purchase_requisition.xml',
        'report/report_purchase_order.xml',
        'report/action_report.xml',
        'report/report_price_adjust_order.xml',
        'report/report_purchase_history_price.xml',

        # wizard
        'wizard/product_supplierinfo_excel_importor.xml',
        'wizard/preparation_order_mulit_product.xml',
        'wizard/procurement_make_requisition.xml',

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
