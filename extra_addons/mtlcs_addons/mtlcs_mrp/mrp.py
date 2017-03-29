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
from openerp.osv import fields, osv, orm
from openerp.addons.mrp.mrp import mrp_production as MRP_PRODUCTION

def _dest_id_default(self, cr, uid, ids, context=None):
    location_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mtlcs_stock', 'stock_location_finish')[1]
    self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
    return location_id

#change production dest location default
MRP_PRODUCTION._defaults['location_dest_id'] = _dest_id_default


class resource_resource(osv.osv):
    _inherit = 'resource.resource'
    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'The Code of the resource must be unique !'),
    ]









