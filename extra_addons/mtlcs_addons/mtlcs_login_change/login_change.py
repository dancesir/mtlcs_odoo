# -*- coding: utf-8 -*-
##############################################################################
from openerp.osv import fields, osv



class monkey_login(osv.osv_memory):
    _name = 'monkey.login'

    def get_sz_openerp_login_url(self, cr, uid, context=None):
        return 'http://192.168.11.70:8069/web'
    _columns = {
        'name': fields.char(u'登录到深圳OpenERP', size=100,),
        'url': fields.char('URL'),
    }
    _defaults = {
        'name': lambda self, cr, uid, c: self.get_sz_openerp_login_url(cr, uid, context=c),
    }

    def ___fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(monkey_login, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            login_namme = self.pool.get('res.users').read(cr, uid, uid, ['login'])['login']
            res['arch']= u'''
                <form string="登录到深圳OpenERP">
                    <group>
                        <h1>
                            <a href='http://192.168.11.70:8069/web'>%s 登录到深圳OpenERP</a>
                        </h1>
                    </group>
                    <footer>
                        <button string="取消" class="oe_link" special="cancel" />
                    </footer>
                </form>
            '''  % (login_namme)
        return res
    
monkey_login()


