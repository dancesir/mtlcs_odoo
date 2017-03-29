# -*- encoding: utf-8 -*-
##############################################################################

import time
from openerp.osv import osv, fields
from datetime import datetime as DT


class project_task(osv.osv):
    _inherit = 'project.task'
    _columns = {
        'score': fields.integer(u'Score'),
        'bonus': fields.integer(u'Bonus'),
    }

