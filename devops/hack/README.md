## Docker tools

To install `docker-compose` and `dry` (an ncurses based terminal app for monitoring
running containers), simply execute `sudo ./docker-tools.sh` (both tools will be
installed to /usr/local/bin).

## JWT tools

This netatmo app is designed as a micro-service to provide netatmo APIs to a wider
application thus the app assumes authentication is out-of-scope and instead relies 
on signed JWTs for authorization (with the requirement that the value of the 'sub'
field in the token's payload is guaranteed to be a unique string for each app user).

To aid with development (when an actual authentication service may not be
available to issue real JWT auth tokens), use the `jwt-tools.sh` script
to create a mock auth token which only works in dev/debug mode.

Examples (`cd` to this hack dir before running them):

- Installing (you must do this once before using the other commands):

  `sudo ./jwt-tools.sh install`

- To get a dummy JWT auth token for use when calling the app's user API
  endpoints (valid for 1 hour):
  
  `./jwt-tools.sh token user ../../app/.jwt/dummy/privkey.der`

- To get a dummy JWT auth token for use when calling the app's admin API
  endpoints (valid for 1 hour):
  
  `./jwt-tools.sh token admin ../../app/.jwt/dummy/privkey.der`

- To decode a JWT token created with the above `create` commands:
  
  `./jwt-tools.sh decode ../../app/.jwt/dummy/pubkey.der PASTE_YOUR_TOKEN_HERE`
