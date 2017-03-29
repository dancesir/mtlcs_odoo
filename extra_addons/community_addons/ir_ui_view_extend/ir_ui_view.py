
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 08/09/2014
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2013 Daniel Reis
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
from lxml import etree
from openerp.osv import osv, fields

class ir_ui_view(osv.osv):
    _inherit = 'ir.ui.view'
    _columns = {

    }

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        """
        ir_view_action can add context like {'no_create':1} to set tree or  form view create attr
        """
        res = super(ir_ui_view, self).read(cr, uid, ids, fields=fields, context=context, load=load)
        if context.get('no_create') or context.get('no_edit'):
            for view in res:
                view_type = view.get('type')
                if view_type in ['tree', 'form','kanban']:
                    arch = etree.fromstring(view['arch'].encode('utf-8'))
                    for t in arch.xpath("//"+ view_type):
                        if context.get('no_create'):
                            t.attrib['create'] = 'false'
                        if context.get('no_edit'):
                            t.attrib['edit'] = 'false'
                    view['arch'] = etree.tostring(arch)

        return  res
    #view_arch = etree.fromstring(view['arch'].encode('utf-8'))