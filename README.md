# Exist

*An open-source rewrite of Exist core server-side application*

[Exist](https://exist.io) is our web and mobile platform for personal analytics. Connect services like fitness trackers, productivity software, your calendar, and even the weather, and Exist will find insights and correlations in what you do.

![Dashboard](https://exist.io/static/img/pics/feature_today2.png)

We're interested in making the core of Exist (the back-end data handling, but not the front-end) open-source. We're also conveniently experimenting with a new version that can handle arbitrary metadata and events rather than tracking data on a per-day granularity. So, why not build the new version in public?

## Requirements/components

Built with Python 3.4, Django 1.8, SciPy, [Pulsar](https://github.com/quantmind/pulsar/), Django Rest Framework, and Postgres.

## Status

Still very much in alpha. Components from the current live version of Exist will gradually be ported into the new exist-core as it matures.

## Installing

* Set up a new Postgres database
* Add your database config to a file called `local_settings.py` in the `exist` directory
* Create a new virtual environment, clone Exist into it, and run `pip install -r requirements.txt`.
* Run `python manage.py migrate`

## Running

`python manage.py pulse` will spin up a new worker. Visit `localhost:8060/api/` to browse the API.

## Try the real thing

If you're interested in using the full version of Exist you can sign up for an account at [https://exist.io](exist.io).
