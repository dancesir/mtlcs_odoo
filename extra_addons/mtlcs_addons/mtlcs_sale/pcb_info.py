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
from openerp import tools, _
from openerp.exceptions import Warning
from openerp.tools.config import config
import pymssql


PCB_UNIT = [
    ('mil','mil'),
    ('oz', 'oz'),
]

class blind_line(osv.osv):
    _name = 'blind.line'
    _columns = {
        'name': fields.char(u'name', size=16),
        'info_id': fields.many2one('pcb.info', u'用户单'),
        'start_id': fields.many2one('layer.structure.line', u'开始层', required=True),
        'end_id': fields.many2one('layer.structure.line', u'结束层', required=True),
    }

class layer_structure_line(osv.osv):
    _name = 'layer.structure.line'
    _order = 'sequence,name'

    def _name_compute(self, cr, uid, ids, fields_name, arg=None, context=None):
        res = {}
        for i in self.browse(cr, uid, ids, context=context):
            res[i.id] = 'L%s' % i.layer_number
        return res
    _columns = {
        #'name': fields.char(u'名称', size=32, required=True),
        'name': fields.function(_name_compute, type="char", string=u'名称', size=32,),
        'layer_number': fields.integer(u'第几层', required=True, readonly=True),
        'sequence': fields.integer(u'序号', ),
        'type': fields.selection([('cu', u'铜皮'),('pp', u'PP'),('core', u'芯板')], u'类型', required=True),
        #'material_id': fields.many2one
        'cu_thick_base': fields.float(u'基铜厚:μm'),
        'cu_thick_finish': fields.float(u'成品铜厚:μm'),
        'thick': fields.float(u'成品厚度'),
        'unit': fields.selection(PCB_UNIT, u'单位'),
        'info_id': fields.many2one('pcb.info', u'用户单', required=True),
    }

    _defaults = {
        'type': 'cu',
    }

class impedance_line(osv.osv):
    _name = 'impedance.line'
    _columns = {
        'name': fields.char(u'Name', size=32),
        'type': fields.selection([('one',u'单端'),('two',u'差分')], u'类型', required=True),
        'layer_id': fields.many2one('layer.structure.line', u'控制层', required=True),
        'shield_ids': fields.many2many('layer.structure.line', 'imp_struct_ref', 'struct_id', 'imp_id',  u'屏蔽层'),
        'v_customer': fields.char(u'客户要求值', size=32, required=True),
        'v_design':  fields.char(u'设计值', size=32),
        'v_compute': fields.char(u'阻抗计算值',size=32),
        'info_id': fields.many2one('pcb.info', u'用户单', required=True),
    }


class pcb_misc_parts(osv.osv):
    '''
    附货报告和其他物件
    '''
    _name = 'pcb.misc.parts'
    _columns = {
        'name': fields.char('Name', size=64),
        'code': fields.char('Code', size=64),
    }
    _sql_constraints = [
        ('code_uniq', 'unique(code)', u'Code不能重复'),
    ]


class product_uom(osv.osv):
    _inherit = 'product.uom'
    def get_pcb_sale_unit(self, cr,  uid, panel_qty, context=None):
        unit_id = False
        name = str(panel_qty) + 'Unit/PCS'
        ids = self.search(cr, uid, [('category_id.name','=','PCB'),('uom_type','=','bigger'),('name','=',name)], limit=1)
        if ids:
            unit_id = ids[0]
        else:
            category_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mtlcs_sale', 'uom_categ_pcb')[1],
            unit_id = self.create(cr, uid, {
                'name':name,
                'category_id': category_id,
                'uom_type': 'bigger',
                'factor_inv': panel_qty,
            })
        return unit_id


###########################################################
Info_State = [
    ('draft', u'草稿'),
    ('w_director', u'待主管'),
    ('done', u'完成'),
    ('cancel', u'作废'),
    ('w_change', u'待更改')]


