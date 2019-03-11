import datetime
import time
from functools import wraps
from wsgiref.handlers import format_date_time

from flask import make_response


def cacheable(expires=None, public=False):
    """
    Add Flask cache response headers based on expires in seconds.
    
    If expires is None, caching will be disabled. Otherwise, caching headers are set
    to expire in now + expires seconds.
    
    If public is set to True, cache-control header will allow intermediary caches
    to cache the response. If cookie based sessions are being used this should only
    ever be set to True when we know Set-Cookie header will be stripped downstream.
    
    Example usage:
    
    @app.route('/')
    @cacheable(expires=60)
    def index():
        return render_template('index.html')
    
    """
    def cache_decorator(view):
        @wraps(view)
        def cache_func(*args, **kwargs):
            now = datetime.datetime.utcnow()
 
            response = make_response(view(*args, **kwargs))
            response.headers.add('Last-Modified', format_date_time(time.mktime(now.timetuple())))
            
            if expires is None:
                response.headers.add('Expires', 'Fri, 13 Sep 2013 13:13:13 GMT')
                response.headers.add('Cache-Control', 'no-store, no-cache, max-age=0, s-maxage=0, must-revalidate, proxy-revalidate, no-transform, post-check=0, pre-check=0')

            else:
                expires_time = now + datetime.timedelta(seconds=expires)
                privacy_level = 'public' if public else 'private'

                response.headers.add('Cache-Control', '%s, no-transform, max-age=%d, s-maxage=%d' % (privacy_level, expires, expires))
                response.headers.add('Expires', format_date_time(time.mktime(expires_time.timetuple())))

            return response
        return cache_func
    return cache_decorator
