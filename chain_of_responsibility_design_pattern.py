"""
Identify sequential steps in the code which can be transformed to a chain of steps.

EG:

class NotificationSystem:

    def send_notification(self,notification_type:str,recipient:str,message:str):

        .......

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

        .......

The above if elif block is sequence of steps which can be added as Chain of responsibility
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

# CHAIN OF RESPONSIBILITY HANDLER
class Handler(ABC):
    def __init__(self):
        self.next_handler=None

    def set_next(self,handler):
        self.next_handler=handler
        return handler

    @abstractmethod
    def handle(self,context:dict):
        pass

class InputValidationHandler(Handler):
    def handle(self,context:dict):
        if not context['recipient'] or not context['message']:
            logger.error("Invalid Input")
            return False
        #PASSES ON TO NEXT HANDLER
        if self.next_handler:
            return self.next_handler.handle(context)
        return True

class RetryHandler(Handler):
    def handle(self,context:dict):
        success = context['strategy'].send(
            context['recipient'],context['message']
        )
        if not success:
            return False

        if random.choice([True,False]):
            logger.warning("Temporary Failure")
            time.sleep(1)
        else:
            logger.success("Sent Successfully!")

        # PASSES ON TO NEXT HANDLER
        if self.next_handler:
            return self.next_handler.handle(context)
        return True

class MetricsHandler(Handler):
    def handle(self,context:dict):
        logger.log("Notification processed")
        return True


# SERVICE HANDLER OR CONTEXT HANDLER
class NotificationSystem:

    def __init__(self):
        self.chain=self._build_chain()
    # BUILD THE CHAIN
    def _build_chain(self):
        validation = InputValidationHandler()
        retry = RetryHandler()
        metrics = MetricsHandler()

        validation.set_next(retry).set_next(metrics)
        return validation

    def send_notification(self,notification_type:str,recipient:str,message:str):

        # Logging
        logger.log(f"Preparing to send notification_type : {notification_type} to {recipient}")

        # Gives me object for which the notification will be sent (Factory Design)
        # eg: if notification_type=email it returns EmailNotification() strategy object
        strategy = NotificationFactory.create_notification(notification_type=notification_type)

        context = dict(strategy=strategy,recipient=recipient,message=message)

        # Calls the self.chain used in __init__ which in turn calls the _build_chain which calls each
        # Handler Object which have implemented handle method for which the context is passed
        return self.chain.handle(context)


if __name__=='__main__':
    system = NotificationSystem()

    system.send_notification(notification_type='email',recipient="sanchit10gawde@gmail.com",message="Hello I am email")
    system.send_notification(notification_type='sms',recipient="9029187708",message="Hello I am text message")
    system.send_notification(notification_type='push',recipient="FRIDAY_USER",message="Hello I am firebase message")

    #NEGATIVE:
    system.send_notification(notification_type='sms',recipient="abc@gmail",message="Hello I am text message")

