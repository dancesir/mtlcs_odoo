# -*- encoding: utf-8 -*-
##############################################################################

from openerp.osv import osv, fields
Film_Type = [
    ('000',u'▲+'),
    ('001',u'▼+'),
    ('010',u'▲-'),
    ('011',u'▼-'),
    ('100',u'△+'),
    ('101',u'▽+'),
    ('110',u'△-'),
    ('111',u'▽-'),
]

Drill_Type = [
    ('first', u'一钻'),
    ('second', u'二钻'),
    ('position', u'定位孔||盘中孔'),
]


class drill_drill(osv.osv):
    _name='drill.drill'
    _order='type,sequence'

    _columns = {
        'name': fields.char(u'T', size=16),
        'type': fields.selection(Drill_Type,  u'类型'),
        'routing_id':fields.many2one('mrp.routing', u'工艺路线'),
        'production_id':fields.many2one('mrp.production', u'生产单'),
        'sequence':fields.integer(u'序号'),
        'finish_size': fields.float( u'成品孔径'),
        'tol_upper':fields.float(u'正公差'),
        'tol_lower':fields.float(u'负公差'),
        'tool_size':fields.float(u'刀具孔径'),
        'count':fields.integer(u'孔数'),
        'is_slot':fields.boolean(u'槽'),
        'is_npth':fields.boolean('NPTH'),
        'note': fields.char(u'备注', size=32),
        #'is_via':fields.boolean(u'is_via'),
    }
    _defaults = {
    }

    def change_finish_size(self,cr,uid,ids,finish_size,context=None):
        res={}
        if 0.0<finish_size<= 0.8:
            res.update({'tol_upper':0.08,'tol_lower':0.08})
            return {'value':res}
        elif 1.60>=finish_size>=0.85:
            res.update({'tol_upper':0.10,'tol_lower':0.10})
            return {'value':res}
        elif 5>=finish_size>=1.65:
            res.update({'tol_upper':0.15,'tol_lower':0.15})
            return {'value':res}

class film_film(osv.osv):
    _name = 'film.film'
    _order = 'sequence'
    _columns = {
        'name': fields.char('Name'),
        'routing_id': fields.many2one('mrp.routing', 'Routing'),
        'type': fields.selection(Film_Type, 'Type'),
        'sequence':fields.integer('sequence', ),
    }

class workcenter_attribute(osv.osv):
    _name = 'workcenter.attribute'
    _columns ={
        'name': fields.char('Name', size=32),
        'code': fields.char('code', size=16),
        'workcenter_id': fields.many2one('mrp.workcenter', 'WC', required=True,),
        'value_ids': fields.one2many('workcenter.attribute.value', 'attribute_id', 'Value'),
    }

class workcenter_attribute_value(osv.osv):
    _name = 'workcenter.attribute.value'
    _columns = {
        'name': fields.char('Name', size=32),
        'attribute_id': fields.many2one('workcenter.attribute', 'Attribute', required=True,),
        'workcenter_id': fields.related('attribute_id', 'workcenter_id', string="Workcenter", type='many2one', relation='mrp.workcenter', readonly=True),
    }


class mrp_routing(osv.osv):
    _inherit = 'mrp.routing'
    _columns ={
        'drill_ids': fields.one2many('drill.drill', 'routing_id', 'Drill', domain=[('type','=','first')]),
        'drill_ids2': fields.one2many('drill.drill', 'routing_id', 'Drill2', domain=[('type','=','second')]),
        'drill_ids3': fields.one2many('drill.drill', 'routing_id', 'Drill3', domain=[('type','=','position')]),
        'film_ids': fields.one2many('film.film', 'routing_id', 'Film'),
    }

class mrp_workcenter(osv.osv):
    _inherit = 'mrp.workcenter'
    _columns = {
        'attribute_ids': fields.one2many('workcenter.attribute', 'workcenter_id', 'Attribute'),
    }


class work_order_arg(osv.osv):
    _name = 'work.order.arg'
    _columns = {
        'routing_wcl_id': fields.many2one('mrp.routing.workcenter', 'Routing WCL'),
        'routing_id': fields.related('routing_wcl_id','routing_id', type='many2one', relation='mrp.routing', string='Routing', readonly=True),
        'production_wcl_id': fields.many2one('mrp.production.workcenter.line', 'Production WCL'),
        'production_id': fields.related('production_wcl_id', 'production_id', type='many2one', relation='mrp.production', string='Production', readonly=True),
        'attribute_id': fields.many2one('workcenter.attribute', 'attribute'),
        'name': fields.many2one('workcenter.attribute.value', 'value'),
        'note': fields.char('Note', size=32),
        'sequence': fields.integer('Sequence'),
        'need_print': fields.boolean('Print'),
    }


class mrp_routing_workcenter(osv.osv):
    _inherit = 'mrp.routing.workcenter'
    _columns = {
        'arg_ids': fields.one2many('work.order.arg', 'routing_wcl_id', 'ARG'),
    }

class mrp_routing(osv.osv):
    _inherit = 'mrp.routing'
    _columns = {
        'arg_ids': fields.one2many('work.order.arg', 'routing_id', 'ARG'),
    }

class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'
    _columns = {
        'arg_ids': fields.one2many('work.order.arg', 'production_wcl_id',  'ARG'),
    }

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    _columns ={
        'drill_ids': fields.one2many('drill.drill', 'production_id', 'Drill'),
        'arg_ids': fields.one2many('work.order.arg', 'production_id', 'ARG'),
    }

    def create_args(self):
        pass


##########################################################################################################
