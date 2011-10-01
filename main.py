from google.appengine.ext.webapp import util

import routes
import webapp2
import config

app = webapp2.WSGIApplication(config=config.webapp2_config, debug=True)
routes.add_routes(app)

def main():
    util.run_wsgi_app(app)


if __name__ == '__main__':
    main()
