# -*- coding: utf-8 -*-
##############################################################################

import xlrd
import base64
from openerp.osv import osv, fields
from openerp.tools.translate import _
import logging

_logger = logging.getLogger(__name__)

def log_or_raise(self, string, strict=True):
    if strict:
        raise osv.except_osv(_('Error!'),_(string))
    else:
        _logger.info(string)

def Parse_Title_Data(filename=None, file_contents=None, sheet_index=1):
    res = {}
    try:
        book = xlrd.open_workbook(filename=filename, file_contents=file_contents,)
        sheet = book.sheet_by_index(sheet_index-1)
        titles = sheet.row_values(1)
        _logger.info('excel title:%s' % titles)
        datas = []
        for i in range(2, sheet.nrows):
            dic = dict(zip(titles, sheet.row_values(i)))
            dic.update({'line_number': i + 1})
            datas.append(dic)
        res.update({'title': titles, 'data': datas})
    except Exception, e:
        _logger.error('Error,excel parse %s' % e)
    return res


class excel_importor(osv.osv_memory):
    _name = 'excel.importor'
    _Parse = Parse_Title_Data
    _Log_Raise = log_or_raise
    _columns = {
        'name': fields.char('Name', size=20, ),
        'file': fields.binary(u'Excel文件', filters='*.xls｜*.csv'),
        # 'model': fields.selection([(k, Excel_model[k]['string']) for k in Excel_model], u'导入内容'),
        'type': fields.selection([('create', u'新建'),('update', u'更新')], u'导入类型'),
        'strict': fields.boolean(u'数据严格检测',help=u'当表格行内容数据错误，停止导入，否则，忽略错误行，继续导入下一行'),
        'sheet_index': fields.integer(u'导入第几张表格'),
    }

    _defaults = {
        'type': 'create',
        'strict': True,
        'sheet_index':1,
    }

    def apply(self, cr, uid, ids, context=None,):
         # the inheirt class must extend ths
        return context.get('active_model')










    ##############################################################################
