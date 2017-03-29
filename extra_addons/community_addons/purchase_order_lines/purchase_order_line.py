
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

from openerp.osv import osv, fields


class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'

    def open_lines(self, cr, uid, domain, limit=80, context=None, target='new'):

        tree_view_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'purchase_order_lines', 'purchase_order_line_tree_view')[1]

        pol_ids = self.search(cr, uid, domain, context=context, limit=limit)
        return {
            'domain': [('id', 'in', pol_ids)],
            'name': (u'采购明细'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views':[(tree_view_id,'tree'),],
            'res_model': 'purchase.order.line',
            'type': 'ir.actions.act_window',
            'target': target,
            # ==========1217
            'context': {'show_supplier_code':1, 'show_product_id':1}
        }
################################################################################