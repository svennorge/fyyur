#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from datetime import datetime
from config import SQLALCHEMY_DATABASE_URI
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import Artist, Venue, Shows, object_as_dict, app, db
from datetime import datetime



#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# app and db is imported from models
moment = Moment(app)
app.config.from_object('config')

# DONE: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime


#------------------#
# Helper
#------------------#

# gets the current timestamp
# using a lambda function to get always the current time

getnow  = lambda : datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

    data = []
    venues = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state)
    for venue in venues:
        detail = []
        info = dict(zip(('city', 'state'), venue))
        query_venue = db.session.query(Venue.id, Venue.name).filter_by(city=venue.city, state=venue.state).all()
        for ven in query_venue:
            det = dict(zip(('id', 'name'), ven))
            up_shows = db.session.query(Shows).filter_by(venue_id=ven.id).filter(Shows.start_time > getnow()).all()
            det['num_upcoming_shows'] = len(up_shows)
            detail.append(det)
        info['venues'] = detail
        data.append(info)

    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  detail = Venue.query.get(venue_id)
  if detail is None:
      abort(404)
  else:
      data = Venue.venue_detail(detail)
  
  return render_template('pages/show_venue.html', venue=data)
  
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # seeking = request.form['seeking_venue']
    # if seeking == 'y':
    #     seeking_venue = True
    # else:
    #     seeking_venue = False
    seeking = False

    newVenue=Venue(
        name=request.form['name'],
        city=request.form['city'],
        address=request.form['address'],
        state= request.form['state'],
        genres=request.form['genres'],
        facebook_link=request.form['facebook_link'],
        phone=request.form['phone'],
        seeking_talent=seeking
    )

    if Venue.insert(newVenue):
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
        abort(404)
        flash('An error occurred. Venue '+request.form['name']+' could not be listed.')

    return redirect(url_for('show_venue', venue_id=newVenue.id))
    # return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    '''
    Delete of Venues not assisiated to a show. Venues with assosiated show(s) can not be deleted
    :param venue_id:
    :return:
    '''
    error = 0
    if Venue.query.get(venue_id) is None:
        return jsonify({'Status': 'Not Found', 'Operation': 'DELETE'})
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        error = 1
    finally:
        db.session.close()
    if error == 0:
        return jsonify({'Status': 'Success', 'Operation': 'DELETE'})
    else:
        return jsonify({'Status': 'Error Delete', 'Operation': 'DELETE', 'detail': 'Venues related to Shows could not be deleted'})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = Artist.artist_short(Artist.query.all())
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  artist_query = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%')).all()
  data=[]
  count = 0
  for artist in artist_query:
      upp = db.session.query(Shows).filter_by(artist_id=artist.id).filter(Shows.start_time > getnow()).count()
      z = zip(('id', 'name', 'num_upcoming_shows'), (artist.id, artist.name, upp))
      data.append(dict(z))
      count = count + 1

  response = dict(zip(('count', 'data'), (len(data), data)))

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    detail = Artist.query.get(artist_id)
    if detail is None:
        abort(404)
    else:
        artist = Artist.detail(detail)
    return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venues = Venue.query.get(venue_id)
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  venue = object_as_dict(venues)
  form.name.data = venue['name']
  form.genres.data = venue['genres']
  form.address.data = venue['address']
  form.city.data = venue['city']
  form.state.data = venue['state']
  form.phone.data = venue['phone']
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    seeking = request.form['seeking_venue']
    if seeking == 'y':
        seeking_venue = True
    else:
        seeking_venue = False

    newArtistData = Artist(
        seeking_venue=seeking_venue,
        name = request.form['name'],
        genres = request.form.getlist('genres'),
        city = request.form['city'],
        state = request.form['state'],
        phone = request.form['phone'],
        website = request.form['website'],
        image_link = request.form['image_link'],
        facebook_link = request.form['facebook_link'],
        seeking_description = request.form['seeking_description'])

    if Artist.insert(newArtistData):
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

    return redirect(url_for('show_artist', artist_id=newArtistData.id))

    # return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # todo use join to capture data
  # displays list of shows at /shows
  # needs to use join like   show_query = Show.query.options(db.joinedload(Show.Venue), db.joinedload(Show.Artist)).all()
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = Shows.query.all()
  for show in shows:
       record = dict(zip(('venue_id',
                          'venue_name',
                          'artist_id',
                          'artist_name',
                          'artist_image_link',
                          'start_time'),
                         (show.venue_id, show.venue.name, show.artist_id, show.artist.name,show.artist.image_link,show.start_time)))
       data.append(record)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    newShow = Shows(
        artist_id = request.form['artist_id'],
        venue_id = request.form['venue_id'],
        show_date = request.form['start_time']
        )
    if Shows.insert(newShow):
        flash('Show was successfully listed!')
        return redirect(url_for('shows'))
    else:
        flash('An error occurred. Show could not be listed.')
        abort(404)
        return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
