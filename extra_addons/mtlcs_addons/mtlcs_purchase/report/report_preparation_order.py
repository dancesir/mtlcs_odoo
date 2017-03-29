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
import time
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp.exceptions import  Warning


class parser_preparation_order(report_sxw.rml_parse):


    def __init__(self, cr, uid, name, context):
        super(parser_preparation_order, self).__init__(cr, uid, name, context=context)

        # ==========1124
        # preparation_ids = context.get('active_ids')
        # preparation_obj = self.pool['preparation.order']
        #
        # for p in preparation_obj.browse(cr, uid, preparation_ids, context):
        #     if p.state != 'done':
        #         raise Warning(u'只能打印状态为【完成】的记录')

        self.localcontext.update({
        })

class report_preparation_order(osv.AbstractModel):
    _name = 'report.mtlcs_purchase.report_preparation_order'
    _inherit = 'report.abstract_report'
    _template = 'mtlcs_purchase.report_preparation_order'
    _wrapped_report_class = parser_preparation_order




###############################################################################
