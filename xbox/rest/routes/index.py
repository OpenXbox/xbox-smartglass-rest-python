from flask import current_app as app
from . import routes

@routes.route('/')
def index():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append('%s' % rule)

    return app.success(endpoints=sorted(routes))
