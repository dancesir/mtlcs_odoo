# -*- coding: utf-8 -*-
##############################################################################
import time
from hashlib import md5
from openerp.osv import fields, osv
from openerp.exceptions import Warning
from openerp.tools import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


class tech_detection_line(osv.osv):
    _name = 'tech.detection.line'
    _columns = {
        'name': fields.char(u'明细内容', size=32),
        'ts_id': fields.many2one('tech.standard.detection', )
    }


Detection_Status = [
    ('draft', u'草稿'),
    ('w_eng', u'待工程'),
    ('w_plan', u'待计划'),
    ('w_dpt', u'待其他部门'),
    ('w_gm', u'待总经办'),
    ('w_oc', u'待订单中心'),
    ('done', u'完成'),
    ('cancel', u'取消',),
]


class tech_standard_detection(osv.osv):
    _name = 'tech.standard.detection'

    _State_Transfer = {
        'draft': 'w_eng',
        'w_eng': 'w_plan',
        'w_plan': 'w_dpt',
        'w_dpt': 'w_gm',
        'w_gm': 'w_oc',
        'w_oc': 'done',
    }

    _columns = {
        'name': fields.char(u'非常规', size=32),
        'state': fields.selection(Detection_Status, u'完成'),
        'pprice_id': fields.many2one('pcb.price', u'报价单', readonly=True),
        'partner_id': fields.related('pprice_id', 'partner_id', type='many2one', relation='res.partner', string=u'客户', readonly=True),
        'info_id': fields.related('pprice_id', 'info_id', type='many2one', relation='pcb.info', string=u'用户单', readonly=True),
        'receive_id': fields.related('pprice_id', 'receive_id', type='many2one', relation='receive.order', string=u'接单', readonly=True),
        'company_id': fields.related('pprice_id', 'company_id', type='many2one', relation='res.company', string=u'投产工厂', readonly=True),

        ##Business  info
        'qty': fields.related('pprice_id', 'qty', type='integer',   string=u'数量', readonly=True),
        'delivery_period': fields.related('pprice_id', 'delivery_period', type='integer',   string=u'交付周期', readonly=True),

        'line_ids': fields.one2many('tech.detection.line', 'ts_id', u'超常规内容'),
        'note': fields.text(u'备注'),
        'comment_lines': fields.one2many('dpt.comment.line', 'detection_id', u'部门评审'),
        'is_tech': fields.boolean(u'技术非常规'),
        'is_delivery_time': fields.boolean(u'交期非常规'),
    }

    _sql_constraints = [
        ('name_uniq', 'unique(name)', u'非常规单号不允许重复'),
    ]

    def default_get(self, cr, uid, fields, context=None):
        return {
            'name': time.strftime('%Y%m%d%H%M%S'),
            'state': 'draft'
        }

    def action_next(self, cr, uid, ids, context=None):
        me = self.browse(cr, uid, ids[0], context=context)
        now_state = me.state
        to_state = self._State_Transfer.get(now_state)

        if to_state == 'done':
            self.pool.get('pcb.price').write(cr, uid, me.pprice_id.id, {'detection_pass':True})

        self.write(cr, uid, me.id, {'state': to_state}, context=context)
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)

    def rest_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)


class unconventional_standard(osv.osv):
    _name = 'unconventional.standard'

    _columns = {
        'name': fields.char(u'项目', size=32),
        'field_id': fields.many2one('ir.model.fields', u'字段', domain=[('model', '=', 'pcb.info')]),
        # 'type': fields.selection([('',''),('','')], string=u'类型'),
        'description': fields.text(u'描述'),
        'eval_code': fields.text(u'代码', size=128),
        'company_id': fields.many2one('res.company', u'公司'),
    }

    def _auto_init(self, cr, context=None):
        res = super(unconventional_standard, self)._auto_init(cr, context=context)
        names = [
            u'层数',
            u'盲埋孔',
            u'HDI',
            u'表面镀层',
            u'板材',
            u'成品孔径D',
            u'厚径比',
            u'镀层厚度',
            u'孔铜厚度',
            u'底铜厚度',
            u'阻焊颜色',
            u'字符颜色',
            u'最大板厚',
            u'最小板厚',
            u'板厚(T)公差MM',
            u'最大成品板尺寸',
            u'最小成品板尺寸',
            u'金手指斜边',
            u'V-CUT',
            u'验收标准',
        ]
        # company_ids = [1, 2]

        for name in names:
            ids = self.search(cr, SUPERUSER_ID, [('name', '=', name)])
            if not ids:
                self.create(cr, SUPERUSER_ID, {'name': name, 'company_id': 1})
        return res

    def check_unconventional(self, cr, uid, pprice, context=None):
        info = pprice.info_id
        lines = []
        detection_obj = self.pool.get('tech.standard.detection')
        standard_ids = self.search(cr, uid, [('company_id','=', pprice.company_id.id)])
        standards = self.browse(cr, uid, standard_ids)
        lines = []
        for s in standards:
            _logger.info(s.name)
            if not s.eval_code:
                continue
            fn = None
            exec (s.eval_code)
            if fn(info):
                lines.append(s.description)
        return lines

