from marshmallow import Schema, fields, post_load

class Query():
  def __init__(self, vineyards, varietals, years, rack, show, regions, t, note, limit):
    self.vineyards = vineyards
    self.varietals = varietals
    self.years = years
    self.rack = rack
    self.show = show
    self.regions = regions
    self.t = t
    self.note = note
    self.limit = limit
    self.id = 0

  def __repr__(self):
    return '<Query(id={self.id!r})>'.format(self=self)


class QuerySchema(Schema):
  vineyards = fields.List(fields.String)
  varietals = fields.List(fields.String)
  years = fields.List(fields.String)
  rack = fields.Number()
  show = fields.Str()
  regions = fields.List(fields.Number)
  t = fields.Str()
  note = fields.Str()
  limit = fields.Number()

  @post_load
  def make_query(self, data):
    return Query(**data)
