from flask import Flask, render_template
from flask import request
import feedparser
import json
import urllib.request
from urllib.parse import quote

altan = Flask(__name__)
RSS_FEEDS = {'armaghplanet': 'https://armaghplanet.com/feed',
             'nasa-solar&beyond': 'https://www.nasa.gov/rss/dyn/solar_system.rss'
             }

DEFAULTS = {'publication': 'armaghplanet',
            'city': 'ACCRA, GHANA'}

# api key is copy an pasted at appid=
WEATHER_URL = '''http://api.openweathermap.org/data/2.5/ 
    weather?q={}&units=metric&appid='''
CURRENCY_URL = f'''https://openexchangerates.org/api/latest.json?
app_id='''



# note to self: Always pass the URL using an exception handler


@altan.route('/')
def home():
    # get customized science info based on user input or default
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles = science_info(publication)
    # get customized weather info based on user input or default
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)
    # get random chuck norris jokes
    jokes = request.args.get('jokes')
    # render html files with Jinja template engine    
    render_template('home.html', articles=articles, weather=weather)


@altan.route('/')  # the use of angle brackets for dynamic routing
def science_info(query):  #
    """Parsing the news from rss feeds"""
    if not query or query.lower() not in RSS_FEEDS:
        # if user query not in rss_feeds, choose armaghplanet feed by default
        publication = 'armaghplanet'
    else:
        publication = query.lower()

    feed = feedparser.parse(RSS_FEEDS[publication])  # the feedparser parses the URL into a dictionary
    # all the items in the feed are assigned to the entries variable    
    return feed['entries']


def get_weather(query):
    """Reading weather data from OpenWeatherMap API"""
    # replace spaces in query with %20 using url.parse.quote(). By default, URLs
    # don't understand space characters
    query = quote(query)
    # attach query to url using string format method.
    url = WEATHER_URL.format(query)
    # download JSON data
    data = urllib.request.urlopen(url).read()
    # convert json into a python dictionary using json.loads() method
    parsed = json.loads(data)
    # create a variable(in my case weather) which picks values from
    # recently converted JSON and puts it in a dictionary of its own 
    # JSON data (parsed) has too many attributes we don't need
    # So aggregate values you need in another smaller dictionary(weather)  
    weather = None
    # Although OpenWeatherMap API handles duplicates cities well,
    # it can show the weather of a different which bears the city name 
    # as what the client is also querying for
    # Showing the country makes client know which country's weather is displaying
    if parsed.get('weather'):
        weather = {
            'description': parsed['weather'][0]['description'],
            'temperature': parsed['main']['temp'],
            'city': parsed['name'],
            'country': parsed['sys']['country']
        }

    return weather


if __name__ == "__main__":
    altan.run(debug=True)
