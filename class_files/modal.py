from my_packages import localPackages


class UserInfo(localPackages.ndb.Model):
    username = localPackages.ndb.StringProperty(required=True)
    email = localPackages.ndb.StringProperty(required=True)
    password = localPackages.ndb.StringProperty(required=True)
    profilepic = localPackages.ndb.StringProperty(required=True)
    isOnline = localPackages.ndb.BooleanProperty(required=True)


class Post(localPackages.ndb.Model):
    post = localPackages.ndb.TextProperty(required=True)
    name = localPackages.ndb.StringProperty(required=True)
    likes = localPackages.ndb.IntegerProperty(required=True)
    timestamp = localPackages.ndb.DateTimeProperty(auto_now_add=True)


parameters = {"lat": 12.9846218, "lon": 80.2457648, 'APPID': 'bbc326371956012fa3393d40ded368d1'}
weatherinfo = localPackages.requests.get("http://api.openweathermap.org/data/2.5/weather", params=parameters).json()
issinfo = localPackages.requests.get("http://api.open-notify.org/iss-now.json").json();


class weather:
    description = weatherinfo.get('weather')[0].get('description')
    latitude = weatherinfo.get('coord').get('lat')
    longitude = weatherinfo.get('coord').get('lon')
    date = localPackages.datetime.datetime.fromtimestamp(weatherinfo.get('dt')/1000.0)
    tempmin = weatherinfo.get('main').get('temp_min') - 273.15
    tempmax = weatherinfo.get('main').get('temp_max') - 273.15
    place = weatherinfo.get('name')


class Globals:
    newpostkey = ""
    getPostResponse = {
                        "success": True,
                        "feeds": [],
                        "next_cursor": "",
                        "more": True
                      }
