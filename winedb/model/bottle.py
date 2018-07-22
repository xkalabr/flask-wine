from marshmallow import Schema, fields, post_load

class Bottle():
    def __init__(self, bid, winery, varietal, vineyard, size, year, t, price, drinkMin, drinkMax, score, region, restricted, note, rack, pri, sec):
        self.bid = bid
        self.winery = winery
        self.varietal = varietal
        self.vineyard = vineyard
        self.size = size
        self.year = year
        self.t = t
        self.price = str(price)
        self.drinkMin = drinkMin
        self.drinkMax = drinkMax
        self.score = str(score)
        self.region = str(region)
        if restricted:
            self.restricted = "Y"
        else:
            self.restricted = "N"
        self.note = note
        self.rack = rack
        self.pri = pri
        self.sec = sec

    def __repr__(self):
        return '<Bottle(id={self.bid!r})>'.format(self=self)

class BottleSchema(Schema):
    bid = fields.Int()
    winery = fields.Str()
    varietal = fields.Str()
    vineyard = fields.Str()
    size = fields.Str()
    year = fields.Str()
    t = fields.Str()
    price = fields.Number()
    drinkMin = fields.Str()
    drinkMax = fields.Str()
    score = fields.Int()
    region = fields.Str()
    restricted = fields.Bool()
    note = fields.Str()
    rack = fields.Int()
    pri = fields.Str()
    sec = fields.Str()

    @post_load
    def make_bottle(self, data):
        return Bottle(**data)
