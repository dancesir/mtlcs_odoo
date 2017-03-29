# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
##############################################################################

from openerp.osv import fields, osv
from openerp import tools, _
from openerp.exceptions import Warning

class process_limit(osv.osv):
    _name = 'process.limit'

    _columns = {
        'name': fields.char(u'名称', size=32),
        'code': fields.char(u'编码', size=32),
        'type': fields.char([('float', u'数字'),('char', u'字符')], u'类型'),
        'value': fields.float(u'值'),
        'company_id': fields.many2one('res.company', u'公司'),
        #'value': fields.function(_compute_value, ),
    }


