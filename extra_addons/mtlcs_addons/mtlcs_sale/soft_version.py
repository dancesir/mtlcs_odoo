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

from openerp.osv import fields, osv


class soft_version(osv.osv):
    _name = 'soft.version'
    _description = 'Soft & Version'
    def _compute_name(self, cr, uid, ids, fields_name, arg=None, context=None):
        res = {}
        for i in self.browse(cr, uid, ids, context=context):
            res[i.id] = '%s[%s]' % (i.soft_id.name, i.version)
        return res

    _columns = {
        'name': fields.char('Name', size=48),
        #'name': fields.function(_compute_name, type="char",  string=u'软件版本', size=48, readonly=True, store=True),
        #'soft_id': fields.many2one('soft.soft', u'软件', required=True),
        #'version': fields.char(u'版本', size=32, required=True),
    }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'不能重复'),
    ]
