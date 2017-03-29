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
from openerp.exceptions import Warning


class parse_material_acquire(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        ids = context.get('active_ids')
        cr.execute("""select state from material_acquire where id = ANY(%s);""", (ids,))
        for info in cr.fetchall():
            if info[0]  in ['draft', 'cancel']:
                raise Warning(u'草稿状态不可打印！')

        super(parse_material_acquire, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

class report_material_acquire(osv.AbstractModel):
    _name = 'report.mtlcs_stock.report_material_acquire'
    _inherit = 'report.abstract_report'
    _template = 'mtlcs_stock.report_material_acquire'
    _wrapped_report_class = parse_material_acquire




###############################################################################
