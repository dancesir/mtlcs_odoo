# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
import logging
import werkzeug

import openerp
from openerp.addons.auth_signup.res_users import SignupError
from openerp.addons.web.controllers.main import ensure_db
from openerp import http
from openerp.http import request
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class auto_login_home(openerp.addons.web.controllers.main.Home):

    @http.route('/web/signup2', type='http', auth='public', website=True)
    def web_auto_signup(self, *args, **kw):
        #系统A  自动登录到 系统B 登录的方法
        #1： 使用admin rpc 链接，出发 系统b对应的用户生成一个验证码，和允许登录时间（1分钟内）
        #2： 生成一个符合B系统自动登录规则的url，用户点击登录
        #系统B
        #有这个验证码的，而且在有效时间内的，根据验证码，自动返回用户和口令，登录，否则，返回普通登录界面
        qcontext = self.get_auth_signup_qcontext()
        print ">>>>>>>>", qcontext, args, kw
        return self.web_auth_signup(args, kw)






# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