Delivery_Time_Standard_Type = [
    ('normal',u'普通'),
    ('hole_in_pad',u'盘中孔'),
    ('blind',u'盲埋孔'),
    ('surface',u'表面处理'),
    ('half_hole', u'半孔'),
    ('hole_density',u'孔密度'),
    ('cu_thick',u'铜厚'),

]


class delivery_time_standard(osv.osv):
    _name = 'delivery.time.standard'
    _order = 'id'

    def _compute_uniq_code(self, cr, uid, ids, field_name, arg=None, context=None):
        res = {}
        def S(x):
            return x and str(x) or ''
        for i in self.browse(cr, uid, ids, context=context):
            txt = '-'.join([
                S(i.type), S(i.company_id),
                S(i.layer_min), S(i.layer_max),
                S(i.area_min), S(i.area_max),
            ])
            res[i.id] = md5(txt).hexdigest()
        return res


    _columns = {
        'name': fields.char(u'名称'),
        'type': fields.selection(Delivery_Time_Standard_Type, u'类型', required=True),
        'company_id': fields.many2one('res.company', u'公司'),
        'uniq_code': fields.function(_compute_uniq_code, type='char', size=48, string=u'编码', store=True),
        'layer_min': fields.integer(u'最小层数>='),
        'layer_max': fields.integer(u'最大层数<'),
        'area_min': fields.float(u'最小面积>='),
        'area_max': fields.float(u'最大面积<'),
        'value': fields.float(u'标准天数'),
        'min_value': fields.float(u'最短天数'),
        'eval_code': fields.text(u'计算代码', help=u'伪代码'),
        'note': fields.char(u'备注'),
        'description': fields.text(u'描述'),
    }

    def parse_value(self, cr, uid, dts, pprice, context=None):
        _logger.info(dts)
        if not dts:
            return 0, 0

        if dts.eval_code:
            fn = None
            exec(dts.eval_code)
            return fn(pprice)
        else:
            return dts.value, dts.min_value

    def get_dts(self, cr, uid, ttype, domain, context=None):
        domain = [('type','=', ttype)] + domain
        ids = self.search(cr, uid, domain, context=context)
        if len(ids) == 1:
            return self.browse(cr, uid, ids[0], context=context)
        elif len(ids) == 0:
            return None
        else:
            raise Warning(u'条件%s,记录%s' % (domain, ids))

    def get_value(self, cr, uid, ttype, domain, pprice, context=None):
        dts = self.get_dts(cr, uid, ttype, domain)
        v, min_v = self.parse_value(cr, uid, dts, pprice)
        return  [v, min_v]

    def check_unconventional(self, cr, uid, pprice, context=None):
        days = self.compute_standard_period(cr, uid, pprice, context=context)
        return days

    def compute_standard_period(self, cr, uid, pprice, context=None):
        def period_add(vv, vv_add):
            vv[0] += vv_add[0]
            vv[1] += vv_add[1]
        vv = self.get_period_normal(cr, uid, pprice)
        vv_add = self.get_period_hole_in_pad(cr, uid, pprice)
        period_add(vv, vv_add)
        vv_add = self.get_period_blind(cr, uid, pprice, )
        period_add(vv, vv_add)
        vv_add = self.get_period_surface(cr, uid, pprice, )
        period_add(vv, vv_add)
        vv_add = self.get_period_half_hole(cr, uid, pprice,)
        period_add(vv, vv_add)
        vv_add = self.get_period_hole_density(cr, uid, pprice,)
        period_add(vv, vv_add)
        vv_add = self.get_period_cu_thick(cr, uid, pprice, )
        period_add(vv, vv_add)
        return vv

    def get_period_normal(self, cr, uid, pprice, context=None, ttype='normal'):
        info = pprice.info_id
        domain = [
            ('type', '=', ttype),
            ('layer_min', '<=', info.layer_count),
            ('layer_max', '>', info.layer_count),
            ('area_min', '<=', pprice.m2_area),
            ('area_max', '>', pprice.m2_area),
            ('company_id', '=', pprice.company_id.id)
        ]
        return self.get_value(cr, uid, ttype, domain, pprice)

    def get_period_hole_in_pad(self, cr, uid, pprice, context=None, ttype='hole_in_pad'):
        info = pprice.info_id
        domain = [
            ('type', '=', ttype),
            ('layer_min', '<=', info.layer_count),
            ('layer_max', '>', info.layer_count),
            ('area_min', '<=', pprice.m2_area),
            ('area_max', '>', pprice.m2_area),
            ('company_id', '=', pprice.company_id.id)
        ]
        return self.get_value(cr, uid, ttype, domain, pprice)

    def get_period_blind(self, cr, uid, pprice, context=None, ttype='blind'):
        info = pprice.info_id
        domain = [
            ('type', '=', ttype),
            ('layer_min', '<=', info.layer_count),
            ('layer_max', '>', info.layer_count),
            ('area_min', '<=', pprice.m2_area),
            ('area_max', '>', pprice.m2_area),
            ('company_id', '=', pprice.company_id.id)
        ]
        return self.get_value(cr, uid, ttype, domain, pprice)

    def get_period_surface(self, cr, uid, pprice, context=None, ttype='surface'):
        info = pprice.info_id
        domain = [
            ('type', '=', ttype),
            ('layer_min', '<=', info.layer_count),
            ('layer_max', '>', info.layer_count),
            ('area_min', '<=', pprice.m2_area),
            ('area_max', '>', pprice.m2_area),
            ('company_id', '=', pprice.company_id.id)
        ]
        return self.get_value(cr, uid, ttype, domain, pprice)

    def get_period_half_hole(self, cr, uid, pprice, context=None,  ttype='half_hole'):
        info = pprice.info_id
        domain = [
            ('type', '=', ttype),
            ('layer_min', '<=', info.layer_count),
            ('layer_max', '>', info.layer_count),
            ('area_min', '<=', pprice.m2_area),
            ('area_max', '>', pprice.m2_area),
            ('company_id', '=', pprice.company_id.id)
        ]
        return self.get_value(cr, uid, ttype, domain, pprice)

    def get_period_hole_density(self, cr, uid, pprice, context=None, ttype='hole_density'):
        info = pprice.info_id
        domain = [
            ('type', '=', ttype),
            ('layer_min', '<=', info.layer_count),
            ('layer_max', '>', info.layer_count),
            ('area_min', '<=', pprice.m2_area),
            ('area_max', '>', pprice.m2_area),
            ('company_id', '=', pprice.company_id.id)
        ]
        return self.get_value(cr, uid, ttype, domain, pprice)

    def get_period_cu_thick(self, cr, uid, pprice, context=None, ttype='cu_thick'):
        info = pprice.info_id
        domain = [
            ('type', '=', ttype),
            ('layer_min', '<=', info.layer_count),
            ('layer_max', '>', info.layer_count),
            ('area_min', '<=', pprice.m2_area),
            ('area_max', '>', pprice.m2_area),
            ('company_id', '=', pprice.company_id.id)
        ]
        return self.get_value(cr, uid, ttype, domain, pprice)





class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
    }

    def get_unconventional_standard(self, cr, uid, ids, context=None):
        company_id = ids[0]
        return {
            'name': u'非常规技术标准',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'unconventional.standard',
            'type': 'ir.actions.act_window',
            'domain': [('company_id', '=', company_id)],
            # 'target': 'new',
        }

    def get_delivery_time_standard(self, cr, uid, ids, context=None):
        company_id = ids[0]
        return {
            'name': u'非常规交期标准',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'delivery.time.standard',
            'type': 'ir.actions.act_window',
            'domain': [('company_id', '=', company_id)],
            # 'target': 'new',
        }




















######################################################################################
