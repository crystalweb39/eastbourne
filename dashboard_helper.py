from django.utils import simplejson
from eastbourne.shop.models import *
from eastbourne.helpers import formatCurrency
from django.http import HttpResponse
import operator
import datetime


def order_statistics(request):
    if not request.user.is_staff:
        return HttpResponse(simplejson.dumps({'error':'Bad Request'}))
    
    wo = Order.objects.filter(status__status='Shipped',is_wholesale=True)
    ro = Order.objects.filter(status__status='Shipped',is_wholesale=False)
    wo_total = sum([x.total_charged for x in wo])
    ro_total = sum([x.total_charged for x in ro])
    wo_average = float(wo_total)/len(wo) if wo else 0.00
    ro_average = float(ro_total)/len(ro) if ro else 0.00
    
    return HttpResponse(simplejson.dumps({'wo_total':formatcurrency(formatCurrency(wo_total)), 'ro_total':formatcurrency(formatCurrency(ro_total)),'wo_average':formatcurrency(formatCurrency(wo_average)),'ro_average':formatcurrency(formatCurrency(ro_average))}))

def sale_statistics(request):
    if not request.user.is_staff:
        return HttpResponse(simplejson.dumps({'error':'Bad Request'}))    

    html = ''
    d = {}
    p = Product.objects.all()
    for x in p:
        num = len(x.productorder_set.filter(order__status__status='Shipped'))
        d[x.id,x.title] = num
        
    sorted_x = sorted(d.iteritems(), key=operator.itemgetter(1))
    sorted_x.reverse()
    for x,y in sorted_x[:6]:
        html += ''' <div class="row">
                        <a href='/admin/shop/product/%s/'>%s </a> <ul class="actions">
                                <li class="add-link">%s</li>
                                
                            </ul>
                    </div>''' %(x[0],x[1],y)
    return HttpResponse(simplejson.dumps({'html':html}))

