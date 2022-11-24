# Anchormake - AnkerMake Library

Anchormake is a Python library for working with AnkerMake M5 FDM 3D printers

## Super Early Alpha Disclaimer

This is super rough right now, but I've gone ahead and uploaded it as more and more people are going to be getting their M5's soon. I'll break things and change things as we move along. 

## Installation

```bash
pip install anchormake
```

## Usage

I'd recommend that you create a second AnkerMake account and then share your printer access with that account in order to use this library. Much of the AnkerMake cloud infrastructure seems to borrow from or leverage Anker's Eufy Security platform, and that's generally the recommendation there.

### Initial login:
```python
import json
from anchormake import ankermake

email = "yourSecondAnkermakeAccountEmail@example.com"
password = "REDACTED" # obviously you'd never just hard code this in a code file
region = "US"
client = ankermake.Client(email, password, region)

login_results = client.login()

if login_results.success:
  login_response = login_results.data
  # login_results.data should be saved somewhere for future interactions
  # I dunno, maybe stick json.dumps(login_results.data) somewhere to json.loads later.

  # The first thing Anker clients like to do...get the printer list and their details:
  results = client.get_fdm_list()
  print(json.dumps(results.data, indent=2))
```

### Using the saved x-auth token from initial login:
```python
import json
from anchormake import ankermake

email = "yourSecondAnkermakeAccountEmail@example.com"
password = "REDACTED" # obviously you'd never just hard code this in a code file
region = "US"

# this is the login_results.data you saved earlier. Token is good for about a month.
login_response_data = json.loads("""{ "user_id":"blahblahblah" ... }""")

client = ankermake.Client(email, password, region, login_response_data)

# If your token is valid, no need to call client.login() again. Doing so
# too much will just put you in the CAPTCHA zone pretty quickly.

results = client.get_fdm_list()
print(json.dumps(results.data, indent=2))
```

### CAPTCHA fun
If the login() call's `results.code == ankermake.ReturnCode.CAPTCHA_REQUIRED` (100032)
then the login response data will contain a CAPTCHA id and a base64 encoded PNG. 

To login, call login() again with the appropriate response:

```python
result = client.login(captcha_id="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", answer="A123")
```

### 

## Contributing

Pull requests are welcome, as are nuggets of info that you discover about AnkerMake APIs and interfaces. Feel free to open an issue first to discuss what you would like to change.

## License

MIT License

Copyright (c) 2022 Chad Fawcett

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.