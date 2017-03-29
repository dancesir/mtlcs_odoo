# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Julius Network Solutions SARL <contact@julius.fr>
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
###############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _

class mrp_production_scarp_reason(orm.Model):
    _name = 'stock.move.scrap.reason'
    _description = 'Scrap Reason'
    _columns = {
        'name': fields.char(u'名称', size=256, required=True),
        'code': fields.char(u'编码', size=24, required=True),
        #'active': fields.boolean('Active'),
    }

    _sql_constraints = [
        ('name_uniq', 'unique (name)', u'名称不能重复'),
        ('code_uniq', 'unique (code)', u'编码不能重复'),
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: