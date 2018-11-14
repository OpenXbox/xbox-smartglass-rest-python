=======
History
=======

0.9.8 (2018-11-14)
------------------

* Python 3.7 compatibility

0.9.7 (2018-11-05)
------------------

* Pin xbox-smartglass-core requirement
* Filter returned consoles when addr-query is supplied
* Expose last_error in console status

0.9.6 (2018-10-04)
------------------

* Return unique index endpoint
* Create FAQ
* Always refresh XBL Client with new tokens and implement IP in /device
* Expose IP addr discovery through /devices?addr=192.168.0.123
* Always refresh XBL Client with new tokens
* Add GameDVR endpoint

0.9.5 (2018-08-16)
------------------

* Add App Type and Fix Media Status

0.9.4 (2018-08-14)
------------------

* Add /web/titlehistory endpoint
* Enable logfile cmdline argument
* Parse proper parameter from /launch/<app_id> and /media/seek/<seek_position>
* Standardize media commands and input keys casing
* Clean up status codes and auth routes
* Add friendly name and display image from titlehub to console_status response if authenticated
* Do a best effort token load and refresh on startup, auto dump tokens file on successful auth
* Simplify auth url endpoint
* Restructure app to be more modular
* Add XboxLiveClient and endpoint /web/title/<title_id> for downloading friendly name and displayImage
* Allow connecting anonymously when supplying *anonymous=true* via POST to /connect
* Pin xbox-smartglass-stump version
* Adding /media/seek endpoint
* Add /versions endpoint
* Rewrite authentication endpoints, OAUTH and regular auth supported
* Rename endpoint /authentication to /auth

0.9.3 (2018-08-08)
------------------

* Rename /status to /console_status

0.9.2 (2018-08-04)
------------------

* Stump <headend, livetv, tuner lineups> endpoints
* Add console flags
* Preparing NANO endpoints
* Adjusting authentication endpoint slightly
* Allow anonymous connection

0.9.1 (2018-08-04)
------------------

* Small fixup

0.9.0 (2018-08-04)
------------------

* First commit on github
