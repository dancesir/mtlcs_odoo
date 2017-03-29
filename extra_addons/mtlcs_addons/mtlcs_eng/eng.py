# -*- encoding: utf-8 -*-
##############################################################################

from openerp.osv import fields, osv
from openerp import SUPERUSER_ID
from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTFORMAT


class eng_picking_prepare(osv.osv):
    _name = 'eng.picking.prepare'
    _columns = {
        'name': fields.char(u'名称', size=32),
    }
    _defaults = {
    }
    _sql_constraints = {
    }

    def xxx(self, cr, uid, ids, context):
        return True

#############################################################################