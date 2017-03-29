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

class customer_requirement_template(osv.osv):
    _name = 'customer.requirement.template'
    _descrisdfption = '客户通用信息'
    _columns = {
        'name' : fields.char('Name', size=32),
        'partner_id': fields.many2one('res.partner', 'Partner'),
    }
class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'requirement_template_ids': fields.one2many('customer.requirement.template','partner_id', string=u'客户通用信息'),
        #'transport_insurance': fields.selection([('buyer',u'买方'),('seller',u'卖方'),('buyer2',u'乙方'),('seller2',u'甲方')], u'运费及运保费由' ),

    }