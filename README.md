# Strava Telegram Webhooks

```
$ heroku addons:attach <database-app-name> -a <this-app-name>
$ heroku redis:timeout --seconds 60 -a <this-app-name>
```

##### Subscription Creation Request:
```
$ curl -X POST https://api.strava.com/api/v3/push_subscriptions \
      -F client_id={client_id} \
      -F client_secret={client_secret} \
      -F callback_url=https://{this-app-name}.herokuapp.com/webhook \
      -F verify_token=STRAVA
```