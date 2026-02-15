"""
📢 Notification Processing System
Requirements
    Supports:
    Email
    SMS
    Push Notification
Uses third-party providers:
    Twilio (SMS)
    SendGrid (Email)
    Firebase (Push)
Needs:
    Validation before sending
    Logging
    Retry logic
    Event notifications (metrics, alerts)
    Clean API entry point
"""
import random
import time

# VIOLATES SINGLE RESPONSIBILITY one class used for ALL!
# VIOLATES interface segregation if tomorrow someone has to reuse send_notification for their usecase
# Theyll have to use all the notifications which are current provided
class NotificationSystem:
    def __init__(self):
        self.config=dict(email_provider="SendGrid",sms_provider="Twilio",push_provider="firebase")

# LISKOV SUBSTITUTION theres no abstract polymorphism for this to violate
# Since LISKOV is based upon how child class are coded when it comes to its parent class
# with the current code theres only one class

    # Violates SINGLE RESPONSIBILITY one class used for ALL!
    def send_notification(self,notification_type,recipient,message):

        # Logging
        print(f"[LOG] Preparing to send notification_type : {notification_type} to {recipient}")

        # Basic Validation
        if not recipient or not message:
            print("[ERROR] Invalid Input")
            return False

        # IF ELIF VIOLATES OPEN CLOSED PRINCIPLE
        # TOMORROW IF I WANT TO ADD NEW NOTIFICATION SYSTEM I NEED TO UPDATE EXISTING CODE
        # THAT VIOLATES OPEN CLOSED PRINCIPLE which says existing should not be modified but existing can be
        # extended for a new functionality

        if notification_type=="email":
            # VALIDATION for EMAIL SENDING
            if "@" not in recipient:
                print("[ERROR] Invalid Email Address")
                return False

            # DEPENDENCY INVERSION: Violation
            # direct APIS are used we should ideally be pointing to base API class so that
            # tomorrow if sendGridAPI changes to whatsappAPI its seamless.
            # HARDCODING OF sending of mail through sendgrid api
            print("[LOG] using SendGridApi")
            print(f"[sendgrid] sending email to {recipient}:{message}")
            time.sleep(10)
            return None

        elif notification_type == "sms":
            # VALIDATION FOR SMS SENDING
            if not recipient.isdigit():
                print("[ERROR] Invalid Phone number")
                return False

            # HARDCODING OF sending text_message through SMS
            print("[LOG] Using Twillio API")
            print(f"[Twillio] sending SMS to {recipient}:{message}")
            time.sleep(1)

        elif notification_type == "push":
            # HARDCODING OF pushing message through Firebase
            print("[LOG] using FireBase API")
            print(f"[Firebase] sending Push to {recipient}:{message}")
            time.sleep(1)

        else:
            print("[ERROR] unsupported notification type")
            return False

        # RETRY LOGIC
        if random.choice([True,False]):
            print("[WARNING] Temporary failure retrying...")
            time.sleep(1)
            print("[SUCCESS] sent after retry")
        else:
            print("[SUCCESS] sent successfully")


        # METRICS are
        print("[Metrics] Notification Processed")
        return True

if __name__=="__main__":
    notify = NotificationSystem()
    notify.send_notification(notification_type='email',recipient='sanchit10gawde@gmail.com',message='HELLO WORLD!')

