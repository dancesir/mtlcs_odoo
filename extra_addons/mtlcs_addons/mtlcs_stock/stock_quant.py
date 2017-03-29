
# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 08/09/2014
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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################


from openerp.osv import fields, osv

class stock_quant(osv.osv):
    _inherit = "stock.quant"
    _columns = {
        'use_date': fields.related('lot_id', 'use_date', type='datetime', string=u'使用时间', readonly=True),
        'life_date':fields.related('lot_id', 'life_date', type='datetime', string=u'生命终止日期', readonly=True),
        'removal_date':fields.related('lot_id', 'removal_date', type='datetime', string=u'移除日期', readonly=True),
        'alert_date':fields.related('lot_id', 'alert_date', type='datetime', string=u'警示日期', readonly=True),
    }
