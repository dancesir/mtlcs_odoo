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

class special_technic(osv.osv):
    _name = 'special.technic'
    _columns = {
        'name': fields.char(u'特殊工艺', size=32),
        'code': fields.char(u'编码', size=32),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', u'特殊工艺编码不能重复'),
    ]

class process_technic(osv.osv):
    _name = 'process.technic'
    _columns = {
        'name': fields.char(u'工艺', size=32),
        'code': fields.char(u'编码', size=32),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', u'工艺编码不能重复'),
    ]

class mrp_workcenter(osv.osv):
    _inherit = 'mrp.workcenter'
    _columns = {
        'technic_id': fields.many2one('process.technic', u'工艺'),
    }

class technic_attribute(osv.osv):
    _name = 'technic.attribute'
    _columns = {
        'name': fields.char(u'属性', size=32),
        'code': fields.char(u'编码', size=32),
        'workcenter_id': fields.many2one('mrp.workcenter', u'工艺'),
        'technic_id': fields.many2one('process.technic', u'工艺'),
        'is_unconventional': fields.boolean(u'非常规'),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', u'工艺属性编码不能重复'),
    ]


class technic_tag(osv.osv):
    _name = 'technic.tag'
    _columns = {
        'name': fields.char(u'标签', size=32),
        'code': fields.char(u'编码', size=32),
        'attribute_id': fields.many2one('technic.attribute', u'属性'),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', u'工艺编码不能重复'),
    ]
