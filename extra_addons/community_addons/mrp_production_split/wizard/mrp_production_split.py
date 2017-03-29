# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2009 Albert Cervera i Areny - NaN  (http://www.nan-tic.com) All Rights Reserved.
#    Copyright (c) 2010-Today Elico Corp. All Rights Reserved.
#    Author: Andy Lu <andy.lu@elico-corp.com>
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

from openerp.osv import fields, osv


class mrp_production_split(osv.osv):
    _name = 'mrp.production.split'
    _columns = {
        'name': fields.char('Name'),
        'split_qty': fields.float('Split Qty'),
    }

    def split(self, cr, uid, ids, context=None):
        mo_id = context.get('active_id')
        mod = context.get('active_model')
        mo_obj = self.pool.get(mod)
        mo = mo_obj.browse(cr, uid, mo_id, context=context)
        wizard = self.browse(cr, uid, ids[0], context=context)
        values = {
            'product_qty': wizard.split_qty,
            'split_by_id': mo_id,
        }

        new_id = mo_obj.copy(cr, uid, mo_id, values, context=context)

        return {
            'domain': [('id', 'in', [mo_id, new_id])],
            'name':u'分卡',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': mod,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
