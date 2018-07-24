from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from sqlalchemy import *
from winedb.model.query import Query, QuerySchema
from winedb.model.bottle import Bottle, BottleSchema
from datetime import timedelta
import datetime
import random

app = Flask(__name__)
CORS(app)
engine = create_engine('mysql+mysqlconnector://wineapp:pin0tNoir@localhost/wine')
meta = MetaData()
tBottle = Table('bottle', meta, autoload=True, autoload_with=engine)
tRacks = Table('racks', meta, autoload=True, autoload_with=engine)
tDefs = Table('defs', meta, autoload=True, autoload_with=engine)
tRegion = Table('region', meta, autoload=True, autoload_with=engine)
tLoc = Table('loc', meta, autoload=True, autoload_with=engine)
tAdvent = Table('advent', meta, autoload=True, autoload_with=engine)

@app.route("/vineyards")
def list_vineyards():
    retval = []
    conn = engine.connect()
    s = select([tBottle.c.vineyard]).order_by(tBottle.c.vineyard).distinct()
    result = conn.execute(s)
    for row in result:
        retval.append(row[0])
    conn.close()
    return jsonify(retval)

@app.route("/varieties")
def list_varieties():
    retval = []
    conn = engine.connect()
    s = select([tBottle.c.variety]).order_by(tBottle.c.variety).distinct()
    result = conn.execute(s)
    for row in result:
        retval.append(row[0])
    conn.close()
    return jsonify(retval)

@app.route("/years")
def list_years():
    retval = []
    conn = engine.connect()
    s = select([tBottle.c.yr]).order_by(desc(tBottle.c.yr)).distinct()
    result = conn.execute(s)
    for row in result:
        if row[0] == 0:
            continue
        retval.append(str(row[0]))
    conn.close()
    return jsonify(retval)

@app.route("/racks")
def list_racks():
    retval = []
    conn = engine.connect()
    s = select([tRacks.c.rid, tRacks.c.name]).order_by(tRacks.c.rid)
    result = conn.execute(s)
    for row in result:
        retval.append({'id': row[0], 'name': row[1]})
    conn.close()
    return jsonify(retval)

@app.route("/settings")
def list_settings():
    retval = {}
    conn = engine.connect()
    s = select([tDefs.c.dname, tDefs.c.dval])
    result = conn.execute(s)
    for row in result:
        retval[row[0]] = row[1]
    conn.close()
    return jsonify(retval)

@app.route("/regions/<string:formname>")
def list_regions(formname):
    retval = []
    conn = engine.connect()
    attr = 'id'
    if formname == "search":
        attr = 'regid'
    s = select([tRegion.c[attr],tRegion.c.name]).order_by(tRegion.c.regid)
    result = conn.execute(s)  
    for row in result:
        retval.append({'id': row[0], 'name': row[1]})
    conn.close()
    return jsonify(retval)

@app.route('/drink/<string:id>', methods=['DELETE'])
def drink_wine(id):
    print('Deleting ' + id)
    sql = 'delete from loc where bot=' + id
    engine.execute(sql)
    sql = 'update bottle set dd=NOW() where bid=' + id
    engine.execute(sql)
    return '', 204

@app.route('/bottles/', methods=['POST'])
def add_bottle():
    conn = engine.connect()
    bottle = BottleSchema().load(request.get_json())
    b = bottle.data
    ins = tBottle.insert()
    result = conn.execute(ins, vineyard=b.winery, yr=b.year, t=b.t, variety=b.varietal, desig=b.vineyard, size=b.size, price=b.price, dbmin=b.drinkMin, drinkby=b.drinkMax, score=b.score, reg=b.region, restr=b.restricted, note=b.note, da=datetime.now(), de=datetime.now(), dd=0)
    ins2 = tLoc.insert()
    conn.execute(ins2, rack=b.rack, pri=b.pri, sec=b.sec, bot=result.inserted_primary_key[0])
    conn.close()
    return "", 204

@app.route('/bottles/<string:id>', methods=['PUT'])
def update_bottle(id):
    conn = engine.connect()
    bottle = BottleSchema().load(request.get_json())
    b = bottle.data
    stmt = tBottle.update().where(tBottle.c.bid == b.bid)
    conn.execute(stmt, vineyard=b.winery, yr=b.year, t=b.t, variety=b.varietal, desig=b.vineyard, size=b.size, price=b.price, dbmin=b.drinkMin, drinkby=b.drinkMax, score=b.score, reg=b.region, restr=b.restricted, note=b.note, de=datetime.now())
    stmt = tLoc.update().where(tLoc.c.bot == b.bid)
    conn.execute(stmt, rack=b.rack, pri=b.pri, sec=b.sec, bot=b.bid)
    conn.close()
    return "", 204	

@app.route('/bottles/<string:id>')
def fetch_bottle(id):
    retval = {}
    conn = engine.connect()
    sql = text("SELECT bid,vineyard,yr,t,variety,desig,price,dbmin,drinkby,score,restr,note,reg,size,da,dd,rid as name,pri,sec FROM bottle left outer join loc on bid=bot left outer join racks r on rid=rack join region rg on reg=rg.id WHERE bid= :bid")
    result = conn.execute(sql, bid=id)
    for row in result:
        retval = packageData(row)
    conn.close()
    return jsonify(retval)

