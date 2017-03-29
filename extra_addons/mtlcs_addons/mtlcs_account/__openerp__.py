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
    'name': 'MTLCS_Account',
    'version': '1.1',
    'author': 'Jon <alangwansui@qq.com>',
    'category': '',
    'description': """
      MTL PCB extra
    """,
    'website': '',
    'depends': ['base', 'mtlcs_base', 'account', 'account_voucher', 'purchase',
                'account_voucher_date_due', 'account_invoice_line_xls', 'stock_account',
                'account_payment_term_extension', 'fapiao', 'approve_log',
                'account_invoice_line_price_subtotal_gross'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        # 'security/multi_company_control_security.xml',

        ##data
        'data/payment_term.xml',
        'data/ir_sequence.xml',

        ##view
        'account.xml',
        #views
        #report
        'report/action_report.xml',
        'report/supplier_account_voucher.xml',

        # 'views/report_xxxxx.xml',
        'wizard/batch_invoice_line.xml',
        'wizard/batch_statement_order.xml',
        'wizard/batch_account_voucher.xml',

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
