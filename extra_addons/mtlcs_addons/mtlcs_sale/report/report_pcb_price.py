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



class parser_pcb_price(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(parser_pcb_price, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'multi_selection_data':self._get_multi,
        })

    def _get_multi(self,info_id):
        res1 = ''
        res2 = ''
        res3 = []
        res4 = 0.0

        # 特殊工艺
        for s in info_id.special_tech_ids:
            res1 += (' ' + s.name)

        # 基板材料
        for s in info_id.board_format_ids:
            res2 += (' ' + s.name)

        # 铜厚
        for s in info_id.structure_lines:
            if (s.cu_thick_base >= 0):
                res3.append(s.cu_thick_base)
        res3.sort()
        res4 = res3[0]

        return [res1, res2, res4]

class report_pcb_price(osv.AbstractModel):
    _name = 'report.mtlcs_sale.report_pcb_price'
    _inherit = 'report.abstract_report'
    _template = 'mtlcs_sale.report_pcb_price'
    _wrapped_report_class = parser_pcb_price




###############################################################################
