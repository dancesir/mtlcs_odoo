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

from openerp.osv import fields, osv, orm


class genesis_jobs(osv.osv):
    _name = "genesis.jobs"
    _columns = {
        'name': fields.char("Job", size=16,),
        'finish_date': fields.datetime("Finish_Date",),
        'username': fields.char("Username", size=16, ),
        'state': fields.selection([('draft', 'Draft'),('wait_manager',u'Manager'),('done',u'Done'),], 'State' ),
        'image': fields.binary('Image'),
        'create_uid': fields.many2one('res.users', 'Create User', readonly=True),
    }

    _defaults = {
        'state': 'draft',
    }

    def to_manager(self, cr, uid, ids, context=None):
        return  self.write(cr, uid, ids, {'state':'wait_manager'}, context=context)

    def to_done(self, cr, uid, ids, context=None):
        return  self.write(cr, uid, ids, {'state':'done'}, context=context)

    def button_test(self, cr, uid, ids, context=None):
        for job in self.browse(cr, uid, ids, context=None):
            print job.name, job.username
        return True

    def open_scale(self, cr, uid, ids, context=None):
        return {
            'name': 'scale parameter',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'scale.parameter',
            'target': 'new',
        }


    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        for arg in args:
            if arg[1] == 'ilike' and '*'in arg[2]:
                arg[2] = arg[2].replace('*', '%')
        return super(genesis_jobs, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)


class scale_parameter(osv.osv):  #如果这个缩放记录是不需要保存的，就继承成　osv.osv_memory
    _name = 'scale.parameter'
    _columns = {
        'name': fields.many2one("genesis.jobs",'Job' ),
        'scale_x': fields.float("X",),
        'scale_y': fields.float("Y", ),
    }




##################################