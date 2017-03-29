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
from openerp.exceptions import  Warning


class parse_quality_inspection_iqc(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(parse_quality_inspection_iqc, self).__init__(cr, uid, name, context=context)

        # ==========1124
        inspection_ids = context.get('active_ids')
        inspection_obj = self.pool['quality.inspection.order']

        for p in inspection_obj.browse(cr, uid, inspection_ids, context):
            if p.state != 'done':
                raise Warning(u'只能打印状态为【完成】的记录')


        self.localcontext.update({
        })

class quality_inspection_iqc_report(osv.AbstractModel):
    _name = 'report.mtlcs_quality.iqc_report'
    _inherit = 'report.abstract_report'
    _template = 'mtlcs_quality.iqc_report'
    _wrapped_report_class = parse_quality_inspection_iqc




###############################################################################
