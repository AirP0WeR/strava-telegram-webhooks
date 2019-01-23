# Strava Telegram Webhooks

App is ready to be deployed on Heroku. Attach a Postgres Database to the app before using.

```
$ heroku addons:attach <database-app-name> -a <this-app-name>
$ heroku redis:timeout --seconds 60 -a <this-app-name>
$ heroku redis:maxmemory -a <this-app-name> --policy allkeys-lru
```

##### Subscription Creation Request:
```
$ curl -X POST https://api.strava.com/api/v3/push_subscriptions \
      -F client_id={client_id} \
      -F client_secret={client_secret} \
      -F callback_url=https://{this-app-name}.herokuapp.com/webhook \
      -F verify_token=STRAVA
```

##### Deploy Hooks HTTP URL
```
https://api.telegram.org/bot{telegram_bot_token}/sendMessage?chat_id={telegram_chat_id}&text={{app}}%20({{release}})%20deployed!
```

# Deploy
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/panchambharadwaj/strava-telegram-webhooks)