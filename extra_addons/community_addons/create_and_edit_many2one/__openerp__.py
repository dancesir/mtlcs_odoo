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
    'name': 'Create and Edit Many2one Feature Restriction',
    'version': '1.0',
    'category': 'Create and Edit Many2one Feature Restriction Final',
    'sequence': 2,
    'summary': 'Adds res.config option in General Settings, whether to allow or not to allow to user Create and Edit option in Many2One Widget',
    'description': """
The generic OpenERP Create and Edit Many2one Feature Restriction
==================================================================

This application enables a group of people to enable or disable Create and Edit feature with Many2One Widget.
""",
    'author': 'OpenERP SA',
    'website': 'http://www.openerp.com',
    'depends': ['base', 'base_setup', 'web',],
    'data': [
             #'res_config_view.xml',
             'security/create_and_edit_many2one_security.xml',
             ],
    'update_xml': [
        'views/web_client_template.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
