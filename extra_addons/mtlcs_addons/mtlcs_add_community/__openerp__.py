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
    'name': 'mtlcs_add_community',
    'version': '1.1',
    'author': 'Jon <alangwansui@qq.com>',
    'category': '',
    'description': """
      Add MTLCS depend community addons
    """,
    'website': '',
    'depends': [
        'create_and_edit_many2one', 'excel_importor', 'unit_sequence', 'cron_run_manually',
        'acceptance_standard', 'ir_export_extended_ept', 'auto_backup', 'hr_refcodes',
        'ir_ui_view_extend', 'lot_production_date', 'picking_transfer_all_once',
        'persistence_transfer_details', 'purchase_order_lines'
    ],
    'data': [
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
