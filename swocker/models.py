from swocker import db

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    code = db.Column(db.String(5), index=True)
    retrieved_data = db.Column(db.Boolean, unique=False, default = False)
    tweets = db.relationship('Tweet', backref='company',
                                lazy='dynamic')
    def __repr__(self):
        return '<Company %r>' % (self.code)
    def __unicode__(self):
        return unicode(self.some_field) or u''

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), index=True, unique=True)
    sentiment = db.Column(db.Float)
    date = db.Column(db.String(15))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    def __repr__(self):
        return '<Tweet %r>' % (self.name)
    def __unicode__(self):
        return unicode(self.some_field) or u''
