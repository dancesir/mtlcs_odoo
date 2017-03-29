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
from hashlib import md5
import logging
from openerp.osv import fields, osv
from openerp.tools import SUPERUSER_ID
from openerp.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)

Base_Price_Type = [
    ('normal', u'普通板'),
    ('al_base', u'铝基板'),
    ('cu_base', u'铜基板'),
    ('rogers', u'罗杰斯板'),
    ('ptfe', u'PTFE板'),
    ('hdi', u'HDI'),
    ('flex', u'刚柔结合板'),
]
Base_Price_Type_Dic = dict(Base_Price_Type)

PCB_Fee_Arg_Type = [
    ('base', u'基板费'),
    ('board_thick', u'板厚费'),
    ('cu_thick', u'铜厚费'),
    ('special_tech', u'特殊流程费'),
    ('surface', u'表面处理费'),
    ('min_hole', u'最小孔径费'),
    ('hole_density', u'孔密度费'),
    ('line_space', u'线间距费'),
    ('hole_line', u'孔到线费'),
    ('routing', u'锣程费'),
    ('usage_rate', u'材料利用率费'),
    ('core', u'光板费'),
    ('pp', u'PP费'),
    ('test', u'飞针测试费'),
    ('finger', u'金手指费'),
    ('finger2', u'金手指超常规费'),
    ('eng', u'工程费'),
    ('eng_panel', u'工程套版费'),
    ('plot', u'菲林费'),
    ('special_test', u'专测费'),
    ('common_test', u'通测费'),
    ('eng_pack', u'工程打包费'),
    ('jig', u'模具费'),
    ('urgent', u'加急费'),
    ('change', u'变更费'),
]
Arg_Type_Dic = dict(PCB_Fee_Arg_Type)


class pcb_fee_arg_type(osv.osv):
    _name = 'pcb.fee.arg.type'
    _order = 'sequence'
    _columns = {
        'name': fields.selection(PCB_Fee_Arg_Type, u'类型', required=True),
        'show_fields': fields.many2many('ir.model.fields', 'fd_type_ref', 'type_id', 'fd_id', string=u'相关参数字段',
                                        domain=[('model_id.model', '=', 'pcb.fee.arg'), (
                                            'name', 'not in', ['name', 'type', 'value', 'eval_code', 'uniq_code'])]),
        'sequence': fields.integer(u'序号'),
    }
    _sql_constraints = [
        ('uniq_name', 'unique(uniq_name)', u'收费类型已经存在'),
    ]

    def _auto_init(self, cr, context=None):
        res = super(pcb_fee_arg_type, self)._auto_init(cr, context=context)
        for fee_type in [x[0] for x in PCB_Fee_Arg_Type]:
            ids = self.search(cr, SUPERUSER_ID, [('name', '=', fee_type)])
            if not ids:
                self.create(cr, SUPERUSER_ID, {'name': fee_type})
        return res

    def open_pcb_fee_arg(self, cr, uid, ids, context=None):
        me = self.browse(cr, uid, ids[0], context=context)
        show_fields = [x.name for x in me.show_fields]
        return {
            'name': u'价格参数',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'pcb.fee.arg',
            'type': 'ir.actions.act_window',
            'domain': [('type', '=', me.name)],
            'context': {'show_fields': show_fields, 'default_type': me.name},
            # 'target': 'new',
        }

    def open_form_view(self, cr, uid, ids, context=None):
        return {
            'name': u'价格参数',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pcb.fee.arg.type',
            'res_id': ids[0],
            'type': 'ir.actions.act_window',
            # 'domain': [('type', '=', me.name)],
            # 'context': {'show_fields':show_fields, 'default_type': me.name},
            # 'target': 'new',
        }

    def browse_by_name(self, cr, uid, name, context=None):
        ids = self.search(cr, uid, [('name', '=', name)], context=context, limit=1)
        return self.browse(cr, uid, ids[0], context=context)

    def reset_show_fields(self, cr, uid, ids, context=None):

        dict_type_fields = {
            'base': ['btype', 'layer_count', 'min_order_area', 'max_order_area', 'min_cu_thick', 'max_cu_thick'],
            'board_thick': ['min_layer_qty', 'max_layer_qty', 'min_db_thick', 'max_db_thick', 'is_htg'],
            'cu_thick': ['min_cu_thick', 'max_cu_thick'],
            'special_tech': ['special_tech_id', 'min_order_area', 'max_order_area'],
            'surface': ['surface_id', 'min_order_area', 'max_order_area', 'min_au_thick', 'max_au_thick',
                        'min_ni_thick', 'max_ni_thick'],
            'min_hole': ['min_hole', 'max_hole'],
            'hole_density': ['min_hole_density'],
            'line_space': ['min_line_width'],
            'hole_line': ['min_hole2line'],
            'routing': ['routing'],
            'usage_rate': [],
            'core': [],
            'pp': ['min_pp_count'],
            'test': ['btype', 'min_layer_qty', 'max_layer_qty', 'min_order_area', 'max_order_area', 'min_point_count',
                     'max_point_count'],
            'finger': ['min_finger_count', 'max_finger_count', 'min_au_thick', 'max_au_thick'],
            'finger2': ['min_order_area', 'max_order_area', 'min_au_thick', 'max_au_thick', 'min_ni_thick',
                        'max_ni_thick', 'min_one_finger_area', 'max_one_finger_area'],
            'eng': ['btype', 'layer_count'],
            'eng_panel': [],
            'plot': ['btype', 'min_layer_qty', 'max_layer_qty', 'min_order_area', 'max_order_area'],
            'special_test': ['min_point_count', 'max_point_count'],
            'common_test': [],
            'eng_pack': [],
            'jig': [],
            'urgent': ['lead_days', 'min_layer_qty', 'max_layer_qty'],
        }
        for k, fd_names in dict_type_fields.items():
            fd_obj = self.pool['ir.model.fields']
            arg_type = self.browse_by_name(cr, uid, k)
            fd_ids = fd_obj.search(cr, uid, [('model_id.model', '=', 'pcb.fee.arg'), ('name', 'in', fd_names)])
            self.write(cr, uid, arg_type.id, {'show_fields': [(6, 0, fd_ids)]})
        return True


