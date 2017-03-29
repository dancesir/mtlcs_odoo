'''

to_removes = [
        ['procurement.order',],
        ['purchase.order.line',],
        ['purchase.order',],

        ['stock.quant',],
        ['stock.move',],
        ['stock.pack.operation',],
        ['stock.picking',],
        ['stock.inventory.line',],
        ['stock.inventory',],
        ['stock.quant.package',],
        ['stock.quant.move.rel',],
        ['stock.production.lot',],
        ['stock.fixed.putaway.strat',],
        ['mrp.production.workcenter.line',],
        ['mrp.production',],
        ['mrp.production.product.line',],
        ['sale.order.line',],
        ['sale.order',],
        ['pos.order.line',],
        ['pos.order',],

        ['account.voucher.line',],
        ['account.voucher',],
        ['account.invoice',],
        ['account.partial.reconcile',],
        ['account.move',],

        ['production.plan.month',],
        ['preparation.order',],
        ['purchase.requisition',],
['quality.inspection.order',],
['fa.piao',],


['price.adjust.line',],
['change.order',],
['pcb.price',],
['layer.struct.line',],
['impedance.line',],
['pcb.info',],
['receive.order',],
['tech.standard.detection',],
['sale.order.line.batch'],
['pcb.remind',],
]

def remove_data(cr):
        try:
            for line in to_removes :
                obj_name = line[0]
                obj = self.pool.get(obj_name)
                if obj and obj._table_exist:
                    sql = "delete from %s" % obj._table
                    cr.execute( sql)


        except Exception, e:
            raise Warning(e)

        return True

remove_data(cr,)

'''