@app.route('/adventpick/<string:day>')
def advent_pick(day):
    if int(day) > 24:
        return "Invalid day", 404
    yr = datetime.date.today().year
    row_check = -1
    conn = engine.connect()
    s = text("SELECT count(*) FROM advent WHERE yr= :yr AND day= :day")
    result = conn.execute(s, yr=yr, day=day)
    for row in result:
        row_check = row[0]
    if row_check == 0:
        candidates = []
        s = select([tBottle.c.yr,tBottle.c.vineyard,tBottle.c.variety,tBottle.c.desig]).where((tBottle.c.dd == 0) & (tBottle.c.restr == 'N') & (tBottle.c.dbmin <= yr))
        result = conn.execute(s)
        for row in result:
            candidates.append(";".join(map(str,row)))
        thePick = random.choice(candidates)
        s = tAdvent.insert()
        conn.execute(s, yr=yr, day=day, bottle=thePick)
    conn.close()
    return jsonify(getAdventCalendar())

@app.route('/advent')
def advent():
    return jsonify(getAdventCalendar())

@app.route('/query', methods=['POST'])
def doSearch():
    retval = []
    query = QuerySchema().load(request.get_json())
    sql = generateSql(query.data)
    result = engine.execute(sql)
    for row in result:
        retval.append(packageData(row))
    if query.data.limit > 0:
        retval = [random.choice(retval)]
    return jsonify(retval)


def generateSql(query):
    sql = "SELECT DISTINCT bid,vineyard,yr,t,variety,desig,price,dbmin,drinkby,score,restr,note,reg,da,dd,size"
    if query.show == 'Drunk':
        sql += " FROM bottle,region rg WHERE reg=rg.id AND dd>0"
    else:
        sql += ",r.name,pri,sec FROM bottle left outer join loc on bid=bot left outer join racks r on rid=rack join region rg on reg=rg.id WHERE "
    if query.show == 'Current':
        sql += "dd=0"
    elif query.show == 'Recent':
        sql += "da>'" + calcOldDate() + "' AND dd=0"
    else:
        sql += "dd>=0"

    if len(query.note) > 0:
        sql += " AND note LIKE '%" + query.note + "%'"
    if 'A' not in query.t:
        sql += " AND t='" + query.t + "'"

    sql += parseQueryList(query.vineyards, "vineyard")
    sql += parseQueryList(query.years, "yr")
    sql += parseQueryList(query.varietals, "variety")
    sql += parseQueryList(query.regions, "regid")

    if query.rack > 0:
        sql += " AND rid='" + str(int(query.rack)) + "' ORDER BY pri,sec"
    else:
        sql += " ORDER BY yr,vineyard,variety"
    return sql

def packageData(bottle):
    retval = {}
    retval['bid'] = bottle['bid']
    retval['winery'] = bottle['vineyard']
    retval['year'] = str(bottle['yr'])
    retval['t'] = bottle['t']
    retval['varietal'] = bottle['variety']
    retval['vineyard'] = bottle['desig']
    retval['price'] = str(bottle['price'])
    retval['drinkmin'] = bottle['dbmin']
    retval['drinkmax'] = bottle['drinkby']
    retval['score'] = bottle['score']
    if bottle['note'] != None:
        retval['note'] = bottle['note']
    else:
        retval['note'] = ''
    retval['da'] = str(bottle['da'].year)
    retval['drunk'] = bottle['dd'] != None
    if retval['drunk']:
        retval['restricted'] = 'N'
    else:
        retval['restricted'] = bottle['restr']
    retval['size'] = bottle['size']
    retval['region'] = bottle['reg']
    if bottle['name'] != None:
        retval['rack'] = bottle['name']
        retval['pri'] = bottle['pri']
        retval['sec'] = bottle['sec']
    else:
        retval['rack'] = ''
        retval['pri'] = ''
        retval['sec'] = ''
    return retval

# Process the list query items
def parseQueryList(attr, name):
    retval = ''
    if len(attr) > 0 and 'Any' not in attr:
        for i, val in enumerate(attr):
            if i == 0:
                retval += " AND (" + name + " LIKE '" + val + "%'"
            else:
                retval += " OR " + name + " LIKE '" + val + "%'"
        retval += ")"
    return retval

# Determine 30 days ago for Recent query
def calcOldDate():
    old_date = datetime.date.today() + timedelta(-30)
    return str(old_date.year) + '-' + str(old_date.month).zfill(2) + '-' + str(old_date.day).zfill(2)

def getAdventCalendar():
    retval = []
    tmpResult = []

    # Determine day of week of Dec 1
    yr = datetime.date.today().year
    dec1 = datetime.date(yr, 12, 1)
    theFirst = int(dec1.strftime('%w')) + 1

    # Retrieve the opened squares
    opened = {}
    conn = engine.connect()
    s = select([tAdvent.c.day, tAdvent.c.bottle]).where(tAdvent.c.yr == yr).order_by(tAdvent.c.day)
    result = conn.execute(s)
    for row in result:
        opened[row[0]] = row[1]
    conn.close()

    # Populate November days
    for i in range(1, theFirst):
        tmpResult.append({'tag': 'nov', 'day': str(31 + i - theFirst)})
    # Figure out how many weeks we need to represent
    target = 5*7
    if theFirst > 5:
        target = 6*7
    # Populate December days (theFirst -1) + 1 for starting range at 1 instead of 0
    for i in range(1, target - theFirst + 2):
        if i > 31:
            tmpResult.append({'tag': 'nov', 'day': str(i - 31)})
        else:
            contents = []
            if str(i) in opened:
                y,w,v,z = opened[str(i)].split(";")
                contents.append(y[0:4] + " " + w)
                contents.append(v)
                contents.append(z)
            tmpResult.append({'tag': 'dec', 'day': str(i), 'pick': contents})

    newList = []
    for i in range(0, len(tmpResult)):
        newList.append(tmpResult.pop(0))
        if len(tmpResult) % 7 == 0:
            retval.append(newList)
            newList = []
    return retval