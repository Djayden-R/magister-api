# Magister Exporter

Magister Exporter is an async library that makes it possible to retrieve Magister student information using the username and password of the student. This project is not endorsed by or affiliated with Magister. This project uses webscraping and using it could result in negative consequences, I am not responsibe for any damages resulting from this program.

## How to use it

### Authentication

In order to get information from a Magister account you need two things: the `user_id` and `bearer_token`. This can be done using the `fetch_magister_token()` function in the following way:

```python
from magister_export.auth import fetch_magister_token
import asyncio

user_token, user_id = asyncio.run(fetch_magister_token(base_url, username, password, headless=True))
```

Here is `base_url` the URL in a format of `[school].magister.net`, `username` the number you enter on your login screen, and `password` your account's Microsoft password.

### Getting information
