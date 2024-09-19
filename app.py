"""
Create a crypto notification service as an HTTP Rest API server


Create a Notification (Input parameters: Current Price of Bitcoin, Daily Percentage Change, Trading Volume, etc)

Send a notification to email/emails

List notifications (Sent, Pending, Failed)

Update/Delete notification

1. working
2. github repo
3. ajsrinivas@bitgo.com
"""

"""
1. flask app
2. store notification in db - triggers
3. send notification, with an id
4. list registered notification
5. update/delete
"""

from uuid import uuid4

from flask import Flask
from flask import request
from dataclasses import dataclass, asdict
import hashlib
import json
import os

def send_email(email_id, email_payload):
    message = f"Sending payload -> {email_payload} to {email_id}"
    print(message)
    return len(email_payload)


@dataclass
class Notification:
    payload: str
    name: str
    description: str
    id: str = ""

    def render_email(self):
        return self.payload

class NotificationStore:
    def __init__(self):
        self.persistent_file = "notification_doc.json"
        self.store = self.disk_load() or {}

    def disk_load(self):
        if os.path.exists(self.persistent_file):
            with open(self.persistent_file, "r") as fp:
                data = json.load(fp)
                for k, v in data.items():
                    notif = Notification(**v)
                    notif.id = k
                    data[k] = notif
                return data

    def disk_dump(self):
        with open("notification_doc.json", "w") as fp:
            data = {k: asdict(v) for k, v in self.store.items()}
            json.dump(data, fp)

    def add_notification(self, notif: Notification):
        # maybe we should also check for notification duplication at scale, we can use hash instead of random uuid
        notif_id = (
            str(uuid4()) + "-" + hashlib.sha256(notif.payload.encode()).hexdigest()[:10]
        )
        notif.id = notif_id
        self.store[notif_id] = notif
        self.disk_dump()
        return notif_id

    def get(self, notif_id: str) -> Notification: 
        return self.store.get(notif_id)

    def iter_notifs(self):
        for notif in self.store.values():
            yield notif

NotifStore = NotificationStore()

app = Flask(__name__)


@app.route("/set_notification", methods=["POST"])
def set_notification():
    payload = request.json.get("payload")
    name = request.json.get("name")
    description = request.json.get("description")
    if not payload:
        return {"status": "error", "message": "payload is required"}, 400

    notif_id = NotifStore.add_notification(Notification(payload, name, description))
    return {
        "status": "success",
        "message": "notification added successfully",
        "data": {"notification_id": notif_id},
    }


@app.route("/list_notifications", methods=["GET"])
def get_notifications():
    return [
        asdict(notif) for notif in NotifStore.iter_notifs()
    ]


@app.route("/send_notifications", methods=["POST"])
def send_notifications():
    email_address_list = request.json["email_address_list"]
    notif_id = request.json.get("notification_id")

    notification = NotifStore.get(notif_id)
    if not notification:
        return {"status": "error", "message": "unknown notification id"}, 404
    email_success = {}
    # this can be parallelized
    # or it can be pushed to a notification queue, for a more event driven system
    for email in email_address_list:
        success = send_email(email, notification.render_email())
        email_success[email] = success > 0
    success_email_count = sum(email_success.values())
    return {
        "status": "success",
        "message": f"{success_email_count}/{len(email_address_list)} emails sent",
        "email_status": email_success,
    }, 200