Arg_Digits = (4, 3)


class pcb_fee_arg(osv.osv):
    _name = 'pcb.fee.arg'
    _order = 'id'

    def _compute_uniq_code(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}

        def S(x):
            return x and str(x) or ''

        for i in self.browse(cr, uid, ids, context=context):
            txt = '_'.join([
                S(i.type), S(i.btype), S(i.layer_count),
                S(i.cu_thick), S(i.lead_days),
                S(i.min_layer_qty), S(i.max_layer_qty),
                S(i.max_pcs_area), S(i.min_pcs_area),
                S(i.min_point_count), S(i.max_point_count),
                S(i.min_order_area), S(i.max_order_area),
                S(i.min_au_thick), S(i.max_au_thick),
                S(i.min_finger_count), S(i.max_finger_count),
                S(i.min_db_thick), S(i.max_db_thick),
                S(i.flayer_count),
                S(i.surface_id and i.surface_id.id or ''),
                S(i.special_tech_id and i.special_tech_id.id or ''),
                S(i.min_cu_thick), S(i.max_cu_thick),
                S(i.min_ni_thick), S(i.max_ni_thick),
                S(i.min_hole), S(i.max_hole),
                S(i.min_line_width), S(i.min_line_space),
                S(i.min_one_finger_area), S(i.max_one_finger_area),
                S(i.is_htg),
            ])
            res[i.id] = md5(txt).hexdigest()
        return res

    def _compute_name(self, cr, uid, ids, fields, arg=None, context=None):
        arg_type = self.pool['pcb.fee.arg.type']
        res = {}
        for arg in self.browse(cr, uid, ids, context=context):
            name = ''
            art_type = arg_type.browse_by_name(cr, uid, arg.type)
            T = '%s:%s '
            for f in art_type.show_fields:
                if f.ttype == 'many2one':
                    name += T % (f.field_description, getattr(arg, f.name).name)
                elif f.ttype == 'selection':
                    if f.name == 'btype':
                        name += T % (f.field_description, Base_Price_Type_Dic.get(getattr(arg, f.name)))
                    else:
                        name += T % (f.field_description, getattr(arg, f.name))
                else:
                    name += T % (f.field_description, getattr(arg, f.name))

            if not name:
                name = Arg_Type_Dic.get(arg.type, '')
            res[arg.id] = name
        return res

    _columns = {
        'name': fields.function(_compute_name, type='char', string=u'名称', size=160, readonly=True),
        'type': fields.selection(PCB_Fee_Arg_Type, u'费用', required=True, size=32),
        'active': fields.boolean(u'有效'),
        'method': fields.selection([('fixed', u'固定'), ('func', u'函数')], u'计算方式'),
        'value': fields.float(u'值', digits=Arg_Digits),
        'uniq_code': fields.function(_compute_uniq_code, type='char', size=48, string=u'编码', store=True),

        'layer_count': fields.integer(u'层数'),
        'min_layer_qty': fields.integer(u'最小层数'),
        'max_layer_qty': fields.integer(u'最大层数'),
        'min_order_area': fields.float(u'最小面积', digits=Arg_Digits),
        'max_order_area': fields.float(u'最大面积', digits=Arg_Digits),
        'btype': fields.selection(Base_Price_Type, u'基价类型'),
        # 'pcb_type': fields.selection([('s', 's')], u'PCB类型'),
        'max_pcs_area': fields.float(u'pcs上', digits=Arg_Digits),
        'min_pcs_area': fields.float(u'pcs下', digits=Arg_Digits),
        'max_point_count': fields.float(u'测点上', digits=Arg_Digits),
        'min_point_count': fields.float(u'测点下', digits=Arg_Digits),
        'min_cu_thick': fields.float(u'铜厚下', digits=Arg_Digits),
        'max_cu_thick': fields.float(u'铜厚上', digits=Arg_Digits),
        'cu_thick': fields.float(u'铜厚', digits=Arg_Digits),
        'lead_days': fields.integer(u'加急天'),
        'min_au_thick': fields.float(u'金厚下', digits=Arg_Digits),
        'max_au_thick': fields.float(u'金厚上', digits=Arg_Digits),
        'min_ni_thick': fields.float(u'镍厚下', digits=Arg_Digits),
        'max_ni_thick': fields.float(u'镍厚上', digits=Arg_Digits),
        'min_finger_count': fields.integer(u'最小手指数'),
        'max_finger_count': fields.integer(u'最大手指数'),
        'min_one_finger_area': fields.float(u'单个手指面积', digits=Arg_Digits),
        'max_one_finger_area': fields.float(u'单个手指面积', digits=Arg_Digits),
        'min_db_thick': fields.float(u'最小板厚', digits=Arg_Digits),
        'max_db_thick': fields.float(u'最大板厚', digits=Arg_Digits),
        'is_htg': fields.boolean(u'是否高TG'),
        'min_hole': fields.float(u'孔径上限', digits=Arg_Digits),
        'max_hole': fields.float(u'孔径下限', digits=Arg_Digits),

        'min_line_width': fields.float(u'最小线宽', digits=Arg_Digits),
        'min_line_space': fields.float(u'最小线距', digits=Arg_Digits),

        'flayer_count': fields.integer(u'柔层数'),
        'surface_id': fields.many2one('technic.attribute', u'表面处理'),
        'special_tech_id': fields.many2one('special.technic', u'特殊工艺'),
        'eval_code': fields.text('Eval Code', ),
    }

    _defaults = {
        'active': True,
        'method': 'fixed',
    }

    _sql_constraints = [
        ('uniq_code', 'unique(uniq_code)', u'重复参数'),
    ]

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for i in self.read(cr, uid, ids, ['name'], context=context):
            name = i['name'] or 'ID:%s' % i['id']
            res.append((i['id'], name))
        return res

    def _check_value(self, cr, uid, ids, context=None):
        for arg in self.browse(cr, uid, ids, context=context):
            if not (bool(arg.value) ^ bool(arg.eval_code)):
                return False
        return True

    _constraints = [
        (_check_value, u'参数值或计算方式错误', ['value', 'eval_code', ]),
    ]

    def make_log(self, cr, uid, ttype, pprice_id, v, arg, domain, context=None):
        log_obj = self.pool.get('price.log')

        log_obj.create(cr, uid, {
            'name': arg and '%s' % v or '%s <-%s' % (v, domain),
            'arg_id': arg and arg.id or None,
            'type': ttype,
            'price_id': pprice_id,
        }, context=context)
        return True

    def get_arg(self, cr, uid, ttype, domain, context=None):
        domain = [('type', '=', ttype)] + domain
        ids = self.search(cr, uid, domain, context=context)
        if len(ids) == 1:
            return self.browse(cr, uid, ids[0], context=context)
        elif len(ids) == 0:
            return None
        else:
            raise Warning(u'条件%s,记录%s' % (domain, ids))

    def parse_value(self, cr, uid, arg, pprice, fee_dic, context=None, ):
        v = 0.0
        if arg:
            _logger.info('parse_value: arg ID:%s' % arg.id)
            if arg.value:
                v = arg.value
            else:
                if not arg.eval_code:
                    raise Warning(u'价格参数%s计算错误' % arg.id)
                fn = None
                exec (arg.eval_code)
                if fn.func_code.co_argcount == 1:
                    v = fn(pprice)
                if fn.func_code.co_argcount == 2:
                    v = fn(pprice, fee_dic)
        else:
            pass
        return v

    def get_value(self, cr, uid, ttype, domain, pprice, fee_dic, context=None, log=True):
        arg = self.get_arg(cr, uid, ttype, domain)
        v = self.parse_value(cr, uid, arg, pprice, fee_dic)
        if log:
            self.make_log(cr, uid, ttype, pprice.id, v, arg, domain, context=context)
        return v

    def compute_fee(self, cr, uid, pprice, context=None):
        # compute_fee
        fee_dic = {}
        self.get_fee_base(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_board_thick(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_cu_thick(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_special_tech(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_surface(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_blind(cr, uid, pprice, fee_dic, context=None, )
        self.get_fee_min_hole(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_hole_density(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_line_space(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_hole_line(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_routing(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_usage_rate(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_core(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_pp(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_test(cr, uid, pprice, fee_dic, context=None)
        # merge.get_fee_test    self.get_fee_special_test(cr, uid, pprice, fee_dic, context=None)
        # merge.get_fee_test    self.get_fee_common_test(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_finger(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_eng(cr, uid, pprice, fee_dic, context=None)
        # merge.get_fee_eng self.get_fee_eng_panel(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_plot(cr, uid, pprice, fee_dic, context=None)
        # self.get_fee_eng_pack(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_jig(cr, uid, pprice, fee_dic, context=None)
        self.get_fee_urgent(cr, uid, pprice, fee_dic, context=None)
        # get
        self.fee_arrangement(cr, uid, pprice, fee_dic, context=context)
        return fee_dic

    def get_fee_base(self, cr, uid, pprice, fee_dic, context=None, ttype='base'):
        def get_domain(p):
            btype, info, dm = p.btype, p.info_id, [('btype', '=', p.btype)]
            if btype in ['normal', 'rogers']:
                dm += [('layer_count', '=', p.info_id.layer_count),
                       ('min_order_area', '<', p.m2_area),
                       ('max_order_area', '>=', p.m2_area)]
            elif btype in ['al_base', 'cu_base', 'ptfe']:
                dm += [('layer_count', '=', p.info_id.layer_count),
                       ('min_order_area', '<', p.m2_area),
                       ('max_order_area', '>=', p.m2_area),
                       ('min_cu_thick', '<', info.max_cu_thick),
                       ('max_cu_thick', '>=', info.max_cu_thick)]
            elif btype in ['hdi', 'flex']:
                dm += [('layer_count', '=', p.info_id.layer_count)]
            return dm

        domain = get_domain(pprice)
        v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=None)
        fee_dic.update({'fee_base': v})
        return True

    def get_fee_board_thick(self, cr, uid, pprice, fee_dic, context=None, ttype='board_thick'):
        info = pprice.info_id
        domain = [
            ('layer_count', '=', pprice.info_id.layer_count),
            ('min_db_thick', '<', info.finish_thick),  #
            ('max_db_thick', '>=', info.finish_thick),  #
        ]
        if any([x.is_htg for x in info.board_format_ids]):
            domain.append(('is_htg', '=', True))
        else:
            domain.append(('is_htg', '!=', True))

        v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=None)
        fee_dic.update({'fee_board_thick': v})
        return True

    def get_fee_cu_thick(self, cr, uid, pprice, fee_dic, context=None, ttype='cu_thick'):
        info = pprice.info_id
        domain = [
            ('min_cu_thick', '<=', info.max_cu_thick),
            ('max_cu_thick', '>=', info.max_cu_thick),
        ]
        v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=None)
        fee_dic.update({'fee_cu_thick': v})
        return True

    def get_fee_special_tech(self, cr, uid, pprice, fee_dic, context=None, ttype='special_tech'):
        info = pprice.info_id
        value = 0
        for special in info.special_tech_ids:
            domain = [
                ('special_tech_id', '=', special.id),
                ('min_order_area', '<', pprice.m2_area),
                ('max_order_area', '>=', pprice.m2_area),
            ]
            v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=None)
            value += v
        fee_dic.update({'fee_special_tech': value})
        return True

    def get_fee_blind(self, cr, uid, pprice, fee_dic, context=None, ttype='base'):
        info = pprice.info_id
        value = 0.0
        replace_btype = 'normal'
        for line in info.blind_lines:
            n = line.end_id.layer_number - line.start_id.layer_number + 1
            n = n % 2 and n + 1 or n
            domain = [
                ('btype', '=', replace_btype),
                ('layer_count', '=', n),
                ('min_order_area', '<', pprice.m2_area),
                ('max_order_area', '>=', pprice.m2_area)
            ]
            v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=context, log=False)
            v = v * 0.45
            value += v
            self.make_log(cr, uid, ttype, pprice.id, v, None, u'盲孔费', context=None)
        fee_dic.update({'fee_blind': value})
        return True

    def get_fee_surface(self, cr, uid, pprice, fee_dic, context=None, ttype='surface'):
        info = pprice.info_id
        surface_code = info.surface_coating.code or ''
        if 'au' in surface_code or 'ni' in surface_code:
            dm_au = [
                ('surface_id', '=', info.surface_coating.id),
                ('min_au_thick', '<=', info.au_thick),
                ('max_au_thick', '>', info.au_thick),
            ]
            dm_ni = [
                ('surface_id', '=', info.surface_coating.id),
                ('min_ni_thick', '<=', info.ni_thick),
                ('max_ni_thick', '>', info.ni_thick),
            ]
            if pprice.m2_area > 1:
                v_au = self.get_value(cr, uid, ttype, dm_au, pprice, fee_dic, context=None)
                v_ni = self.get_value(cr, uid, ttype, dm_ni, pprice, fee_dic, context=None)
                v_all = (v_au + v_ni )* pprice.area  > 80  and ( v_au + v_ni ) or 80 / pprice.area
            else:
                v_au = self.get_value(cr, uid, ttype, dm_au, pprice, fee_dic, context=None,log=False)
                v_ni = self.get_value(cr, uid, ttype, dm_ni, pprice, fee_dic, context=None,log=False)
                v_all = (v_au + v_ni )* pprice.area  > 80  and (v_au + v_ni)* pprice.area  or 80
                self.make_log(cr, uid, ttype, pprice.id, v_all, None, u'一次性表面处理费用', context=context)
            fee_dic.update({'fee_surface': v_all})
        else:
            domain = [
                ('surface_id', '=', info.surface_coating.id),
            ]
            if pprice.m2_area > 1:
                v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=None)
            else:
                v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=None,log=False)
                self.make_log(cr, uid, ttype, pprice.id, v, None, u'一次性表面处理费用', context=context)
            fee_dic.update({'fee_surface': v})


    def get_fee_min_hole(self, cr, uid, pprice, fee_dic, context=None, ttype='min_hole'):
        info = pprice.info_id
        domain = [('max_hole', '>=', info.min_finish_hole), ('min_hole', '<', info.min_finish_hole)]
        v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=None)
        fee_dic.update({'fee_min_hole': v})
        return True

    def get_fee_hole_density(self, cr, uid, pprice, fee_dic, context=None, ttype='hole_density'):
        domain = []
        v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=None)
        fee_dic.update({'fee_hole_density': v})
        return True

    def get_fee_line_space(self, cr, uid, pprice, fee_dic, context=None, ttype='line_space'):
        info = pprice.info_id
        if info.min_line_width or info.min_line_space:
            domain = []
            v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=None)
            fee_dic.update({'fee_line_space': v})
        else:
            self.make_log(cr, uid, ttype, pprice.id, 0, None, u'没有最小线宽线距', context=None)
        return True

    def get_fee_hole_line(self, cr, uid, pprice, fee_dic, context=None, ttype='hole_line'):
        info = pprice.info_id
        domain = []
        v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=None)
        fee_dic.update({'fee_hole_line': v})
        return True

    def get_fee_routing(self, cr, uid, pprice, fee_dic, context=None, ttype='routing'):
        info = pprice.info_id
        domain = []
        v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=None)
        fee_dic.update({'fee_routing': v})
        return True

    def get_fee_usage_rate(self, cr, uid, pprice, fee_dic, context=None, ttype='usage_rate'):
        info = pprice.info_id
        domain = []
        v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=None)
        fee_dic.update({'fee_usage_rate': v})
        return True

    def get_fee_core(self, cr, uid, pprice, fee_dic, context=None, ttype='core'):
        info = pprice.info_id
        domain = []
        v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=None)
        fee_dic.update({'fee_core': v})
        return True

    def get_fee_pp(self, cr, uid, pprice, fee_dic, context=None, ttype='pp'):
        info = pprice.info_id

        if info.fill_pp_count:
            domain = []
            v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=None)
            fee_dic.update({'fee_pp': v})
        else:
            self.make_log(cr, uid, ttype, pprice.id, 0, None, u'无填充pp', context=None)
        return True

    def get_fee_test(self, cr, uid, pprice, fee_dic, context=None):
        test_code = pprice.info_id.test_id.code
        if test_code == 'flying_test':
            self.get_fee_fly_test(cr, uid, pprice, fee_dic, context=context)
        elif test_code == 'special_test':
            self.get_fee_special_test(cr, uid, pprice, fee_dic, context=context)
        elif test_code == 'general_test':
            self.get_fee_common_test(cr, uid, pprice, fee_dic, context=context)

    def get_fee_fly_test(self, cr, uid, pprice, fee_dic, context=None, ttype='test'):
        info = pprice.info_id
        domain = [
            ('btype', '=', pprice.btype),
            ('min_layer_qty', '<', info.layer_count),
            ('max_layer_qty', '>=', info.layer_count),
            ('min_order_area', '<', pprice.m2_area),
            ('max_order_area', '>=', pprice.m2_area),
            ('min_point_count', '<', info.tp_density),
            ('max_point_count', '>=', info.tp_density),
        ]
        v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=context)
        fee_dic.update({'fee_test': v})
        return True

    def get_fee_special_test(self, cr, uid, pprice, fee_dic, context=None, ttype='special_test'):
        info = pprice.info_id
        domain = [
            ('min_point_count', '<=', info.tp_count),
            ('max_point_count', '>', info.tp_count),
        ]
        v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=context)
        fee_dic.update({'fee_special_test': v})
        return True

    def get_fee_common_test(self, cr, uid, pprice, fee_dic, context=None, ttype='common_test'):
        return True

    def get_fee_finger(self, cr, uid, pprice, fee_dic, context=None, ttype='finger'):
        info = pprice.info_id
        if not info.have_finger:
            self.make_log(cr, uid, ttype, pprice.id, 0, None, u'无金手指试', context=context)
            return True
        # get finger base
        dm = [
            ('min_au_thick', '<', info.finger_au_thick),
            ('max_au_thick', '>=', info.finger_au_thick),
            ('min_finger_count', '<', info.finger_qty),
            ('max_finger_count', '>=', info.finger_qty),
        ]
        v = self.get_value(cr, uid, ttype, dm, pprice, fee_dic, context=context)
        fee_dic.update({'fee_finger': v})
        # get finger add
        one_finger_area = info.finger_length * info.finger_width / 0.07
        dm2 = [
            ('min_order_area', '<', pprice.m2_area),
            ('max_order_area', '>=', pprice.m2_area),
            ('min_au_thick', '<', info.finger_au_thick),
            ('max_au_thick', '>=', info.finger_au_thick),
            ('min_ni_thick', '<', info.finger_ni_thick),
            ('max_ni_thick', '>=', info.finger_ni_thick),
            ('min_one_finger_area', '<', one_finger_area),
            ('max_one_finger_area', '>=', one_finger_area),
        ]
        v2 = self.get_value(cr, uid, 'finger2', dm2, pprice, fee_dic, context=context)
        fee_dic.update({'fee_finger2': v2})
        return True

    def get_fee_eng(self, cr, uid, pprice, fee_dic, context=None, ttype="eng"):
        info = pprice.info_id
        domain = [
            ('btype', '=', pprice.btype),
            ('layer_count', '=', info.layer_count),
        ]
        v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=context)
        fee_dic.update({'fee_eng': v})
        v_panel = self.get_value(cr, uid, 'eng_panel', [], pprice, fee_dic, context=context)
        fee_dic['fee_eng'] += v_panel
        return True

    def get_fee_plot(self, cr, uid, pprice, fee_dic, context=None, ttype="plot"):
        info = pprice.info_id
        btype = pprice.btype
        replace_type = btype not in ['hid', 'flex'] and 'normal' or 'hdi'
        domain = [
            ('btype', '=', replace_type),
            ('min_layer_qty', '<', info.layer_count),
            ('max_layer_qty', '>=', info.layer_count),
            ('min_order_area', '<=', info.panel_area),
            ('max_order_area', '>', info.panel_area),
        ]
        v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=context)
        fee_dic.update({'fee_plot': v})
        return True

    def get_fee_eng_pack(self, cr, uid, pprice, fee_dic, context=None, type='eng_pack'):
        info = pprice.info_id
        domain = [
            ('type', '=', type),
        ]
        # arg = self.get_arg(cr, uid, domain, context=context)
        value = 0
        fee_dic.update({'common_test': value})
        self.make_log(cr, uid, [value, domain], type, pprice.id)
        return True

    def get_fee_jig(self, cr, uid, pprice, fee_dic, context=None, ttype='jig'):
        domain = []
        v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=context)
        fee_dic.update({'fee_jig': v})
        return True

    def get_fee_urgent(self, cr, uid, pprice, fee_dic, context=None, ttype='urgent'):
        info = pprice.info_id
        urgent_days = pprice.standard_period - pprice.delivery_period
        if urgent_days > 0:
            domain = [
                ('min_layer_qty', '<', info.layer_count),
                ('max_layer_qty', '>=', info.layer_count),
                ('lead_days', '=', urgent_days),
            ]
            v = self.get_value(cr, uid, ttype, domain, pprice, fee_dic, context=context)
        else:
            v = 0.0
            self.make_log(cr, uid, ttype, pprice.id, 0, None, u'不是加急单', context=context)

        fee_dic.update({'fee_urgent': v})
        return True


    def fee_arrangement(self, cr, uid, pprice, fee_dic, context=None):
            fee_dic['price_pcs'] = sum([
                fee_dic.get('fee_base',0),
                fee_dic.get('fee_board_thick',0),
                fee_dic.get('fee_cu_thick',0),
                fee_dic.get('fee_special_tech',0),
                fee_dic.get('fee_surface', 0) < 80 and fee_dic.get('fee_surface',0) or 0,
                fee_dic['fee_blind'],
                fee_dic['fee_min_hole'],
                fee_dic['fee_hole_density'],
                fee_dic.get('fee_line_space', 0),
                fee_dic['fee_hole_line'],
                fee_dic['fee_routing'],
                fee_dic['fee_usage_rate'],
                fee_dic['fee_core'],
                fee_dic.get('fee_pp', 0)
            ]) * pprice.info_id.panel_area

            fee_dic['amount_plot_'] = fee_dic['fee_plot']
            fee_dic['amount_test'] = fee_dic.get('fee_test', 0) + fee_dic.get('fee_special_test', 0)
            fee_dic['amount_eng'] = fee_dic['fee_eng']
            fee_finger = fee_dic.get('fee_finger2', 0) or fee_dic.get('fee_finger', 0) * pprice.qty
            fee_dic['amount_other'] = sum([
                fee_dic['fee_jig'],
                fee_finger,
            ])
            fee_dic['amount'] = sum([
                fee_dic['price_pcs'] * pprice.qty,
                fee_dic['amount_plot_'],
                fee_dic['amount_test'],
                fee_dic['amount_eng'],
                fee_dic['amount_other']
            ])
            fee_dic['amount_urgent'] = fee_dic['amount'] * fee_dic['fee_urgent']

            fee_dic['once_fee'] = sum([
                fee_dic.get('amount_plot_',0),
                fee_dic.get('amount_test',0),
                fee_dic.get('amount_eng', 0),
                fee_dic.get('amount_other', 0),
                fee_dic.get('amount_urgent', 0),
                fee_dic.get('fee_surface',0) >= 80 and fee_dic.get('fee_surface',0) or 0,
            ])

            fee_dic['final_amount'] = sum([
                fee_dic.get('price_pcs',0) * pprice.qty,
                fee_dic.get('once_fee',0)
            ])
            return True



#############################################################################################################
