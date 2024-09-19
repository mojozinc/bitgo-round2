# bitgo-round2
repo for notification storage assignment

## Starting the app
1. setup a python environ with flask, with correct versioning
```
Python 3.12.4
Flask 2.2.3
Werkzeug 2.2.3
```
2. start the server
`flask --app app run`

## sample APIs

### send notification

`curl --location 'localhost:5000/send_notifications' \
--header 'Content-Type: application/json' \
--data-raw '{
	"email_address_list": ["abc@example.com", "xyz@bitgo.com"],
    "notification_id": "b775d402-f4f0-4838-9924-91ad0f7493aa-01bcec038d"
}'`

### add notification
`curl --location 'localhost:5000/set_notification' \
--header 'Content-Type: application/json' \
--data '{
    "payload": "best time to buy is 2008"
}'`

### list notifications
`curl --location 'localhost:5000/list_notifications'`

