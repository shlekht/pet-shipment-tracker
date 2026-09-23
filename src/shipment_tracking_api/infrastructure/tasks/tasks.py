from email.message import EmailMessage

from shipment_tracking_api.infrastructure.tasks.celery_app import celery


def send_notification_mail_template(shipment: dict, email_to: str):
    email = EmailMessage()

    email["Subject"] = "Shipment status"
    email["From"] = "shipment_app@example.com"
    email["To"] = email_to

    email.set_content(
        f"""
    <h1> Status of your shipment has changed.</h1>
    Your shipment with id: {shipment["id"]} now has status {shipment["status"]}
    Tracking number: {shipment["tracking_number"]}. Date of status change: {shipment["updated_at"]}
""",
        subtype="html",
    )

    return email


@celery.task(name="send_notification_about_status")
def send_notification_about_status(shipment: dict, email_to: str):
    msg_content = send_notification_mail_template(shipment, email_to)
    print(
        f"Mail for {email_to}: (new status: {shipment['status']}, tracking number: {shipment['tracking_number']})"
    )


#         with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
#         server.login(settings.SMTP_USER, settings.SMTP_PASS)
#         server.send_message(msg_content)
