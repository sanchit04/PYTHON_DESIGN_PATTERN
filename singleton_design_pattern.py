"""
Even though we removed if-elif inside NotificationSystem,
we pushed that decision to the caller.

The client is creating the objects instead all the object creation has to be done at one place in a factory.

EG from previous code:

if __name__=='__main__':
    system = NotificationSystem()
    email_strategy = EmailNotification()
    sms_strategy = SMSNotification()
    push_strategy = PushNotification()

    system.send_notification(strategy=email_strategy,recipient="sanchit10gawde@gmail.com",message="Hello I am email")
    system.send_notification(strategy=sms_strategy,recipient="9029187708",message="Hello I am text message")
    system.send_notification(strategy=push_strategy,recipient="FRIDAY_USER",message="Hello i am firebase message")

OR

if notification_type == "email":
    EmailNotification()
elif notification_type == "sms":
    SMSNotification()

# In the above case theres direct violation of DIP Dependency Inversion Principle
# Client is depending upon concrete classes EmailNotification(),SMSNotification()


Use Factory Pattern when:
    You see new or direct class instantiation scattered
    Creation logic depends on a type or condition
    You want to hide concrete classes from client
    You want a single place to manage object creation
    You want to reduce coupling

"""

from abc import ABC,abstractmethod
import random
import time

# STRATEGY PATTERN
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

#FACTORY TO CENTRALIZE OBJECT CREATION AND MOVE THAT FROM MAIN TO HERE:
class NotificationFactory:
    @staticmethod
    def create_notification(notification_type:str) -> NotificationStrategy:
        if notification_type=='email':
            return EmailNotification()
        elif notification_type=='sms':
            return SMSNotification()
        elif notification_type == 'push':
            return PushNotification()
        else:
            raise ValueError("Invalid notification type!")


# SERVICE HANDLER OR CONTEXT HANDLER
class NotificationSystem:

    def send_notification(self,notification_type:str,recipient:str,message:str):

        # Logging
        print(f"[LOG] Preparing to send notification_type : {notification_type} to {recipient}")

        strategy = NotificationFactory.create_notification(notification_type=notification_type)

        # Basic Validation
        if not recipient or not message:
            print("[ERROR] Invalid Input")
            return False

        success=strategy.send(recipient=recipient,message=message)
        if not success:
            return False

        # Retry Logic (Still messy)
        if random.choice([True,False]):
            print("[WARNING] Temporary failure retrying...")
            time.sleep(1)
            print("[SUCCESS] sent after retry")
        else:
            print("[SUCCESS] sent successfully")

        # METRICS
        print("[Metrics] Notification Processed")

        return True


if __name__=='__main__':
    system = NotificationSystem()
    # NOT REQUIRED ANYMORE AS WE IMPLEMENTED FACTORY DESIGN PATTERN
    # email_strategy = EmailNotification()
    # sms_strategy = SMSNotification()
    # push_strategy = PushNotification()

    system.send_notification(notification_type='email',recipient="sanchit10gawde@gmail.com",message="Hello I am email")
    system.send_notification(notification_type='sms',recipient="9029187708",message="Hello I am text message")
    system.send_notification(notification_type='push',recipient="FRIDAY_USER",message="Hello i am firebase message")

    #NEGATIVE:
    system.send_notification(notification_type='sms',recipient="abc@gmail",message="Hello I am text message")

