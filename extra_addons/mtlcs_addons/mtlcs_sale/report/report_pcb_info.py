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

class parser_pcb_info(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(parser_pcb_info, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'multi_selection_data': self._get_multi,
        })

    def _get_multi(self, info_id):

        # 特殊工艺
        special_tech_ids = ''
        for s in info_id.special_tech_ids:
            special_tech_ids += (' ' + s.name)

        # 基板材料
        board_format_ids = ''
        for s in info_id.board_format_ids:
            board_format_ids += (' ' + s.name)

        # 铜厚
        structure_lines = []
        for s in info_id.structure_lines:
            if (s.cu_thick_base >= 0):
                structure_lines.append(s.cu_thick_base)
        structure_lines.sort()

        # 涂层厚度及要求
        surface_coating_add = ''
        if info_id.surface_coating:
            if 'au' in info_id.surface_coating.code:
                surface_coating_add += u'au:' + str(info_id.au_thick) + u'µ"、'
            if 'a2u' in info_id.surface_coating.code:
                surface_coating_add += u'au2:' + str(info_id.au_thick_2) + u'µ"、 '
            if 'ni' in info_id.surface_coating.code:
                surface_coating_add += u'ni:' + str(info_id.ni_thick) + u'µ"、 '
            if 'n2i' in info_id.surface_coating.code:
                surface_coating_add += u'ni2:' + str(info_id.ni_thick_2) + u'µ"、 '
            if 'ag' in info_id.surface_coating.code:
                surface_coating_add += u'ag:' + str(info_id.ag_thick) + u'µ"、 '
            if 'sn' in info_id.surface_coating.code:
                surface_coating_add += u'sn:' + str(info_id.sn_thick) + u'µ"、 '
            surface_coating_add += str(info_id.surface_percent) + u'%'

        # 附货要求
        misc_ids = ''
        for s in info_id.misc_ids:
            misc_ids += ' ' + s.name

        # ET章
        # test_et = info_id.test_et and u'加盖ET章' or ''

        # 包装要求
        packing_re = ''
        if info_id.packing_inner:
            packing_re = u'内包装：'
            for p in info_id.packing_inner:
                packing_re += (' ' + p.name)
            for p in info_id.packing_inner_requires:
                packing_re += (' ' + p.name)
        if info_id.packing_outer:
            packing_re += (u' 外包装：' + info_id.packing_outer.name)

        # 过线孔阻焊
        via_solder_pad = ''
        via_solder_hole = ''
        via_solder_pad_list = \
            self.pool.get('pcb.info').fields_get(self.cr, self.uid, allfields=['via_solder_pad'], context={})[
                'via_solder_pad']['selection']
        for s in via_solder_pad_list:
            if info_id.via_solder_pad == s[0]:
                via_solder_pad = u'焊盘：' + s[1]

        via_solder_hole_list = \
            self.pool.get('pcb.info').fields_get(self.cr, self.uid, allfields=['via_solder_hole'], context={})[
                'via_solder_hole']['selection']
        for s in via_solder_hole_list:
            if info_id.via_solder_hole == s[0]:
                via_solder_hole = u'孔：' + s[1]

        # 标记要求
        mark_ids = ''
        for s in info_id.mark_ids:
            mark_ids += (' ' + s.name)


        return {
            'special_tech_ids': special_tech_ids,
            'board_format_ids': board_format_ids,
            'cu_thick_inside': len(structure_lines) and structure_lines[0]or'',
            'surface_coating_add': surface_coating_add,
            'misc_ids': misc_ids,
            'test_et': info_id.test_et and u'加盖ET章' or '',
            'packing_re': packing_re,
            'via_solder_pad': via_solder_pad,
            'via_solder_hole': via_solder_hole,
            'mark_ids':mark_ids
        }

class report_pcb_info(osv.AbstractModel):
    _name = 'report.mtlcs_sale.report_pcb_info'
    _inherit = 'report.abstract_report'
    _template = 'mtlcs_sale.report_pcb_info'
    _wrapped_report_class = parser_pcb_info

###############################################################################
