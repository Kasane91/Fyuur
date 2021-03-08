from app import db
import datetime

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(1000))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String(120)))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(180))
    listed_at = db.Column(db.DateTime, default=datetime.datetime.now())
    
    shows = db.relationship('Show', backref='venues', lazy=True)
    
    def __repr__(self):
      return f'<venues {self.name}>'


    
class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(1000))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(250))
    genres = db.Column(db.ARRAY(db.String(120)))
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artists', lazy=True)
    listed_at = db.Column(db.DateTime, default=datetime.datetime.now())
    lists_available = db.Column(db.Boolean, default=False)
    available_from = db.Column(db.DateTime)
    available_to = db.Column(db.DateTime)



    
    def __repr__(self):
      return f'<artists {self.id} {self.name}>'

class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  venue = db.relationship('Venue', backref='shows_venue', lazy=True)
  artist = db.relationship('Artist', backref='shows_artist', lazy=True)

  def __repr__(self):
    return f'<shows {self.artist_id} {self.venue_id}>'