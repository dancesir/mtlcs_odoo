# -*- coding: utf-8 -*-
##############################################################################

import time
from openerp.osv import fields, osv
from openerp.exceptions import Warning


class wizard_layer_structure_line(osv.osv_memory):
    _name = 'wizard.structure.line'
    _inherit = 'layer.structure.line'
    _columns = {
        'wizard_id': fields.many2one('wizard.layer.structure', u'Wizard'),
    }


class wizard_layer_structure(osv.osv_memory):
    _name = 'wizard.layer.structure'
    _columns = {
        'layer_count': fields.float(u'层数'),
        'cu_thick_base': fields.float(u'基铜厚'),
        'cu_thick_finish': fields.float(u'成品铜厚'),
        'line_ids': fields.one2many('wizard.structure.line', 'wizard_id', u'Lines'),
    }

    def default_get(self, cr, uid, fields, context=None):
        return {
            'cu_thick_base': 1,
            'cu_thick_finish':1,
        }

    def apply(self, cr, uid, ids, context=None):
        info_obj = self.pool.get('pcb.info')
        info_id = context.get('active_id')

        wizard = self.browse(cr, uid, ids[0], context=context)

        layer_count = info_obj.read(cr, uid, info_id, ['layer_count'])['layer_count']
        lines_data = [(5, 0)]
        for i in range(1,layer_count+1):
            lines_data.append((0, 0, {
                #'name':  'L%s' % i,
                'layer_number': i,
                'cu_thick_base': wizard.cu_thick_base,
                'thick': wizard.cu_thick_finish,
                'sequence': i,
            },))

        info_obj.write(cr, uid, info_id, {'structure_lines': lines_data })
        return True









