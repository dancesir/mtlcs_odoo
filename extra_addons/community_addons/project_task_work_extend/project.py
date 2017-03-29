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
from openerp.exceptions import  Warning
from openerp.tools.translate import _



class project_work(osv.osv):
    _inherit = "project.task.work"
    _columns = {
        'state': fields.selection([('draft','Draft'),('approved','Approved')], 'State'),
        'project_id': fields.related('task_id', 'project_id', type='many2one', relation='project.project', string=u'项目', readonly=1),
    }

    _defaults = {
        'state': 'draft',
    }

    def action_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'approved'}, context=context)
        return True

    def reset_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context=context)
        return True

    def unlink(self, cr, uid, ids, context=None):
        for work in self.browse(cr, uid, ids, context=context):
            if work.state != 'draft':
                raise Warning(u'只有草稿状态能删除')
        return super(project_work, self).unlink(cr, uid, ids, context=context)




########################################################################################################