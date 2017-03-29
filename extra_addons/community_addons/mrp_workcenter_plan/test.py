import logging
logging.basicConfig(level=logging.INFO)
import psycopg2
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
from planner import Work_Center, WC_Order, Production
from datetime import  datetime, timedelta

_logger = logging.getLogger(__name__)
######################################
####init job
def init_planner():
    conn= psycopg2.connect("user=odoo dbname=szodoo password=odoo")
    cr=conn.cursor()
    cr.execute(
        """
        SELECT
            wc.id, source.code, source.name
        FROM
            mrp_workcenter as wc
            LEFT JOIN  resource_resource AS source ON (wc.resource_id=source.id)
        limit 100
        """
    )
    rows = cr.fetchall()
    for row in rows:
        Work_Center(row[0], row[1], row[2] )
    cr.execute(
        """
        SELECT
            id, name, name
        FROM
            mrp_production
        limit 100
        """
    )
    rows = cr.fetchall()
    for row in rows:
        (job_id, job_code, job_name,)=row
        cr.execute(
        """
        SELECT
            wcl.id,
            wcl.name,
            res.name,
            wcl.workcenter_id
        FROM
            mrp_production_workcenter_line  AS  wcl
            LEFT JOIN  mrp_workcenter       AS  wc    ON (wcl.workcenter_id=wc.id)
            LEFT JOIN  resource_resource    AS  res   ON (wc.resource_id=res.id)
        where
            wcl.production_id=%s
        ORDER BY wcl.sequence
        """ % job_id
        )
        rows = cr.fetchall()
        orders=[]
        for row in rows:
            if row[0] and row[1]:
                o_id, o_code, o_name, d_wc_id = row
                order=WC_Order( o_id, o_code, o_name, d_wc_id,)
                orders.append(order)

        Production(job_id, job_code, job_name,   wc_orders=orders )



def test():
    init_planner()
    NOW=0
    Hours = 24
    for i in range(Hours * 60):
        NOW+=1
        _logger.info("TIME %s:======%s" % (i, NOW))

        all_done = True
        for k in Production.pool.keys():
            p = Production.pool[k]
            if p.state=='none':
                all_done = False
                p.start(time=NOW)
                continue
            elif p.state=='running':
                all_done = False
                p.run(time=NOW)
                continue
            else:
                print "error --- should not be here", p.state
                pass

        if all_done:
            _logger.info("All production state is done, Exit")
            return True
test()

_logger.info('------------------------------------------------------')
conn= psycopg2.connect("user=odoo dbname=szodoo password=odoo")
cr=conn.cursor()
now = datetime.now()
for k in WC_Order.pool:
    o = WC_Order.pool[k]
    _logger.info('%s %s %s %s %s %s' % (o.state, o.id, o.name, o.need_time,  o.start_time, o.end_time))
    start_time = now + timedelta(days=o.start_time)
    start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
    print start_time, o.start_time/24.0
    cr.execute('update mrp_production_workcenter_line set(date_planned, hour)=(%s,%s) where id = %s', (start_time, o.start_time, o.id  ))
    conn.commit()






