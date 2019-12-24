from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy, inspect
from flask_migrate import Migrate
from datetime import datetime
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://sven@localhost:5432/fyyur'
# link app to database
db = SQLAlchemy(app)
# migrate = Migrate(app, db)

getnow  = lambda : datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}

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
        '''
        Returns a understandable object of the venue
        :return:
        '''
        return f'<Venue {self.id} {self.name}>'

    def insert(self):
        '''
        Insert class function incl. Error Handling
        :return: Status of operation True if sussessful and False if any error happens
        '''
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
        '''
        Future use
        :return: Nothing
        '''
        pass

    def delete(self):
        '''
        Future use
        :return: Nothing
        '''
        pass

    def past_shows(venue_id):
        '''
        @:param
        :return: list of Shows for given Venue
        '''
        past = db.session.query(Shows).filter_by(venue_id=venue_id).filter(Shows.start_time < getnow()).all()
        shows = []
        for p in past:
            # todo replace link and date p.venue.image_link, p.date_time
            shows.append(dict(zip(('artist_id', 'artist_name', 'artist_image_link', 'start_time'),
                                        (p.artist_id, p.artist.name, "http://www.google.de", p.start_time))))
        return shows

    def coming_shows(venue_id):
        past = db.session.query(Shows).filter_by(venue_id=venue_id).filter(Shows.start_time > getnow()).all()
        shows = []
        for p in past:
            # todo replace link and date p.venue.image_link, p.date_time
            shows.append(dict(zip(('artist_id', 'artist_name', 'artist_image_link', 'start_time'),
                                  (p.artist_id, p.artist.name, "http://www.google.de", p.start_time))))
        return shows

    def venue_detail(self):
        venue = object_as_dict(self)
        venue['upcoming_shows'] = Venue.coming_shows(self.id)
        venue['past_shows'] = Venue.past_shows(self.id)
        venue['past_shows_count'] = len(venue['past_shows'])
        venue['upcoming_shows_count'] = len(venue['upcoming_shows'])
        print(venue)
        return venue

    def venue_short(self):
        data = []

        # todo city state filter

        # todo venue filter

        # todo return result

        return data


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
        artists = self
        data = []
        for artist in artists:
            data.append(dict(zip(('id', 'name'), (artist.id, artist.name))))
        return data

    def detail(self):
        '''
        Like this more than artist_detail
        '''
        artist = object_as_dict(self)
        past = db.session.query(Shows).filter_by(artist_id=self.id).filter(Shows.start_time < getnow()).all()
        past_venues = []
        for p in past:
            # todo replace link and date p.venue.image_link, p.date_time
            past_venues.append(dict(zip(('venue_id', 'venue_name', 'venue_image_link', 'start_time'),
                                        (p.venue_id, p.venue.name, "http://www.google.de", p.start_time))))
        upp = db.session.query(Shows).filter_by(artist_id=self.id).filter(Shows.start_time > getnow()).all()
        upp_venues = []
        for u in upp:
            upp_venues.append(dict(zip(('venue_id', 'venue_name', 'venue_image_link', 'start_time'),
                                       (u.venue_id, u.venue.name, "http://www.google.de", u.start_time))))
        artist["past_shows_count"] = len(past_venues)
        artist["upcoming_shows_count"] = len(upp_venues)
        artist["past_shows"] = past_venues
        artist["upcoming_shows"] = upp_venues

        return artist

class Shows(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False )
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.String(40))


    def __init__(self, **args):
        self.venue_id = args.get('venue_id'),
        self.artist_id = args.get('artist_id'),
        self.start_time = args.get('show_date')

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


# conversion of ORM to DICT
# sourced from
# https://riptutorial.com/sqlalchemy/example/6614/converting-a-query-result-to-dict
def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}
