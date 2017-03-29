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
from openerp.exceptions import Warning
from openerp.osv import fields, osv, expression
from openerp import api, tools, SUPERUSER_ID
from openerp.tools.translate import _



class product_category_code(osv.osv):
    _name = 'product.category.code'

    def _compute_level(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for category in self.browse(cr, uid, ids, context=context):
            level = 0
            if category.parent_id:
                level = category.parent_id.level + 1
            res[category.id] = level
        return res

    def _compute_complete_code(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for category in self.browse(cr, uid, ids, context=context):
            code = category.code or None
            parent_complete_code = category.parent_id and category.parent_id.complete_code
            if parent_complete_code:
                code = '%s%s' % (parent_complete_code, code)
            res[category.id] = code
        return res

    @api.multi
    def name_get(self):
        def get_names(cat):
            """ Return the list [cat.name, cat.parent_id.name, ...] """
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.parent_id
            return res
        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'name': fields.char(u'名称', size=32, required=True),
        'code': fields.char(u'编码', size=16, required=True),
        'level': fields.function(_compute_level, string=u'分类深度', store=True, type='integer'),
        'complete_name': fields.function(_name_get_fnc, type="char", string=u'完整名称'),
        'complete_code': fields.function(_compute_complete_code, string=u'完整编码', type='char', size=40, store=True,
                                         readonly=True),
        'parent_id': fields.many2one('product.category.code', u'上级分类', select=1),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
    }

    _sql_constraints = [
        ('uniq_complete_code', 'unique(complete_code)', u'分类的完全编码必须唯一'),
    ]


###########################################################################