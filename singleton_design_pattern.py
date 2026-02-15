"""
In this case we will target resource managers which can be initialized only once and used so that it becomes easy
to manage and reduces the memory overhead

Eg in our case we have print statements which are written as loggers those are not extensible and if we need to change them
in future we would have to change into multiple places thus we will create a singleton logger class which will be used
for logging purpose

        print("[LOG] using SEND GRID API to send email")
        print(f"[sendgrid] sent mail to recipient:{recipient} with message:{message}")
        print("[LOG] using Twillio API to send email")
        print(f"[twillio] sent message to recipient:{recipient} with message:{message}")

change this to proper centralised logging class
"""

from abc import ABC,abstractmethod
import random
import time


# ALL THE LOGGING CAN BE NOW CONTROLLED FROM ONE SINGLE CLASS!
class Logger:
    # CLASS Variable is instance
    _instance=None

    def __new__(cls):
        if cls._instance is None:
            # IN THIS CASE object class is being called for which a new instance is being created and stored in
            # _instance will store the value of the new object which is created
            # now after this point whenever anyone calls Logger() if instance is present directly that will be provided
            cls._instance = super(Logger,cls).__new__(cls)
        return cls._instance

    def log(self,message:str):
        print(f"[LOG] {message}")

    def error(self,message:str):
        print(f"[ERROR] {message}")

    def warning(self,message:str):
        print(f"[WARNING] {message}")

    def success(self,message:str):
        print(f"[SUCCESS] {message}")

#Setting logger at global level!
logger = Logger()

# STRATEGY PATTERN
class NotificationStrategy(ABC):
    @abstractmethod
    def send(self,recipient,message):
        pass

class EmailNotification(NotificationStrategy):
    def send(self,recipient,message):
        #Validation
        if not "@" in recipient:
            logger.error("invalid recipient for email notification")
        #SendGRIDAPI Implementation
        logger.log("using SEND GRID API to send email")
        logger.success(f"sent mail to recipient:{recipient} with message:{message}")

class SMSNotification(NotificationStrategy):
    def send(self,recipient,message):
        #Validation
        if not recipient.isdigit():
            logger.error("invalid recipient for sms notification")
        #TwilioAPI implementation
        logger.log("using Twillio API to send email")
        logger.success(f"sent message to recipient:{recipient} with message:{message}")

class PushNotification(NotificationStrategy):
    def send(self,recipient,message):
        #FireBase API implementation
        logger.log("using Firebase API to send email")
        logger.success(f"sent message to recipient:{recipient} with message:{message}")

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
        logger.log(f"Preparing to send notification_type : {notification_type} to {recipient}")

        strategy = NotificationFactory.create_notification(notification_type=notification_type)

        # Basic Validation
        if not recipient or not message:
            logger.error("Invalid Input")
            return False

        success=strategy.send(recipient=recipient,message=message)
        if not success:
            return False

        # Retry Logic (Still messy)
        if random.choice([True,False]):
            logger.warning("Temporary failure retrying...")
            time.sleep(1)
            logger.success("sent after retry")
        else:
            logger.success("sent successfully")

        # METRICS
        logger.success("Notification Processed")

        return True


if __name__=='__main__':
    system = NotificationSystem()

    system.send_notification(notification_type='email',recipient="sanchit10gawde@gmail.com",message="Hello I am email")
    system.send_notification(notification_type='sms',recipient="9029187708",message="Hello I am text message")
    system.send_notification(notification_type='push',recipient="FRIDAY_USER",message="Hello i am firebase message")

    #NEGATIVE:
    system.send_notification(notification_type='sms',recipient="abc@gmail",message="Hello I am text message")

