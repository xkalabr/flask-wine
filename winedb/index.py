from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from sqlalchemy import create_engine
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
    if row[0] != 0:
      retval.append(str(row[0]))
  return jsonify(retval)

@app.route("/racks")
def list_racks():
  retval = []
  result = engine.execute('SELECT rid,name FROM racks ORDER BY name')
  for row in result:
    retval.append({'rid': row[0], 'name': row[1]})
  return jsonify(retval)

@app.route("/settings")
def list_settings():
  retval = []
  result = engine.execute('SELECT dname,dval from defs')
  for row in result:
    retval.append({'name': row[0], 'value': row[1]})
  return jsonify(retval)

@app.route("/regions")
def list_regions():
  retval = []
  result = engine.execute('SELECT id,regid,name FROM region ORDER BY regid')
  for row in result:
    retval.append({'id': row[0], 'regid': row[1], 'name': row[2]})
  return jsonify(retval)