# Django Dynamic Models Through Rest Framework
## Retrieve code

- `$ git clone https://github.com/mohamedmousa1989/olx_scraper.git`
- `$ cd olx_scraper`
### Accessing the database

After installing Mongodb on your system, create a new db
- `$ mongo` --> leading to Mongodb shell
- `$ use <db-name>` --> you need to copy this name to django settings

### Installing

* `$ virtualenv -p /usr/bin/python3.4 virtualenv`
* `$ source virtualenv/bin/activate`
* `$ cd olx_scraper`
* `$ pip install -r requirements.txt`
* `$ python olxscraper/manage.py migrate`

### Running

- `$ python olxscraper/manage.py runserver`

### Testing API
* Send a POST request to 'http://127.0.0.1:8000/scrap-olx/'
containing the following data
{
    "search_keyword": "<search_keyword>",
    "email": "<email_address>",
    "size": <int>
}

### IMPORTANT Note:
The code sends the email to the console; the message body is in HTML
so, if pasted in a file (.html), it will be shown proberly
This is just a work around to avoid having paid SMTP server providers