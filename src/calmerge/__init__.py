from icalendar import Calendar

from urllib import request
from http.server import *
from datetime import datetime
import sys

def fetch_calendar(url):
    icalRaw = request.urlopen(url).read()

    calendar = Calendar.from_ical(icalRaw)
    return calendar

def merge_calendars(name, cals):
    result = Calendar()
    result['prodid'] = "//Mostly Typed LLC//Calmerge 0.1//EN"
    result['version'] = "2.0"
    result['calscale'] = "GREGORIAN"
    result['x-wr-calname'] = name

    for cal in cals:
        for component in cal.subcomponents:
            if component.name == 'VEVENT':
                result.add_component(component)
    return result

class MyHandler(BaseHTTPRequestHandler):
    cache = {}

    def do_GET(self):
        try:
            (_, username, secret) = self.path.split('/')
            user = self.server.settings.get(username)
            if user and secret in user['secrets']:
                now = datetime.now()
                calendar = self.cache.get(self.path)
                if not calendar or (now - calendar['last_updated']).total_seconds() > user['timeout']:
                    calendar = {
                        'last_updated': now,
                        'calendar': merge_calendars(username, map(fetch_calendar, user['sources']))
                    }
                    self.cache[self.path] = calendar
                self.send_response(200)
                self.send_header('Content-type', 'text/calendar; charset=utf-8')
                self.end_headers()
                self.wfile.write(calendar['calendar'].to_ical())
                return
        except:
            pass
        self.send_response(404)
        self.end_headers()

class MyServer(HTTPServer):
    def __init__(self, address, handler_class, settings):
        self.settings = settings
        super(MyServer, self).__init__(address, handler_class)


def run(settings, port=8000):
    server_address = ('', port)
    httpd = MyServer(server_address, MyHandler, settings)
    httpd.serve_forever()

def main():
    from sys import argv
    import yaml

    settings = {}
    if len(argv) >= 2:
        f = open(argv[1])
        settings = yaml.load(f, Loader=yaml.SafeLoader)
        f.close()
    if len(argv) >= 3:
        run(settings, port=int(argv[2]))
    else:
        run(settings)

if __name__ == '__main__':
    main()
