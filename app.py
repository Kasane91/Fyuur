#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models import *

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

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  recently_listed_venues = db.session.query(Venue).order_by(Venue.listed_at.desc()).limit(10).all()
  venues = []
  recently_listed_artist = db.session.query(Artist).order_by(Artist.listed_at.desc()).limit(10).all()
  artists = []

  for artist in recently_listed_artist:
    if artist.listed_at != None:
      artists.append({
        'id': artist.id,
        'name' : artist.name,
        'listed_at': artist.listed_at.strftime("%Y-%m-%d")
      })

  for venue in recently_listed_venues:
    if venue.listed_at != None:
      venues.append({
        'id': venue.id,
        'name' : venue.name,
        'listed_at' : venue.listed_at.strftime("%Y-%m-%d")
      })
  return render_template('pages/home.html', venues = venues, artists = artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  
  data = []
  venues = Venue.query.all()
  for area in Venue.query.distinct(Venue.city, Venue.state).order_by(Venue.city.desc()).all():
      data.append({
          'city': area.city,
          'state': area.state,
          'venues': [{
              'id': venue.id,
              'name': venue.name,
               
              } for venue in venues if
              venue.city == area.city and venue.state == area.state]
      })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  search_term = request.form.get('search_term', '')
  result = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%') | Venue.city.ilike(f'%{search_term}') | Venue.state.ilike(f'%{search_term}%')).all()
  
  data = []
  for r in result:
    data.append( {
      "id": r.id,
      "name": r.name,
      "city" : r.city,
      "state" : r.state
    })

  response = {
    
    "count": len(result),
    "data": data
  }
 
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: Done
  
  venue = Venue.query.get(venue_id)
  now = datetime.datetime.now()
  
  if not venue:
    return render_template('errors/404.html')
  
  query_upcoming_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id, Show.start_time > now).all()
  upcoming_shows = []

  query_past_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id, Show.start_time < now).all()
  past_shows = []
  
  for show in query_past_shows:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
      "artist_image_link": show.artist.image_link
    })
  for show in query_upcoming_shows:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
      "artist_image_link": show.artist.image_link   
    })

  
  data = {
    'id': venue.id,
    'name': venue.name,
    'city': venue.city,
    'state': venue.state,
    'address': venue.address,
    'phone': venue.phone,
    'image_link': venue.image_link,
    'facebook_link': venue.facebook_link,
    'genres': venue.genres,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'upcoming_shows': upcoming_shows,
    'past_shows': past_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: Done
  form = VenueForm(request.form)
  
  try:
      venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        facebook_link=form.facebook_link.data,
        genres=form.genres.data,
        seeking_talent=form.seeking_talent.data,
        website = form.website.data,
        seeking_description=form.seeking_description.data)
        

      db.session.add(venue)
      db.session.commit()
      flash(f'Venue {form.name.data} was successfully listed!')
  except ValueError as e:
    print(e)
    flash(f'An error has occured! {form.name.data} could not be listed')
    db.session.rollback()
  finally:
    db.session.close
  return redirect(url_for("index"))
  

 
  
  # TODO: Done
 

