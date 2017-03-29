# -*- encoding: utf-8 -*-
import logging
import openerp
from plannr.planner import Planner
from openerp.exceptions import Warning
from datetime import datetime, timedelta
from openerp.osv import osv, fields
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF

_logger = logging.getLogger(__name__)

class workcenter_line_scheduler(osv.osv_memory):
    _name = 'workcenter.line.scheduler'
    _columns = {
        'name' : fields.char(u'工单计划'),
    }

    def run_scheduler(self, cr, uid, use_new_cursor=True, hours=8, step=5, context=None):
        '''
        '''
        if context is None:
            context = {}
        try:
            if use_new_cursor:
                cr = openerp.registry(cr.dbname).cursor()
                self.run(cr, uid, hours, step, context=context)
            if use_new_cursor:
                cr.commit()
        finally:
            if use_new_cursor:
                try:
                    cr.close()
                except Exception:
                    pass
        return {}

    def prepare_data(self, cr, uid, context=None):
        #wc_obj = self.pool['mrp.workcenter']
        #order_obj = self.pool['mrp.production.workcenter.line']
        production_obj = self.pool['mrp.production']

        p_ids = production_obj.search(cr, uid, [], context=context)
        productions = production_obj.browse(cr, uid, p_ids, context=context)

        mo_datas = [] #[{id: ,'code':, name:'', wo_list:[{id:'', code:'', name:'', 'wc_id', 'wc_code', 'wc_name' }]  }  ]
        wc_datas = []

        wc_ids = []
        for mo in productions:
            wo_datas = []
            for wo in mo.workcenter_lines:
                wc = wo.workcenter_id
                if wc.id not in wc_ids:
                    wc_ids.append(wc.id)
                    wc_datas.append({
                        'id': wc.id,
                        'code':wc.code,
                        'name': wc.name,
                    })
                wo_datas.append({
                    'id': wo.id,
                    'code':wo.name,
                    'name': wo.name,
                    'wc_id': wc.id,
                })

            mo_datas.append({
                'id': mo.id,
                'code': mo.name,
                'name': mo.name,
                'wo_datas': wo_datas
            })

        return (mo_datas, wc_datas)

    def update_date_planned(self, cr, uid, planner, context=None):
        wcl_obj = self.pool['mrp.production.workcenter.line']
        WO = planner.WO
        now = datetime.now()
        for k in WO.pool:
            order = WO.pool[k]
            date_planned = (now + timedelta(days=order.start_time)).strftime(DTF)
            wcl_obj.write(cr, uid, order.id, {'date_planned': date_planned})
        return True

    def run(self, cr, uid, hours=8, step=5, context=None):
        _logger.info('run start')

        mo_datas, wc_datas = self.prepare_data(cr, uid)
        planner = Planner(mo_datas, wc_datas)
        planner.run(hours, step)
        self.update_date_planned(cr, uid, planner)

        _logger.info('run done')
        return True



###############################################################################