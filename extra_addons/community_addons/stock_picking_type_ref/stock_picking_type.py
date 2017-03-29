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

from openerp.tools.translate import _
from openerp.osv import fields, osv


class stock_picking_type(osv.osv):
    _inherit = 'stock.picking.type'
    _columns = {
        'ref': fields.char(u'Ref', size=32),
    }
    _sql_constraints = [
        ('uniq_ref', 'unique(ref)', 'ref must be unique'),
    ]

    def browse_by_ref(self, cr, uid, ref, context=None):
        ids = self.search(cr, uid, [('ref','=',ref)], limit=1)
        if ids:
            return self.browse(cr, uid, ids[0], context=context)
        else:
            return None







##############################################################################