@app.route('/venues/<delete_id>/delete', methods=['POST'])
def delete_venue(delete_id):
  venue = Venue.query.get(delete_id)
  if venue:
    try:
      db.session.delete(venue)
      db.session.commit()
      flash('The Venue has been successfully deleted!')
      return redirect(url_for("index"))
    except:
      db.session.rollback()
  
    finally:
      db.session.close()
  
  return render_template('pages/home.html')
  

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data= Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # Only returns items for state, city or artist.
  # You can search for LA, but not "LA, CA". 
  search_term=request.form.get('search_term', '')
  result = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%') | Artist.city.ilike(f'%{search_term}%') | Artist.city.ilike(f'%{search_term}%')).all()

  data_input = []
  for r in result:
    data_input.append({
      'id': r.id,
      'name': r.name,
      'state': r.state,
      'city': r.city
      
    })

  response={
    "count": len(result),
    "data": data_input
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  current_time = datetime.datetime.now()

  query_past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time < current_time).all()
  past_shows = []
  query_upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time > current_time).all()
  upcoming_shows = []

  for event in query_past_shows:
    past_shows.append({
      "venue_id" : event.venue_id,
      "venue_name" : event.venue.name,
      "venue_image_link": event.venue.image_link,
      "start_time" : event.start_time.strftime("%Y-%m-%d %H:%M:%S") 
    })
  for event in query_upcoming_shows:
    upcoming_shows.append({
      "venue_id" : event.venue_id,
      "venue_name" : event.venue.name,
      "venue_image_link": event.venue.image_link,
      "start_time" : event.start_time.strftime("%Y-%m-%d %H:%M:%S") 
    })

  data = {
    'name' : artist.name,
    'id' : artist_id,
    'genres': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website': artist.website,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'lists_available': artist.lists_available,
    'available_from': artist.available_from.strftime("%Y-%m-%d"),
    'available_to': artist.available_to.strftime("%Y-%m-%d"),
    'image_link': artist.image_link,
    'past_shows': past_shows,
    'past_shows_count' : len(query_past_shows),
    'upcoming_shows': upcoming_shows,
    'upcoming_shows_count': len(query_upcoming_shows)
   }

  
  return render_template('pages/show_artist.html', artist=data)
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  artist= Artist.query.get(artist_id)
  if artist:
    form = ArtistForm(obj=artist)
  else:
    flash('No artist with that ID exist.')
    render_template('errors/404.html')

  # TODO: Done
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if form.available_from.data == None or form.available_to.data == None:
    bool_lists_available = False
  else:
    bool_lists_available = True
  
  try:
    artist.name = form.name.data,
    artist.genres = form.genres.data,
    artist.city = form.city.data,
    artist.state = form.state.data,
    artist.phone = form.phone.data,
    artist.website = form.website.data,
    artist.facebook_link = form.facebook_link.data,
    artist.seeking_description = form.seeking_description.data,
    artist.image_link = form.image_link.data,
    artist.available_from = form.available_from.data, 
    artist.available_to = form.available_to.data, 
    artist.lists_available = bool_lists_available
    db.session.commit()
    
    #Can't get the bool submission to work on edit, while it works flawlessly on create new :S
  except ValueError as e:
    print(e)
    flash('An error has occured! ' + form.name.data+' could not be listed')
    db.session.rollback()
  finally:
    db.session.close

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  if venue:
    form = VenueForm(obj=venue)
  else:
    flash("The Venue does not exist")
    return render_template ('errors/404.html')
   
  # TODO: Done
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  try:
    venue.name = form.name.data,
    venue.city = form.city.data,
    venue.state = form.state.data,
    venue.address = form.address.data,
    venue.phone = form.phone.data,
    venue.image_link = form.image_link.data,
    venue.facebook_link = form.facebook_link.data,
    venue.genres = form.genres.data,
    venue.seeking_description = form.seeking_description.data
    db.session.commit()
    flash(f'{venue.name} was succesfully edited')
  except ValueError as e:
    print(e)
    flash(f'An error has occured. {venue.name} was not succesfully edited')
    db.session.rollback()
  finally:
    db.session.close()


  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)

  if form.available_from.data == None or form.available_to.data == None:
    bool_lists_available = False
  else:
    bool_lists_available = True
  try: 
    artist = Artist(
      name=form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      website = form.website.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data,
      image_link = form.image_link.data,
      available_from = form.available_from.data, 
      available_to = form.available_to.data, 
      lists_available = bool_lists_available

      
    )
    db.session.add(artist)
    db.session.commit()
    flash('Artist '+form.name.data+' was successfully listed!' )
  except ValueError as e:
    print(e)
    flash('An error has occured! ' + form.name.data+' could not be listed')
    db.session.rollback()
  finally:
    db.session.close
  
  return redirect(url_for("index"))


  # called upon submitting the new artist listing form
  # TODO: Done

  # TODO: Done
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  query = db.session.query(Show).join(Artist).join(Venue).order_by(Show.start_time.desc()).all()

  data = []
  for result in query:
    data.append({
      "venue_id": result.venue_id,
      "artist_name": result.artist.name,
      "venue_name": result.venue.name,
      "artist_id": result.artist_id,
      "artist_image_link": result.artist.image_link,
      "start_time": result.start_time.strftime("%Y-%m-%d %H:%M:%S") 
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  #
  #This is a clusterf%¤k
  #

  form = ShowForm(request.form)
  artist = Artist.query.get(form.artist_id.data)
  venue = Venue.query.get(form.venue_id.data)
  time = form.start_time.data
  #Filters if current artist has an available restriction on them
  if artist.lists_available == False or artist.lists_available == None:
  #If no restrriction proceed to add and check that the instances exist  
    if artist and venue and time:
      try:
        show = Show(
          artist_id = form.artist_id.data,
          venue_id = form.venue_id.data,
          start_time = form.start_time.data
        )
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
      except ValueError as e:
        print(e)
        flash('An error has occured. Show could not be listed')
        db.session.rollback()
      finally:
        db.session.close
    elif not artist and venue: 
      flash('An error has occured. The artist does not exist')
    elif not venue and artist:
      flash('An error has occured. That venue does not exist')
      # If date does not exist
    elif not time:
      flash("Are you a traveler of time and space? I think not")
    else:
      flash('Neither artist nor venue exists, get your shit together :P')
  #If there's a restriction, proceed to check that shows fits the schedule.    
  elif artist.lists_available == True:
    if artist.available_from < time < artist.available_to:
  #if it fits schedule, proceed to check that instances exist and add.    
      if artist and venue and time:
        try:
          show = Show(
            artist_id = form.artist_id.data,
            venue_id = form.venue_id.data,
            start_time = form.start_time.data
          )
          db.session.add(show)
          db.session.commit()
          flash('Show was successfully listed!')
        except ValueError as e:
          print(e)
          flash('An error has occured. Show could not be listed')
          db.session.rollback()
        finally:
          db.session.close
      elif not artist and venue: 
        flash('An error has occured. The artist does not exist')
      elif not venue and artist:
        flash('An error has occured. That venue does not exist')
      elif not time:
        # If date does not exist
        flash("Are you a traveler of time and space? I think not")
      else:
        flash('Neither artist nor venue exists, get your shit together :P')
    else: 
        flash('Artist not available in that time')
  return redirect(url_for("index"))
    
  
  

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
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
