
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

from openerp.osv import fields, osv

class stock_return_picking(osv.osv_memory):
    _inherit = 'stock.return.picking'
    _columns = {
    }

    def _create_returns(self, cr, uid, ids, context=None):
        ''' return picking move.dest location , use return_type.dest_location'''
        pick_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')

        res = (new_picking, pick_type_id) = super(stock_return_picking, self)._create_returns(cr, uid, ids, context=context)

        pick = pick_obj.browse(cr, uid, new_picking, context=context)
        pick_type = pick.picking_type_id
        location_dest_id = pick_type.default_location_dest_id and pick_type.default_location_dest_id.id or False
        if location_dest_id and pick.move_lines[0].location_dest_id.id != location_dest_id:
            move_obj.write(cr, uid, [x.id for x in pick.move_lines], {'location_dest_id': location_dest_id})

        return res











#################