class pcb_info(osv.osv):
    _inherits = {'receive.order': 'receive_id'}
    _name = "pcb.info"

    def compute_max_cu_thick(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for info in self.browse(cr, uid, ids, context=context):
            res[info.id] = info.structure_lines and max([x.cu_thick_finish or x.cu_thick_base for x in info.structure_lines])
        return res

    def _compute_density(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for info in self.browse(cr, uid, ids, context=context):
            res[info.id] = {}
            panel_area = info.length * info.width
            hole_count = info.hole_count + info.slot_count*20
            res[info.id]['hole_density'] = panel_area and  hole_count / panel_area or 0
            res[info.id]['tp_density'] = panel_area and info.tp_count / panel_area or 0

        # print '>>>>>>>>>>>>>>>>>',res


        return res

    def compute_blind(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        for info in self.browse(cr, uid, ids, context=context):
            res[info.id] = info.blind_lines and len(info.blind_lines) or 0
        return res

    def _compute_panel_count(self, cr, uid, ids, field_name, arg=None, context=None):
        uom_obj = self.pool.get('product.uom')
        res = {}
        for info in self.browse(cr, uid, ids, context=context):
            res[info.id] = {}
            qty = (info.x_count and info.y_count) and info.x_count * info.y_count or 1
            res[info.id]['panel_count'] = qty
            res[info.id]['sale_unit_id'] = (qty > 1) and uom_obj.get_pcb_sale_unit(cr, uid, qty) or info.uom_id.id
            res[info.id]['panel_area'] = info.length * info.width
        return res

    _columns = {
        'name': fields.char(u'用户单', size=32, readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],},  ),
        'uom_id': fields.many2one('product.uom', u'基本单位'),


        'state': fields.selection(Info_State, u'状态'),
        'product_id': fields.many2one('product.product', u'档案号', readonly=True, states={'draft':[('readonly',False)], 'w_change': [('readonly',False)],}),  # 用户单是潜在的，客户没有确认的档案号，即产品
        'fnumber_ok': fields.boolean(string=u'已建立真实档案号', readonly=False),
        'receive_id': fields.many2one('receive.order', u'接单', required=True, ondelete="restrict", readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'to_company_id': fields.many2one('res.company', u'投产工厂', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),

        'soft_version_id': fields.many2one('soft.version', u'软件版本', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],} ),

        'create_uid': fields.many2one('res.users', u'创建人', readonly=True),
        'user_id': fields.many2one('res.users', u'订单管理员', readonly=True),
        'create_date': fields.datetime(u'创建日期', readonly=True),
        'layer_count': fields.integer(u'层数', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),  # 层数
        'board_format_ids': fields.many2many('product.attribute.value', 'pav_pcb_info_ref', 'inof_id', 'value_id',
                                             string=u'基板材料',  domain=[('attribute_id.code', '=', 'ccl_type')], readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'base_board_thick': fields.float(u'基板厚度:mm', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'board_from_customer': fields.boolean(u'客供板材', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'board_usage_rate': fields.float(u'板材利用率:%', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),

        'finish_thick': fields.float(u'成品板厚:mm', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),  #
        'finish_thick_tolu': fields.float(u'+公差:mm', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),  #
        'finish_thick_told': fields.float(u'-公差:mm', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),  #

        'have_finger': fields.boolean(u'有金手指', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],} ),  # 金手指
        'finger_qty': fields.integer(u'手指数/PCS', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'finger_au_thick': fields.float(u'手指金厚:µ"', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'finger_ni_thick': fields.float(u'手指镍厚:µ"', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'finger_length': fields.float(u'手指长:mm', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],} ),
        'finger_width': fields.float(u'手指宽:mm', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'finger_angle': fields.selection([(30, '30'), (45, '45'), (60, '60')], u'手指斜边:°', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'finger_note': fields.char(u'金手指备注', size=64, readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),

        'plot_count': fields.integer(u'菲林张数', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'fill_core_count': fields.integer(u'填充芯板', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),  # TODO 可以根据材料自动判断
        'fill_pp_count': fields.integer(u'填充PP', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),  # TODO 可以根据材料自动判断

        'min_line_width': fields.float(u'最小线宽:mil', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],} ),  #
        'min_line_space': fields.float(u'最小线距:mil', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),  #
        'min_line2pad': fields.float(u'最小线到Pad:mil', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),  #
        'min_finish_hole': fields.float(u'最小成品孔径:mm', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),  #
        'min_hole2line': fields.float(u'最小孔到线:mil', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),  #
        'min_via_ring': fields.float(u'最小过孔焊环:mil', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),  #
        'min_pth_ring': fields.float(u'最小器件孔焊环:mil', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),  #

        'is_spacial_material': fields.boolean(u'特殊材料', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),  # TODO 可以根据材料自动判断
        'is_htg': fields.boolean(u'高TG', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),  # TODO 可以根据材料自动判断
        # 'is_rigid_and_fixible': fields.boolean(u'刚柔结合'), 和特殊工艺重复
        'is_mix_press': fields.boolean(u'混压', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),  # TODO 可以根据材料自动判断
        'need_impedance_test': fields.boolean(u'阻抗测试', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'need_steel_stencil': fields.boolean(u'提供钢网', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'need_confirm_gerber': fields.boolean(u'确认Gerber', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'need_provide_gerber': fields.boolean(u'提供Gerber', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        # 'need_delivery_chapter': fields.boolean(u'加发货章'),

        'solder_color': fields.many2one('product.attribute.value', u'阻焊颜色', domain=[('attribute_id.code', '=', 'solder_color')], readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),  # 阻焊颜色
        'solder_format': fields.many2one('product.attribute.value', u'阻焊油墨', domain=[('attribute_id.code', '=', 'solder_format')], readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),  # 阻焊油墨型号
        'solder_type': fields.many2one('technic.tag', u'阻焊类型', domain=[('attribute_id.code', '=', 'solder_type')], readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'via_solder_pad': fields.selection([(1, u'覆盖'), (2, u'不覆盖'), (3, u'覆盖焊盘不覆盖孔')], u'过孔阻焊:焊盘', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'via_solder_hole': fields.selection([(1, u'塞孔'), (2, u'不塞孔')], u'过孔阻焊:孔', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),

        'legend_color': fields.many2one('product.attribute.value', u'字符颜色', domain=[('attribute_id.code', '=', 'legend_color')], readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'legend_format': fields.many2one('product.attribute.value', u'字符油墨', domain=[('attribute_id.code', '=', 'legend_format')], readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'legend_type': fields.many2one('technic.tag', u'字符类型', domain=[('attribute_id.code', '=', 'legend_type')], readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),

        'test_ids': fields.many2many('technic.attribute', 'tech_attr_pcb_info_ref_test', 'info_id', 'attr_id', string=u'功能测试',
                                     domain=[('technic_id.code', '=', 'function_test')], readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'test_id': fields.many2one('technic.attribute', u'通断测试', domain=[('technic_id.code', '=', 'connected_test')], readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'test_et': fields.boolean(u'ET章', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'tp_count': fields.integer(u'测试点数', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'tp_density': fields.function(_compute_density, type="float", string=u'测试点密度', multi='_compute_density'),

        'hole_count': fields.integer(u'孔数', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'hole_count_small': fields.integer(u'小于0.15孔数', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'hole_cu_thick': fields.integer(u'孔铜要求:µm', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'hole_density': fields.function(_compute_density, type="float", string=u'孔密度', multi='_compute_density', readonly=True  ),
        # 'shape_ids': fields.many2many('technic.attribute', 'tech_attr_pcb_info_ref_shape', 'info_id', 'attr_id', u'外形加工', domain=[('technic_id.code','=','shape')]),
        'shape_id': fields.many2one('technic.attribute', u'外形加工', domain=[('technic_id.code', '=', 'shape')], readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),

        'rout_length': fields.float(u'锣长:cm', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'slot_count': fields.integer(u'槽孔数', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),

        'surface_coating': fields.many2one('technic.attribute', u'表面涂层', domain=[('technic_id.code', '=', 'surface_treatment')], readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'surface_percent': fields.integer(u'镀层面积比:%', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),

        'au_thick': fields.float(u'金厚:µ"', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'ni_thick': fields.float(u'镍厚:µ"', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'au_thick_2': fields.float(u'金厚:µ"', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'ni_thick_2': fields.float(u'镍厚:µ"', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'pd_thick': fields.float(u'钯厚:µ"', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'sn_thick': fields.float(u'锡厚:µ"', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'ag_thick': fields.float(u'银厚:µ"', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'show_au_thick': fields.boolean(string=u'金厚:µ"', type='boolean', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'show_ni_thick': fields.boolean(string=u'镍厚:µ"', type='boolean', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'show_au_thick_2': fields.boolean(string=u'电金厚:µ"', type='boolean', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'show_ni_thick_2': fields.boolean(string=u'电镍厚:µ"', type='boolean', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'show_pd_thick': fields.boolean(string=u'钯厚:µ"', type='boolean', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'show_sn_thick': fields.boolean(string=u'锡厚:µ"', type='boolean', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'show_ag_thick': fields.boolean(string=u'银厚:µ"', type='boolean', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),

        'coating_request': fields.char(u'涂层描述', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),

        'uom_id': fields.many2one('product.uom', u'Unit', domain=[('category_id.name', '=', 'PCB')]),
        'uos_id': fields.many2one('product.uom', u'PCS Unit数量', domain=[('category_id.name', '=', 'PCB')]),
        'length': fields.float(u'拼版长:cm', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'width': fields.float(u'拼版宽:cm', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),

        'unit_length': fields.float(u'Unit长:cm', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'unit_width': fields.float(u'Unit宽:cm', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'x_count': fields.integer(u'X拼数', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'y_count': fields.integer(u'Y拼数', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'panel_count': fields.function(_compute_panel_count, type='integer', string='拼版数', multi='_compute_panel_count'),
        'panel_area': fields.function(_compute_panel_count, type='float', string='PCS面积:c㎡',  multi='_compute_panel_count'),
        'sale_unit_id': fields.function(_compute_panel_count, type='many2one', relation='product.uom', string=u'销售单位',  multi='_compute_panel_count'),

        'vcut_angle': fields.many2one('technic.tag', u'VCUT度:°', domain=[('attribute_id.code', '=', 'v_cut')]),
        'vcut_thick': fields.float(u'VCUT余厚:mm', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),

        'allow_scrap_percent': fields.integer(u'允许报废比:%', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'allow_scrap_count': fields.integer(u'PCS允许报废Unit', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'acceptance_standard_id': fields.many2one('acceptance.standard', u'验收标准', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'mark_ids': fields.many2many('mark.mark', 'mark_info_ref', 'inof_id', 'mark_id', u'标记要求', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'special_tech_ids': fields.many2many('special.technic', 'spe_tech_info_ref', 'inof_id', 'septech_id', u'特殊工艺', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),

        'special_note_quality': fields.text(u'客户特殊品质要求', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'special_note_package': fields.text(u'客户特殊包装要求', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'special_note_technical': fields.text(u'客户特殊加工要求', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),

        #'inner_cu': fields.float(u'内层铜厚'),
        #'out_cu': fields.float(u'外层铜厚'),
        #'finish_inner_cu': fields.float(u'成品内层铜厚'),  # TODO 可以根据材料自动判断
        #'finish_out_cu': fields.float(u'成品外层铜厚'),  # TODO 可以根据材料自动判断

        'packing_inner': fields.many2many('technic.attribute', 'packing_inner_attribute_ref', 'info_id', 'attr_id', string=u'内包装',
                                          domain=[('technic_id.code', '=', 'packing_inner')], readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'packing_inner_requires': fields.many2many('technic.tag', 'inner_req_tag_ref', 'info_id', 'tag_id', u'内包装要求',
                                                   domain=[('attribute_id.code', '=', 'packing_inner')], readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'packing_outer': fields.many2one('technic.attribute', u'外包装', domain=[('technic_id.code', '=', 'packing_outer')], readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),

        'misc_ids': fields.many2many('pcb.misc.parts', 'misc_info_ref', 'info_id', 'misc_id', u'附货要求', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'ref_info_name': fields.char(u'参考前版本号', size=32, readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),

        'structure_lines': fields.one2many('layer.structure.line', 'info_id', u'层结构信息', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],}),
        'max_cu_thick': fields.function(compute_max_cu_thick, type='float', string=u'最大铜厚:μm'),
        'blind_lines': fields.one2many('blind.line', 'info_id',  u'盲埋孔', readonly=True, states={'draft':[('readonly',False)],'w_change': [('readonly',False)],} ),
        'blind_count': fields.function(compute_blind, type="integer", string=u'盲埋孔组数'),

        'impedance_ids': fields.one2many('impedance.line', 'info_id', u'阻抗信息'),

        # 'blind_description': fields.function(compute_blind_description, type='float', string=u'盲孔描述'),
        'synced': fields.boolean(u'已经同步到东烁'),

        'approve_uid': fields.many2one('res.users', u'审核人', readonly=True, ),
        'approve_date': fields.datetime(u'审核日期', readonly=1, ),

    }

    _sql_constraints = [
        ('receive_id_uniq', 'unique(receive_id)', u'接单不能重复'),
        #('product_uniq', 'unique(product_id)', u'档案号不能重复!'),
    ]

    _defaults = {
        'name': lambda self, cr, uid, ctx: self.pool.get('ir.sequence').get(cr, uid, 'pcb.info'),
        'state': 'draft',
        'product_id': lambda self, cr, uid, ctx: self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mtlcs_sale', 'dummy_pcb_product')[1],
        'uom_id': lambda self, cr, uid, ctx: self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mtlcs_sale', 'pcb_uom_unit')[1],
    }

    ####operation
    def make_structure_lines(self, cr, uid, ids, context=None):
        me = self.browse(cr, uid, ids[0], context=None)
        if me.layer_count <=1:
            raise Warning(u'层数不能小于1')

        return {
            'type': 'ir.actions.act_window',
            'name': u'订单',
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'wizard.layer.structure',
            'target': 'new',
        }


    def _check(self, cr, uid, ids, context=None):

        info = self.browse(cr, uid, ids[0], context=None)

        for i in info:
            if i.board_usage_rate < 0 or i.board_usage_rate > 1:
                raise Warning(u'板材利用率必须大于0小于1')

            if i.fill_core_count < 0:
                raise Warning(u'填充芯板不能小于1')

            if i.fill_pp_count < 0:
                raise Warning(u'填充PP不能小于0')

            if i.layer_count < 0:
                raise Warning(u'层数不能小于0')

            if i.plot_count < 0:
                raise Warning(u'菲林张数不能小于0')

            if i.min_line_width < 0:
                raise Warning(u'最小线宽不能小于0')

            if i.min_line_space < 0:
                raise Warning(u'最小线距不能小于0')

            if i.min_hole2line < 0:
                raise Warning(u'最小孔到线不能小于0')

            if i.min_finish_hole < 0:
                raise Warning(u'最小成品孔径不能小于0')

            if i.hole_count < 0:
                raise Warning(u'孔数不能小于1')

            if i.hole_count_small < 0:
                raise Warning(u'小于0.15孔数不能小于1')

            if i.slot_count < 0:
                raise Warning(u'槽孔数不能小于1')

            if i.vcut_thick < 0:
                raise Warning(u'VCUT余厚不能小于0')

            if i.tp_count < 0:
                raise Warning(u'测试点数不能小于1')

            if i.base_board_thick < 0:
                raise Warning(u'基板厚度不能小于0')

            if i.finish_thick < 0:
                raise Warning(u'成品板厚不能小于0')

            if i.finish_thick_tolu < 0:
                raise Warning(u'正公差不能小于0')

            if i.finish_thick_told < 0:
                raise Warning(u'负公差不能小于0')

            if i.unit_length < 0:
                raise Warning(u'Unit长:CM不能小于0')

            if i.unit_width < 0:
                raise Warning(u'Unit宽:CM不能小于0')

            if i.unit_width < 0:
                raise Warning(u'Unit宽:CM不能小于0')

            if i.length < 0:
                raise Warning(u'拼版长CM:不能小于0')

            if i.width < 0:
                raise Warning(u'拼版宽CM:不能小于0')

            if i.x_count < 0:
                raise Warning(u'X拼数不能小于1')

            if i.y_count < 0:
                raise Warning(u'Y拼数不能小于1')

            if i.allow_scrap_percent < 0  or i.allow_scrap_percent > 100 :
                raise Warning(u'允许报废比%不能小于0大于100')

            if i.allow_scrap_count < 0:
                raise Warning(u'允许报废数量不能小于1')

            if i.max_cu_thick < 0:
                raise Warning(u'结构信息：铜厚不能小于0')

            if i.blind_count < 0:
                raise Warning(u'盲埋孔信息：盲埋孔组数不能小于1')

            if i.surface_coating:
                if ('au' and 'ni') in i.surface_coating.code:
                    info.sn_thick = 0.0
                    info.ag_thick = 0.0
                    if  i.au_thick < 0:
                        raise Warning(u'表面涂层：金厚不能小于0')
                    if i.ni_thick < 0:
                        raise Warning(u'表面涂层：镍厚不能小于0')
                elif 'sn' in i.surface_coating.code:
                    info.ag_thick = 0.0
                    info.au_thick = 0.0
                    info.ni_thick = 0.0
                    if  i.sn_thick < 0:
                        raise Warning(u'表面涂层：锡厚不能小于0')
                elif 'ag' in i.surface_coating.code:
                    info.sn_thick = 0.0
                    info.au_thick = 0.0
                    info.ni_thick = 0.0
                    if  i.ag_thick < 0:
                        raise Warning(u'表面涂层：银厚不能小于0')
                elif 'osf' in i.surface_coating.code:
                    info.sn_thick = 0.0
                    info.au_thick = 0.0
                    info.ag_thick = 0.0
                    info.ni_thick = 0.0

            if i.surface_percent < 0 or i.surface_percent > 100:
                raise Warning(u'镀层面积比%不能小于0大于100')

            if i.have_finger:
                if i.finger_qty <= 0:
                    raise Warning(u'金手指：数量/PCS不能小于1')
                if i.finger_au_thick <= 0:
                    raise Warning(u'金手指：金厚不能小于0')
                if i.finger_ni_thick < 0:
                    raise Warning(u'金手指：镍厚不能小于0')
                if i.finger_length <= 0:
                    raise Warning(u'金手指：长mm不能小于0')
                if i.finger_width <= 0:
                    raise Warning(u'金手指：宽mm不能小于0')
            else:
                info.finger_qty = 0
                info.finger_angle = ''
                info.finger_au_thick = 0.0
                info.finger_ni_thick = 0.0
                info.finger_length = 0.0
                info.finger_width = 0.0

        return True


    def onchange_surface_coating(self, cr, uid, ids, surface_coating, context=None):
        if not surface_coating:
            return True
        surface = self.pool.get('technic.attribute').browse(cr, uid, surface_coating)
        value = {
            'show_au_thick': 'au' in surface.code,
            'show_ni_thick': 'ni' in surface.code,
            'show_au_thick_2': 'a2u' in surface.code,
            'show_ni_thick_2': 'n2i' in surface.code,
            'show_pd_thick': 'pd' in surface.code,
            'show_sn_thick': 'sn' in surface.code,
            'show_ag_thick': 'ag' in surface.code,
        }
        return {'value': value}

    def onchange_finish_thick(self, cr, uid, ids, finish_thick, context=None):
        return {'value': {'finish_thick_tolu': 0, 'finish_thick_told': 0}}

    def confirm(self, cr, uid, ids, context=None):
        self._check(cr, uid, ids, context=None)
        self.write(cr, uid, ids, {'state': 'w_director'})

    def director_approve(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        receive_obj = self.pool.get('receive.order')
        info = self.browse(cr, uid, ids[0], context=context)
        if info.receive_id.state == 'w_info':
            receive_obj.to_price(cr, uid, [info.receive_id.id, ], context=context)
        self.write(cr, uid, info.id, {
            'state': 'done',
            'approve_uid': uid,
            'approve_date': fields.datetime.now(),
        })
        return True

    def to_cancel(self, cr, uid, ids, context=None):
        for info in self.browse(cr, uid, ids, context=context):
            # TODO do some check
            self.write(cr, uid, info.id, {'state': 'cancel'}, context=context)
        return True

    def to_draft(self, cr, uid, ids, context=None):
        for info in self.browse(cr, uid, ids, context=context):
            # TODO do some check
            self.write(cr, uid, info.id, {'state': 'draft'}, context=context)
        return True

    def set_w_change(self, cr, uid, ids, context=None):
        for info in self.browse(cr, uid, ids, context=context):
            # TODO do some check
            self.write(cr, uid, info.id, {'state': 'w_change'}, context=context)
        return True

    def set_change_finish(self, cr, uid, ids, context=None):
        for info in self.browse(cr, uid, ids, context=context):
            # TODO do some check
            self.write(cr, uid, info.id, {'state': 'done'}, context=context)
        return True



    def make_product(self, cr, uid, info_id, context=None, info=None):
        pdt_obj = self.pool.get('product.product')
        categ_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'material', 'product_category_finish')[1]
        info = info or self.browse(cr, uid, info_id, context=context)
        product_id = pdt_obj.create(cr, uid, self._prepare_product(cr, uid, info, context=context), context=context)
        self.write(cr, uid, info.id, {'product_id': product_id, 'fnumber_ok': True})
        return product_id

    def _prepare_product(self, cr, uid, info, context=None):
        categ_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'material', 'product_category_finish')[1]

        def _get_code(info):
            layer_count = info.layer_count
            pre = layer_count == 2 and 'd' or layer_count > 2 and 'm' or 's'
            return self.pool.get('ir.sequence').get(cr, uid, 'file.number.%s' % pre)

        if info.fnumber_ok:
            raise Warning(u'正式档案号已经存在')

        default_code = _get_code(info)
        return {
            'name': info.ref or default_code,
            'default_code': default_code,
            'pcb_info_id': info.id,
            'categ_id': categ_id,
            'sale_ok': True,
            'purchase_ok': False,
            'active': True,
            'uom_id': info.uom_id.id,
            'uom_po_id': info.uom_id.id,
            'uos_id': info.sale_unit_id.id,
        }


    def sync_to_dongshuo(self, cr, uid, ids, context=None):
        mssql_str =  config.options.get('dongshuo_connect','')
        print mssql_str, type(mssql_str)
        connect_arg = eval(eval(mssql_str))
        print connect_arg, type(connect_arg)
        conn = pymssql.connect(**connect_arg)



        column=[]
        if type(ids) == type(column):
            info = self.browse(cr, uid, ids[0])
        else:
            info = self.browse(cr, uid, ids)
        info_board_material=  ','.join([x.name for x in info.board_format_ids])


        billcode = info.name
        column.append(billcode)
        column.append(info.layer_count)
        column.append(info_board_material)
        row=[]
        for i in range(len(column)):
           if type(column[i])==type(u'中文'):
                 row.append((column[i]).encode('utf-8'))
           else:
                 row.append(column[i])
        row=tuple(row)

        print u'-------', info_board_material
        #更新product.attribute.value(198,) product.attribute.value(201,)

        print row
        try:
            #conn = pymssql.connect(server=server, user=user, password=password, database=database)
            cur = conn.cursor()
            sql = '''exec pp_TBpro_OE '%s','%s','%s' ''' % row
            #sql = sql.encode('gbk')
            cur.execute(sql)
        except Exception,e:
            raise osv.except_osv(_('Error!'), _(e))
        else:
            conn.commit()
            conn.close()
            print u'更新成功'
        return




###################################################################################
