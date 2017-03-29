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
from decimal import Decimal

class parse_sale_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(parse_sale_order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'sale_order_data': self._get_sale_order_data,
        })

    # 人民币小写转换成大写
    def cncurrency(self, value):
        # 汉字金额字符定义
        dunit = [u'角', u'分']
        num = [u'零', u'壹', u'贰', u'叁', u'肆', u'伍', u'陆', u'柒', u'捌', u'玖']
        iunit = [None, u'拾', u'佰', u'仟', u'万', u'拾', u'佰', u'仟',u'亿', u'拾', u'佰', u'仟', u'万', u'拾', u'佰', u'仟']
        iunit[0] = u'圆'
        # 转换为Decimal，并截断多余小数
        if not isinstance(value, Decimal):
            value = Decimal(value).quantize(Decimal('0.01'))
        # 转化为字符串
        s = str(value)
        if len(s) > 19:
            raise ValueError(u'金额太大，无法表述。')
        istr, dstr = s.split('.')  # 小数部分和整数部分分别处理
        istr = istr[::-1]  # 翻转整数部分字符串
        so = []  # 用于记录转换结果
        # 零
        if value == 0:
            return num[0] + iunit[0]
        haszero = False  # 用于标记零的使用
        if dstr == '00':
            haszero = True  # 如果无小数部分，则标记加过零，避免出现“圆零整”
        # 处理小数部分
        # 分
        if dstr[1] != '0':
            so.append(dunit[1])
            so.append(num[int(dstr[1])])
        else:
            so.append(u'整')  # 无分，则加“整”
        # 角
        if dstr[0] != '0':
            so.append(dunit[0])
            so.append(num[int(dstr[0])])
        elif dstr[1] != '0':
            so.append(num[0])  # 无角有分，添加“零”
            haszero = True  # 标记加过零了
        # 无整数部分
        if istr == '0':
            if haszero:  # 既然无整数部分，那么去掉角位置上的零
                so.pop()
            so.reverse()  # 翻转
            return ''.join(so)
        # 处理整数部分
        for i, n in enumerate(istr):
            n = int(n)
            if i % 4 == 0:  # 在圆、万、亿等位上，即使是零，也必须有单位
                if i == 8 and so[-1] == iunit[4]:  # 亿和万之间全部为零的情况
                    so.pop()  # 去掉万
                so.append(iunit[i])
                if n == 0:  # 处理这些位上为零的情况
                    if not haszero:  # 如果以前没有加过零
                        so.insert(-1, num[0])  # 则在单位后面加零
                        haszero = True  # 标记加过零了
                else:  # 处理不为零的情况
                    so.append(num[n])
                    haszero = False  # 重新开始标记加零的情况
            else:  # 在其他位置上
                if n != 0:  # 不为零的情况
                    so.append(iunit[i])
                    so.append(num[n])
                    haszero = False  # 重新开始标记加零的情况
                else:  # 处理为零的情况
                    if not haszero:  # 如果以前没有加过零
                        so.append(num[0])
                        haszero = True
        # 最终结果
        so.reverse()
        return ''.join(so)

    def _get_sale_order_data(self, o):

        # 基板材料
        board_format_ids = {}
        # 特殊工艺
        special_tech_ids = {}
        # 过线孔阻焊
        via_solder_all = {}
        # 验收标准
        acceptance_standard_id = ''
        # 包装要求
        packing_all = ''
        # 特殊说明
        special_note_all = ''
        # 交货日期
        delivery_date_all = {}
        i = 0

        # 获取过线孔阻焊列表
        via_solder_pad_list = \
            self.pool.get('pcb.info').fields_get(self.cr, self.uid, allfields=['via_solder_pad'], context={})[
                'via_solder_pad']['selection']
        via_solder_hole_list = \
            self.pool.get('pcb.info').fields_get(self.cr, self.uid, allfields=['via_solder_hole'], context={})[
                'via_solder_hole']['selection']

        for s in o.order_line:
            # 发货日期
            delivery_date = str(s.price_id.delivery_date)[0:10]
            delivery_date_all.update({i: delivery_date})
            for pid in s.price_id.info_id:
                board_name = ''
                special_name = ''
                packing_re = ''
                via_solder_pad = ''
                via_solder_hole = ''
                # 基板材料
                if pid.board_format_ids:
                    for b in pid.board_format_ids:
                        board_name += (' ' + b.name)
                # 特殊工艺
                if pid.special_tech_ids:
                    for sti in pid.special_tech_ids:
                        special_name += (' ' + sti.name)
                # 验收标准
                if pid.acceptance_standard_id:
                    acceptance_standard_id += str(i+1) + ':' + pid.acceptance_standard_id.name
                # 包装要求
                if pid.packing_inner:
                    packing_re = str(i+1) + ':' + u'内包装:'
                    for p in pid.packing_inner:
                        packing_re += (' ' + p.name)
                    for p in pid.packing_inner_requires:
                        packing_re += (' ' + p.name)
                if pid.packing_outer:
                    packing_re += (u' 外包装:' + pid.packing_outer.name)
                packing_all += packing_re
                # 过线孔阻焊
                for vs in via_solder_pad_list:
                    if pid.via_solder_pad == vs[0]:
                        via_solder_pad = vs[1]
                for vs in via_solder_hole_list:
                    if pid.via_solder_hole == vs[0]:
                        via_solder_hole = vs[1]
                # 特殊说明
                if pid.special_note_quality or pid.special_note_package or pid.special_note_technical:
                    special_note_all += str(i + 1) + ':'
                    if pid.special_note_quality:
                        special_note_all +=  pid.special_note_quality
                    if pid.special_note_package:
                        special_note_all += pid.special_note_package
                    if pid.special_note_technical:
                        special_note_all += pid.special_note_technical

            board_format_ids.update({i: board_name})
            special_tech_ids.update({i: special_name})
            via_solder_all.update({i: via_solder_pad + via_solder_hole})
            i += 1

        # # 铜厚
        # structure_lines = []
        # for s in info_id.structure_lines:
        #     if (s.cu_thick_base >= 0):
        #         structure_lines.append(s.cu_thick_base)
        # structure_lines.sort()

        return {
            'special_tech_ids': special_tech_ids,
            'board_format_ids': board_format_ids,
            'amount_total': self.cncurrency(o.amount_total),
            # 'cu_thick_inside':structure_lines[0],
            'packing_all': packing_all,
            'via_solder_all':via_solder_all,
            'acceptance_standard_id': acceptance_standard_id,
            'special_note_all': special_note_all,
            'delivery_date_all':delivery_date_all,
        }

class report_sale_order(osv.AbstractModel):
    _name = 'report.mtlcs_sale.report_sale_order'
    _inherit = 'report.abstract_report'
    _template = 'mtlcs_sale.report_sale_order'
    _wrapped_report_class = parse_sale_order

###############################################################################
