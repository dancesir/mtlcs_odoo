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

from datetime import datetime

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _
from openerp import netsvc


class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    _columns = {
        'split_by_id': fields.many2one('mrp.production', u'分卡于', readonly=True, ondelete="restrict"),
    }

    def action_compute__(self, cr, uid, ids, properties=None, context=None):
        p = self.browse(cr, uid, ids[0], context=context)
        #if this is a split mo, not need raw_input,
        if p.split_by_id:
            return True
        else:
            return super(mrp_production, self).action_compute(cr, uid, ids, properties=properties, context=context)








#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
