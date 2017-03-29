# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _


class stock_move(osv.osv):
    _inherit = 'stock.move'

    def _scrap_reason_get(self, cr, uid, context=None):
        reason_obj = self.pool.get('stock.move.scrap.reason')
        ids = reason_obj.search(cr, uid, [], context=context)
        result = []
        for line in reason_obj.browse(cr, uid, ids, context=context):
            result.append((line.id, line.name))
        result.append((-1, _('Other...')))
        return result

    _columns = {
        'reason': fields.selection(_scrap_reason_get, u'报废原因', size=-1, ),
        'notes_reason': fields.text('报废说明'),
    }

    def action_scrap(self, cr, uid, ids, product_qty, location_id, restrict_lot_id=False,
                     restrict_partner_id=False, context=None):

        res = super(stock_move, self).action_scrap(
            cr, uid, ids, product_qty, location_id, restrict_lot_id=restrict_lot_id,
            restrict_partner_id=restrict_partner_id, context=context)

        if context.get('reason'):
            reason = context.get('reason')
            notes_reason = context.get('notes_reason') or False
            self.write(cr, uid, res, {
                'reason': reason,
                'notes_reason': notes_reason
            }, context=context)

        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
