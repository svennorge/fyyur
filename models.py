from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy, inspect
from flask_migrate import Migrate
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://sven@localhost:5432/fyyur'
# link app to database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    genres = db.Column(db.String(80))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Shows', backref='venue')

    def __init__(self, **args):
        self.name = args.get('name')
        self.city = args.get('city')
        self.state = args.get('state')
        self.address = args.get('address')
        self.genres = args.get('genres')
        self.phone = args.get('phone')
        self.image_link = args.get('image_link')
        self.facebook_link = args.get('facebook_link')
        self.website = args.get('website')
        self.seeking_talent = args.get('seeking_talent')
        self.seeking_description = args.get('seeking_description')

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

    def insert(self):
        error = 0
        try:
            db.session.add(self)
            db.session.commit()
            self.id
        except:
            db.session.rollback()
            error = 1
        finally:
            db.session.close()
        if error == 0:
            return True
        else:
            return False


    def update(self):
        pass

    def delete(self):
        pass

    def past_venue(self):
        return db.session.query(Venue).count()

    def upcomming_venue(self):
        return db.session.query(Venue).count()


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship("Shows", backref='artist')

    def __init__(self, **args):
        self.name = args.get('name')
        self.city = args.get('city')
        self.state = args.get('state')
        self.phone = args.get('phone')
        self.genres = args.get('genres')
        self.website = args.get('website')
        self.image_link = args.get('image_link')
        self.facebook_link = args.get('facebook_link')
        self.seeking_venue = args.get('seeking_venue')
        self.seeking_description = args.get('seeking_description')

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

    def insert(self):
        error = 0
        try:
            db.session.add(self)
            db.session.commit()
            self.id
        except:
            db.session.rollback()
            error = 1
        finally:
            db.session.close()
        if error == 0:
            return True
        else:
            return False

    def update(self):
        error = False
        try:
            pass
        except:
            pass
            error = True
        finally:
            pass
        if error:
            return False
        else:
            return True


    def delete(self):
        error = False
        try:
            db.session.delete(self)
            db.session.commit()
        except:
            db.session.rollback()
            error = True
        finally:
            db.session.close()
        if error:
            return False
        else:
            return True


    def artist_short(self):
        return {'id':self.id, 'name':self.name,}

class Shows(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False )
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    show_date = db.Column(db.String(40))

    def __init__(self, **args):
        self.venue_id = args.get('venue_id'),
        self.artist_id = args.get('artist_id'),
        self.show_date = args.get('show_date')

    def __repr__(self):
        return f'<Show {self.id} {self.show_date}>'

    def insert(self):
        error = False
        try:
            db.session.add(self)
            db.session.commit()
            self.id
        except:
            db.session. rollback()
            error = True
        finally:
            db.session.close()
        if error:
            return False
        else:
            return True

    def detail(self):
        return {
            'artist_id': self.artist_id,
            'artist_name': self.artist.name,
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'start_time': self.show_date
        }

    def comingshows(self):
        return {'artist_id': self.artist_id, 'venue_id': self.venue_id }


def detail_venue(city, state):
    query_venue = db.session.query(Venue.id, Venue.name).filter_by(city=city, state=state).all()
    data = []
    for venue in query_venue:
        z = zip(('id','name'),venue)
        d = dict(z)
        data.append(d)
    return data

def venue_shows(venue_id):
    query_shows = db.session.query.filter_by(venue_id=venue_id).all()
    data=[]
    for show in query_shows:
        data.append(dict(zip(('artist_id', 'artist_name', 'artist_image_link', 'start_time'),
                             (show.id, show.artist.name, show.artist.image_link, show.show_date))))

    return data


# convesrion of ORM to DICT
# sourced from
# https://riptutorial.com/sqlalchemy/example/6614/converting-a-query-result-to-dict
def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}
