# WE WILL TRY TO GET RID OF BEHAVIORAL PATTERN done through condition if else statement in the messy code


"""
if notification_type == "email":
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


This behavioral part will change into a well defined strategy using ABC

    """

from abc import ABC,abstractmethod

class NotificationStrategy(ABC):
    @abstractmethod
    def send(self,recipient,message):
        pass

class EmailNotification(NotificationStrategy):
    def send(self,recipient,message):
        #Validation
        if not "@" in recipient:
            print("[ERROR] invalid recipient for email notification")
        #SendGRIDAPI Implementation
        print("[LOG] using SEND GRID API to send email")
        print(f"[sendgrid] sent mail to recipient:{recipient} with message:{message}")

class SMSNotification(NotificationStrategy):
    def send(self,recipient,message):
        #Validation
        if not recipient.isdigit():
            print("[ERROR] invalid recipient for sms notification")
        #TwilioAPI implementation
        print("[LOG] using Twillio API to send email")
        print(f"[twillio] sent message to recipient:{recipient} with message:{message}")

class PushNotification(NotificationStrategy):
    def send(self,recipient,message):
        #FireBase API implementation
        print("[LOG] using Firebase API to send email")
        print(f"[Firebase] sent message to recipient:{recipient} with message:{message}")

# SERVICE HANDLER OR CONTEXT HANDLER
class NotificationSystem:

    def send_notification(self,strategy:NotificationStrategy,recipient:str,message:str):

        # Logging
        print(f"[LOG] Preparing to send notification_type : {strategy} to {recipient}")

        # Basic Validation
        if not recipient or not message:
            print("[ERROR] Invalid Input")
            return False

        success=strategy.send(recipient=recipient,message=message)

        return True