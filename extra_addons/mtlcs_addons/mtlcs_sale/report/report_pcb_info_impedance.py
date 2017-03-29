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

class parser_pcb_info_impedance(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(parser_pcb_info_impedance, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'multi_selection_data': self._get_multi,
        })

    def _get_multi(self, info_id):

        # 结构信息
        line_cu =   u'=============================================='
        line_pp =   u'++++++++++++++++++++++++++++++++++++++++++++++'
        line_core = u'<><><><><><><><><><><><><><><><><><><><><><><>'
        line_explain = u'图例： [CU：' + line_cu[0:4] + u'], [PP：' + line_pp[0:4] + u'], [Core：' + line_core[0:4] + u']'
        i = 1
        structure_lines = {}

        for sl in info_id.structure_lines:
            line_tmp = {}
            if i == 1:
                line_tmp[1] = 'TOP'
                line_tmp[2] = line_cu
                line_tmp[3] = info_id.max_cu_thick
                line_tmp[4] = sl.type

            if i>1 and sl.type == 'cu':
                line_tmp[1] = sl.name
                line_tmp[2] = line_cu
                # line_tmp[3] = str(sl.cu_thick_base) + ' μm '
                line_tmp[3] = sl.unit and str(sl.thick) + ' ' + sl.unit + ' ' or str(sl.thick)
                line_tmp[4] = sl.type

            if i > 1 and sl.type == 'pp':
                line_tmp[1] = sl.name
                line_tmp[2] = line_pp
                line_tmp[3] = sl.unit and str(sl.thick) + ' ' + sl.unit + ' ' or str(sl.thick)
                line_tmp[4] = sl.type

            if i > 1 and sl.type == 'core':
                line_tmp[1] = sl.name
                line_tmp[2] = line_core
                line_tmp[3] = sl.unit and str(sl.thick) + ' ' + sl.unit + ' ' or str(sl.thick)
                line_tmp[4] = sl.type

            if i == len(info_id.structure_lines) and sl.type == 'cu':
                line_tmp[1] = 'BOT'
                line_tmp[2] = line_cu
                line_tmp[3] = info_id.max_cu_thick
                line_tmp[4] = sl.type
                structure_lines[i] = line_tmp

            structure_lines[i] = line_tmp
            i += 1

        # 基板材料
        board_format_ids = ''
        for s in info_id.board_format_ids:
            board_format_ids += (' ' + s.name)

        # 基板材料
        i = 0
        shield_ids = {}
        for s in info_id.impedance_ids:
            s_ids = ''
            for si in s.shield_ids:
                s_ids += si.name + ','
            shield_ids[i] = s_ids
            i += 1

        return {
            'structure_lines': structure_lines,
            'line_explain': line_explain,
            'board_format_ids':board_format_ids,
            'shield_ids':shield_ids,
        }

class report_pcb_info(osv.AbstractModel):
    _name = 'report.mtlcs_sale.report_pcb_info_impedance'
    _inherit = 'report.abstract_report'
    _template = 'mtlcs_sale.report_pcb_info_impedance'
    _wrapped_report_class = parser_pcb_info_impedance

###############################################################################
