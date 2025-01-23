# Mountain-Project-data
running the code available will allow collection of all data from all current routes on mountain project.com

## scraper.py

`scraper.py` outputs data in the jsonl format, where each line in stdout is a
valid JSON object. It scrapes
[themountainproject](https://www.themountainproject.com) (TMP)
and outputs routes, user ratings for routes, and user "ticks" for routes
(i.e. when a user completed a route).

### Output schema

These are the types of data outputted:

#### Route
```json
{
    "routeId": 0,
    "routeName": ""
}
```

#### RouteRating
```json
{
    "routeId": 0,
    "userId": 0,
    "ratings": [""]
}
```

#### RouteTick
```json
{
    "routeId": 0,
    "userId": 0,
    "text": "",
    "date": "1970-01-01T00:00:00"
}
```

Note that the `text` field is free-input text from users on TMP. This means
that while it may contain sensitive information and therefore shouldn't be
used for analysis, cleaning of the data may yield data that could prove
helpful. For example, the appearance of the word "flash" in a tick likely
indicates that the climber was able to complete the route on their first
try. The words "fell" or "hung", however, likely indicate that the user
struggled slightly. Cleaning up the free-input text to only include
notable words like this could make the data useful while removing concerns
about user data being in our data.
