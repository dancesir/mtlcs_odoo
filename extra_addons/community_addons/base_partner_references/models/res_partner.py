# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.osv import osv, fields


class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'ref_customer': fields.char(u'客户编码', size=64, ),
        'ref_supplier': fields.char(u'供应商编码', size=64, ),
    }
    _sql_constraints = [
        ('ref_customer_uniq', 'unique(ref_customer)', u'客户编码必须唯一!'),
        ('ref_supplier_uniq', 'unique(ref_supplier)', u'供应商编码必须唯一!'),
    ]


    def name_get(self, cr, uid, ids, context=None):
        """
        name_get display partner code
        """
        res = super(res_partner, self).name_get(cr, uid, ids, context=context)
        codes = self.read(cr, uid, ids, ['ref_customer','ref_supplier'], context=context)
        show_customer_code = context.get('show_customer_code')
        show_supplier_code = context.get('show_supplier_code')
        new_res = []
        for i in range(len(res)):
            if show_customer_code and codes[i]['ref_customer']:
                new_res.append((res[i][0],  '%s[%s]' % (res[i][1], codes[i]['ref_customer'])   ))
            elif show_supplier_code and codes[i]['ref_supplier']:
                new_res.append((res[i][0],  '%s[%s]' % (res[i][1], codes[i]['ref_supplier'])   ))
            else:
                new_res.append(res[i])
        return new_res




