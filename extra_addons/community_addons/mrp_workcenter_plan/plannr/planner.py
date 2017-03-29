# -*- coding: utf-8 -*-
import logging
# logging.basicConfig(level=logging.INFO)
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)


class Planner_Base(object):
    def update(self, value):
        for k in value:
            self.__setattr__(k, value[k])

    def __setattr__(self, name, value):
        if name == 'state' and value not in self._State_Selection:
            raise Exception, 'state:%s not in %s' % (value, self._State_Selection)
        object.__setattr__(self, name, value)


class Work_Center(Planner_Base):
    _State_Selection = ['start', 'stop']
    pool = {}

    def __init__(self, id, code, name, state='stop', ):
        self.id = id
        self.code = code
        self.name = name
        self.state = state
        if id not in self.pool:
            self.pool[id] = self

    def find_by_code(self, code, state='stop'):
        pass

    def start(self, ):
        _logger.info('WC:%s start to work' % self.name)
        self.state = 'start'

    def stop(self, ):
        _logger.info('WC:%s stop to work' % self.name)
        self.state = 'stop'

class WC_Order(Planner_Base):
    _State_Selection = ['none', 'running', 'done']
    pool = {}
    WC = None

    def __init__(self, id, code, name, wc_id=None, production_id=None, need_time=3, state='none', ):
        self.id = id
        self.code = code
        self.name = name
        self.state = state
        self.wc_id = wc_id
        self.production_id = production_id
        self.need_time = need_time  # min
        self.start_time = None  # start time
        self.end_time = None  # end time
        WC_Order.pool[id] = self

    def start(self, time):
        wc = Work_Center.pool[self.wc_id]
        if wc.state == 'stop':
            self.update({'start_time': time, 'state': 'running', 'work_center': wc, })
            wc.start()
            _logger.info('WC_Order ID:%s start' % self.id)
            return True
        else:
            _logger.info('WC:%s is busy can not start a new order' % wc.name)
        return None

    def done(self, time):
        self.update({'state': 'done', 'end_time': time, })
        wc = Work_Center.pool[self.wc_id]
        wc.stop()
        _logger.info('WC_Order id:%s name%s done' % (self.id, self.name))
        return True


class Production(Planner_Base):
    _State_Selection = ['none', 'running', 'done']
    pool = {}
    done_pool = {}

    def __init__(self, id, code, name, wc_orders=None, state='none', start_time=None, end_time=None, ):
        self.id = id
        self.code = code
        self.name = name
        self.wc_orders = wc_orders
        self.state = state
        self.start_time = 0
        self.end_time = 0
        Production.pool[id] = self

    def check(self):
        pass

    def start(self, time=None):
        _logger.info('Production:%s Start' % self.code)
        if not self.wc_orders:
            self.done()
            return True

        wc_order = self.wc_orders[0]
        if wc_order and wc_order.start(time):
            self.update({'state': 'running', 'start_time': time})

            return True
        return False

    def done(self, time=None):
        self.update({'state': 'done', 'end_time': time})
        self.done_pool[self.id] = Production.pool.pop(self.id)
        return True

    def run(self, time=None):
        '''
        run:
        1: if current_order state is running and time finish, pass_card(done current and try to start next)
        2:                    ... is none, try to start it.
        '''
        NOW = time
        current_order = self.current_order()
        if current_order.state == 'running':
            if (NOW - current_order.start_time) >= current_order.need_time:
                self.pass_card(current_order, NOW)
        elif current_order.state == 'none':
            current_order.start(NOW)

    def pass_card(self, current_order, now):
        '''
        pass card:
        1:done the current_order,
        2:if next_order, tyr to start it, if not next_order, done the production.
        '''
        next_order = self.next_order()
        current_order.done(now)
        if next_order:
            res = next_order.start(now)
        else:
            self.done(now)
        _logger.info('pass_card: %s %s' % (current_order.id, next_order and next_order.id or None))
        return True

    def current_order(self):
        '''
        the current_order state may be 'running' or 'none'(becuase, when pass card,)
        '''
        for order in self.wc_orders:
            if order.state in ['running', 'none']:
                return order
        return None

    def next_order(self, ):
        orders = self.wc_orders
        l = len(orders)
        for i in range(l):
            if orders[i].state in ['running', 'none']:
                if i <= l - 2:
                    return orders[i + 1]
        return None

    def is_finished(self):
        for production in self.pool.values():
            if production.state != 'done':
                return False
        return True

class Planner(Planner_Base):
    _State_Selection = ['none', 'running', 'done']
    def __init__(self, mo_datas, wc_datas, WO=WC_Order, WC=Work_Center, MO=Production, state='none'):
        self.WO = WO
        self.WC = WC
        self.MO = MO
        self.mo_datas = mo_datas
        self.wc_datas = wc_datas
        self.init()
        self.state = state

    def init(self,):
        for wc in self.wc_datas:
            self.WC(wc['id'], wc['code'], wc['name'])
        for mo in self.mo_datas:
            orders = []
            for wo in mo['wo_datas']:
                orders.append(
                    self.WO(wo['id'], wo['code'], wo['name'], wo['wc_id'])
                )
            self.MO(mo['id'], mo['code'], mo['name'], orders)

    def run(self, hours=8, step=1):
        now = 0
        MO = self.MO
        for i in range(hours * 60):
            ALL_DONE = True
            for k in MO.pool.keys():
                p = MO.pool[k]
                if p.state=='none':
                    ALL_DONE = False
                    p.start(time=now)
                    continue
                elif p.state=='running':
                    ALL_DONE = False
                    p.run(time=now)
                    continue
                else:
                    _logger.error("Error, you should never be here")

            now += step
            if ALL_DONE:
                _logger.info("All production state is done")
                return True


    def print_result(self):
        WO = self.WO
        now = datetime.now()
        for k in WO.pool:
            o = WO.pool[k]
            _logger.info('%s %s %s %s %s %s' % (o.state, o.id, o.name, o.need_time,  o.start_time, o.end_time))
            start_time = now + timedelta(days=o.start_time)
            start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
