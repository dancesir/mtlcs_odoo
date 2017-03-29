# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#    Copyright (C) 2015 credativ ltd. <info@credativ.co.uk>
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
#################################################################################
from openerp.osv import osv, fields
from openerp import models

class product_attribute(osv.osv):
    _inherit = "product.attribute"
    _columns = {
        'code': fields.char(u'编码', size=32 ),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', u' 产品属性编码不能重复'),
    ]

class product_attribute_value(osv.osv):
    _inherit = "product.attribute.value"
    _columns = {
        'code': fields.char(u'编码', size=32 ),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', u' 产品属性值编码不能重复'),
    ]