def build_datalist(request):
    if not request.user.is_staff:
        return HttpResponse(simplejson.dumps({'error':'Bad Request'}))    
    datalist = []
    option = request.POST.get('option','')
    value = request.POST.get('value','')
    now = datetime.datetime.now()
    label = 'Date'
    limit = 1
    vlabel = 'No. of Orders' if value == 'sale' else 'Amount'
    if option == 'day':
       
        pre = now
        rr = range(1,25)
        rr.reverse()
        for x in rr:
            delta = datetime.timedelta(hours=x)
            timeline = now - delta
            o = Order.objects.filter(status__status='Shipped',started__lte=pre, started__gte=timeline)
            ro = o.filter(is_wholesale=False)
            wo = o.filter(is_wholesale=True)
            pre = timeline
            datalist.append([timeline.strftime("%d %I%p"),len(o),len(ro),len(wo)]) if value == 'sale' else datalist.append([timeline.strftime("%d %I%p"),round(sum([x.total_charged for x in o]),2),round(sum([x.total_charged for x in ro]),2),round(sum([x.total_charged for x in wo]),2)])
        label = 'Time'        
        limit = 4
    elif option == 'week':
        
        pre = datetime.datetime(now.year,now.month,now.day)
        oneday = datetime.timedelta(days=1)
        rr = range(1,8)
        rr.reverse()
        for x in rr:
            delta = datetime.timedelta(days=x)
            
            timeline = pre - delta
            next_timeline = timeline + oneday
            o = Order.objects.filter(status__status='Shipped',started__lte=next_timeline, started__gte=timeline)
            ro = o.filter(is_wholesale=False)
            wo = o.filter(is_wholesale=True)
            datalist.append([timeline.strftime("%d/%m"),len(o),len(ro),len(wo)]) if value == 'sale' else datalist.append([timeline.strftime("%d/%m"),round(sum([x.total_charged for x in o]),2),round(sum([x.total_charged for x in ro]),2),round(sum([x.total_charged for x in wo]),2)])
        label = 'Date'
        limit = 1
        
    elif option == 'month':
        rr = range(1,31)
        rr.reverse()
        for x in rr:
            delta = datetime.timedelta(days=1)
            timedelta = datetime.timedelta(days=x)
            until = datetime.datetime(now.year,now.month,now.day) 
            timeline = until - timedelta
            next_timeline = timeline + delta
            o = Order.objects.filter(status__status='Shipped',started__gte =timeline, started__lte=next_timeline)
            ro = o.filter(is_wholesale=False)
            wo = o.filter(is_wholesale=True)            
            datalist.append([timeline.strftime("%d/%m"), len(o),len(ro),len(wo)]) if value == 'sale' else datalist.append([timeline.strftime("%d/%m"), round(sum([x.total_charged for x in o]),2),round(sum([x.total_charged for x in ro]),2),round(sum([x.total_charged for x in wo]),2)]) 
        label = 'Date'
        limit = 4
        
    elif option == 'year':
        pre = datetime.datetime(now.year,now.month,1)
        rr = range(1, now.month+1)
        for x in rr:
            timeline = datetime.datetime(now.year,x,1)
            next_timeline = datetime.datetime(now.year,x+1,1) if x != 12 else datetime.datetime(now.year+1,1,1)
            o = Order.objects.filter(status__status='Shipped',started__gte =timeline, started__lte=next_timeline)
            ro = o.filter(is_wholesale=False)
            wo = o.filter(is_wholesale=True)            
            datalist.append([timeline.strftime("%m/%Y"), len(o), len(ro),len(wo)]) if value == 'sale' else datalist.append([timeline.strftime("%m/%Y"), round(sum([x.total_charged for x in o]),2),round(sum([x.total_charged for x in ro]),2),round(sum([x.total_charged for x in wo]),2)])
        label = 'Month'
        limit = 2
    return HttpResponse(simplejson.dumps({'datalist':datalist, 'label':label, 'vlabel':vlabel,'limit':limit}))

def analytics(request):
    if not request.user.is_staff:
        return HttpResponse(simplejson.dumps({'error':'Bad Request'}))        
    rg = request.POST
    datalist = getAnalyticData()
    return HttpResponse(simplejson.dumps(datalist))


import gdata.analytics.client
def getAnalyticData():
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=30)
    date_from = now - delta
    
    SOURCE_APP_NAME = 'datafeed'
    my_client = gdata.analytics.client.AnalyticsClient(source=SOURCE_APP_NAME)
    my_client.client_login('clairefraunfelter@gmail.com','FrauFrau',source='datafeed',service=my_client.auth_service)
    data_query = gdata.analytics.client.DataFeedQuery({
        'ids': 'ga:15562937',#table_id
        'start-date': '%s-%s-%s' %(date_from.year,str(date_from.month).zfill(2),str(date_from.day).zfill(2)),
        'end-date': '%s-%s-%s' %(now.year,str(now.month).zfill(2),str(now.day).zfill(2)),
        'dimensions': '',
        'metrics': 'ga:visits,ga:pageviews,ga:pageviewsPerVisit,ga:visitBounceRate,ga:avgTimeOnSite,ga:percentNewVisits',
        'sort': '',
       # 'filters': 'ga:medium==referral',
        'max_results':100
    })
    feed = my_client.GetDataFeed(data_query)
    d = {}
    for entry in feed.entry:
        for met in entry.metric:
            if met.type in ['float','percent']:
                d[met.name.replace(':','_')] = "%.2f%%" % round(float(met.value),2)
            elif met.type == 'time':
                d[met.name.replace(':','_')] = str(datetime.timedelta(seconds=float(met.value))).split('.')[0]
            else:
                d[met.name.replace(':','_')] = met.value

    return d

import locale
def formatcurrency(value):
    locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )
    return locale.format("%.2f", float(value), grouping=True)




        
    