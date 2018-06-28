from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from sqlalchemy import create_engine
from winedb.model.query import Query, QuerySchema
app = Flask(__name__)
CORS(app)
engine = create_engine('mysql+mysqlconnector://wineapp:pin0tNoir@localhost/wine')


@app.route("/")
def hello_world():
  return "Hello, World!"

@app.route("/vineyards")
def list_vineyards():
	retval = []
	result = engine.execute('SELECT DISTINCT vineyard FROM bottle ORDER BY vineyard')
	for row in result:
		retval.append(row[0])
	return jsonify(retval)

@app.route("/varieties")
def list_varieties():
  retval = []
  result = engine.execute('SELECT DISTINCT variety FROM bottle ORDER BY variety')
  for row in result:
    retval.append(row[0])
  return jsonify(retval)

@app.route("/years")
def list_years():
  retval = []
  result = engine.execute('SELECT DISTINCT yr FROM bottle ORDER BY yr DESC')
  for row in result:
    if row[0] == 0:
      continue
    retval.append(str(row[0]))
  return jsonify(retval)

@app.route("/racks")
def list_racks():
  retval = []
  result = engine.execute('SELECT rid,name FROM racks ORDER BY rid')
  for row in result:
    retval.append({'id': row[0], 'name': row[1]})
  return jsonify(retval)

@app.route("/settings")
def list_settings():
  retval = {}
  result = engine.execute('SELECT dname,dval from defs')
  for row in result:
    retval[row[0]] = row[1]
  return jsonify(retval)

@app.route("/regions")
def list_regions():
  retval = []
  result = engine.execute('SELECT id,name FROM region ORDER BY regid')
  for row in result:
    retval.append({'id': row[0], 'name': row[1]})
  return jsonify(retval)

@app.route('/query', methods=['POST'])
def doSearch():
  retval = []
  query = QuerySchema().load(request.get_json())
  print(query)
  print(request.get_json())
  #sql = (
  #  'insert into inventory (cid,price,cond,indeck,isfoil) values (\'' + card.data.cid + '\''
  #  ',' + str(card.data.price) + ',' + str(card.data.cond) + ',' + str(indeck) + ','
  #  + str(isfoil) + ')'
  #)
  #engine.execute(sql)
  return jsonify(retval)