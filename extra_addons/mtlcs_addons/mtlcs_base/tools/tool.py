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
import warnings
from decimal import Decimal

CNumber = {
'0':r'/',
'1':u'壹',
'2':u'贰',
'3':u'叁',
'4':u'肆',
'5':u'伍',
'6':u'陆',
'7':u'柒',
'8':u'捌',
'9':u'玖',
}

def number2china(f, p1=10, p2=2):
    s = '%.*f' % (p2, f)
    long = f < 0 and  p1 + p2 + 1 or p1 + p2
    chine = tuple([CNumber[i] for i in s.zfill(long) if i.isalnum()])
    return chine

def cncurrency(value, capital=True, prefix=False, classical=None):
    if not isinstance(value, (str, int, long, float)):
        warnings.warn(u'%s 不是数字'  % value)
# 默认大写金额用圆，一般汉字金额用元
    if classical is None:
        classical = True if capital else False
# 汉字金额前缀
    if prefix is True:
        prefix = '人民币'
    else:
        prefix = ''
# 汉字金额字符定义
    dunit = ('角', '分')
    if capital:
        num = ('零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖')
        iunit = [None, '拾', '佰', '仟', '万', '拾', '佰', '仟',
                '亿', '拾', '佰', '仟', '万', '拾', '佰', '仟']
    else:
        num = ('〇', '一', '二', '三', '四', '五', '六', '七', '八', '九')
        iunit = [None, '十', '百', '千', '万', '十', '百', '千',
                '亿', '十', '百', '千', '万', '十', '百', '千']
    if classical:
        iunit[0] = '圆' if classical else '元'
# 转换为Decimal，并截断多余小数
    if not isinstance(value, Decimal):
        value = Decimal(value).quantize(Decimal('0.01'))
# 处理负数
    if value < 0:
        prefix += '负'          # 输出前缀，加负
        value = - value         # 取正数部分，无须过多考虑正负数舍入
                            # assert - value + value == 0
# 转化为字符串
    s = str(value)
    if len(s) > 19:
        raise ValueError('金额太大了，不知道该怎么表达。')
    istr, dstr = s.split('.')           # 小数部分和整数部分分别处理
    istr = istr[::-1]                   # 翻转整数部分字符串
    so = []     # 用于记录转换结果
    # 零
    if value == 0:
        return prefix + num[0] + iunit[0]
    haszero = False     # 用于标记零的使用
    if dstr == '00':
        haszero = True  # 如果无小数部分，则标记加过零，避免出现“圆零整”
# 处理小数部分
# 分
    if dstr[1] != '0':
        so.append(dunit[1])
        so.append(num[int(dstr[1])])
    else:
        so.append('整')         # 无分，则加“整”
# 角
    if dstr[0] != '0':
        so.append(dunit[0])
        so.append(num[int(dstr[0])])
    elif dstr[1] != '0':
        so.append(num[0])       # 无角有分，添加“零”
        haszero = True          # 标记加过零了
# 无整数部分
    if istr == '0':
        if haszero:             # 既然无整数部分，那么去掉角位置上的零
            so.pop()
        so.append(prefix)       # 加前缀
        so.reverse()            # 翻转
        return ''.join(so)
# 处理整数部分
    for i, n in enumerate(istr):
        n = int(n)
        if i % 4 == 0:          # 在圆、万、亿等位上，即使是零，也必须有单位
            if i == 8 and so[-1] == iunit[4]:   # 亿和万之间全部为零的情况
                so.pop()                        # 去掉万
            so.append(iunit[i])
            if n == 0:                          # 处理这些位上为零的情况
                if not haszero:                 # 如果以前没有加过零
                    so.insert(-1, num[0])       # 则在单位后面加零
                    haszero = True              # 标记加过零了
            else:                               # 处理不为零的情况
                so.append(num[n])
                haszero = False                 # 重新开始标记加零的情况
        else:                                   # 在其他位置上
            if n != 0:                          # 不为零的情况
                so.append(iunit[i])
                so.append(num[n])
                haszero = False                 # 重新开始标记加零的情况
            else:                               # 处理为零的情况
                if not haszero:                 # 如果以前没有加过零
                    so.append(num[0])
                    haszero = True

# 最终结果
    so.append(prefix)
    so.reverse()
    return ''.join(so)
####################################################################################

# hash = {
# '/': u'/',
# '0':u'零',
# '1':u'壹',
# '2':u'贰',
# '3':u'叁',
# '4':u'肆',
# '5':u'伍',
# '6':u'陆',
# '7':u'柒',
# '8':u'捌',
# '9':u'玖',
# }
# t_int = u'%s亿%s仟%s佰%s拾%s万%s仟%s佰%s拾%s圆'
# t_decimal = u'%s角%s分'
# def number2china(v, dsize=2):
#     def drop_pre_zero(s):
#         while s[0] == '/' and len(s) > 2:
#             return drop_pre_zero( s[2:] )
#         else:
#             return s
#
#     def drop_mid_zero(s):
#         s.search(u'零')
#
#     f= round(float(v), 2)
#     s1, s2  = str(f).split('.')
#     s1 = s1.rjust(t_int.count('%s'), '/')
#     ss1 = t_int % ( tuple([hash[i] for i in s1]))
#
#     cn_number = drop_mid_zero( drop_pre_zero(ss1) )
#
#     return cn_number
