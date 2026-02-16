# Wrapper for main context handler if you have lot of stuff going on
"""
In our case notificationsytem has being doing lot of things
it building the chain
initializind the observers attaching those
initializing the factory
initializing the strategy
everything

such class when directly exposed to client can be problematic we should hide all this logic using Facade design pattern

"""
"""
In the current system when a notification is sent nothing else react
Lets say if the notificationsystem sends the notification and its being used by
Analytics team
Billing Team
Audit team

It would like:

class NotificationSystem:

    result =  strategy.send()
    #pass the results to required team
    notify_analytics(result)
    notify_billing(result)
    notify_audit(result)

Hardcodinng like this makes it DIP violation we as well OCP violation
since adding or removing notification lets say tomorrow i dont want to notify billing instead notify marketting team
i have to change the notificationSystem again thats where Observer pattern shines
"""

"""
In the current code setup strategy is directly calling EXTERNAL APIS to send mail, sms, push to firebase etc through a
specific set of providers : SendGrid, Twillio and Firebase
Lets say tomorrow we have to change the provider to Google instead of Sendgrid
This will mean we will have to update the email strategy this violates two solid principles

DIP > Dependency inversion is violated since we are doing direct calls to concrete external APIs
OCP > Open closed is violated since new provider means update of strategy thus we are modifying original code!


class EmailNotification(NotificationStrategy):
    def send(self,recipient,message):
        #Validation
        if not "@" in recipient:
            logger.error("invalid recipient for email notification")
        #SendGRIDAPI Implementation PROBLEMS
        logger.log("using SEND GRID API to send email")
        logger.success(f"sent mail to recipient:{recipient} with message:{message}")


We need to fix this using Adapter pattern: used when we have to connect to multiple third party api to solve the same problem
EG:
SendGrid might have send_email(send_name,send_body) as a function to send the mail
Twillio might have send_phone(number, send_stuff) as a function to send the text

Thus theres no common way of doing stuff if directly accessiing external API
Adapter acts as a bridge to address this issue
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

# SIMULATING EXTERNAL APIs

class SendGridAPI:
    def send_jumbo_mail(self,to_name,message_body):
        logger.success(f"JUMBO Mail is sent to {to_name} with {message_body}")
        return True

class TwillioAPI:
    def send_text_message(self,mobile_number,message_content):
        logger.success(f"SMS message sent to {mobile_number} with {message_content}")
        return True

class FireBaseAPI:
    def send_push_message(self,push_id,push_content):
        logger.success(f"PUSH message sent to {push_id} with {push_content}")
        return True

### CREATING A COMMON INTERFACE WHICH STRATEGY CAN POINT TO:

class NotificationProvider:
    @abstractmethod
    def send(self,recipient,message):
        pass

# NOW DEFINING ALL THE ADPATER WHICH WILL IMPLEMENT SEND OF NOTIFICATION PROVIDER
class SendGridAdapter(NotificationProvider):
    def __init__(self):
        self.api=SendGridAPI()

    def send(self,recipient,message):
        return self.api.send_jumbo_mail(to_name=recipient,message_body=message)

class TwillioAdapter(NotificationProvider):
    def __init__(self):
        self.api=TwillioAPI()

    def send(self,recipient,message):
        return self.api.send_text_message(mobile_number=recipient,message_content=message)


class FireBaseAdapter(NotificationProvider):
    def __init__(self):
        self.api = FireBaseAPI()

    def send(self, recipient, message):
        return self.api.send_push_message(push_id=recipient, push_content=message)


# UPDATE THE STRATEGY NOW TO USE THE COMMON NOTIFICATION PROVIDER INSTEAD OF USING HARDCODED CONCRETES
class EmailNotification(NotificationStrategy):
    def __init__(self,provider:NotificationProvider):
        self.provider=provider

    def send(self,recipient,message):
        #Validation
        if not "@" in recipient:
            logger.error("invalid recipient for email notification")
            return False
        # Update to use abc send implemented by concrete strategy
        return self.provider.send(recipient,message)

class SMSNotification(NotificationStrategy):
    def __init__(self,provider:NotificationProvider):
        self.provider=provider

    def send(self,recipient,message):
        #Validation
        if not recipient.isdigit():
            logger.error("invalid recipient for sms notification")
            return False
        return self.provider.send(recipient,message)

class PushNotification(NotificationStrategy):
    def __init__(self,provider:NotificationProvider):
        self.provider=provider

    def send(self,recipient,message):
        return self.provider.send(recipient,message)


#FACTORY TO CENTRALIZE OBJECT CREATION AND MOVE THAT FROM MAIN TO HERE:
# UPDATE FACTORY TO PASS THE PROVIDER OBJECT TO STRATEGY
class NotificationFactory:
    @staticmethod
    def create_notification(notification_type:str) -> NotificationStrategy:
        if notification_type=='email':
            sendgrid_provider = SendGridAdapter()
            return EmailNotification(provider=sendgrid_provider)
        elif notification_type=='sms':
            twillio_provider = TwillioAdapter()
            return SMSNotification(provider=twillio_provider)
        elif notification_type == 'push':
            firebase_provider = FireBaseAdapter()
            return PushNotification(provider = firebase_provider)
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

# DEFINE THE OBSERVER INSTANCE:
class NotificationObserver(ABC):
    @abstractmethod
    def update(self,event_data:dict):
        pass

# CONCRETE ABCs
class AnalyticsObserver(NotificationObserver):
    def update(self,event_data:dict):
        print(f"[Analytics] Recieved the event: {event_data['notification_type']} and the message is {event_data['message']}")

class AuditLogObserver(NotificationObserver):
    def update(self,event_data:dict):
        print(f"[AuditLog] Recieved the event: {event_data['notification_type']} and the recipient is {event_data['recipient']}")

class BillingObserver(NotificationObserver):
    def update(self,event_data:dict):
        print(f"[Billing] Recieved the event: {event_data['notification_type']} and the cost center will be {event_data['recipient']}")

#Notification EVENT HANDLER
class NotificationEventManager:
    def __init__(self):
        self._observer_list = []

    def attach(self,observer:NotificationObserver):
        self._observer_list.append(observer)

    def remove(self,observer:NotificationObserver):
        self._observer_list.remove(observer)

    def notify(self,event_data:dict):
        for observer in self._observer_list:
            observer.update(event_data)


# SERVICE HANDLER OR CONTEXT HANDLER
class NotificationSystem:

    def __init__(self):
        self.chain=self._build_chain()
        self.notification_manager = NotificationEventManager()

        # ADD OBSERVERS TO NOTIFICATION MANAGER
        self.notification_manager.attach(AnalyticsObserver())
        self.notification_manager.attach(AuditLogObserver())
        self.notification_manager.attach(BillingObserver())

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
        #return self.chain.handle(context) -> Now instead of returning the notification output we will pass the successful
        # Notifications to our observers

        if self.chain.handle(context):
            event_data = dict(notification_type=notification_type,recipient=recipient,message=message)
            self.notification_manager.notify(event_data)


class NotificationFacade:
    def __init__(self):
        # This will initialize notification system when NotificationFacade is instantiated
        self._system=NotificationSystem()

    def notify(self,notification_type,recipient,message):
        self._system.send_notification(notification_type,recipient,message)


if __name__=='__main__':

    """
    system = NotificationSystem()

    system.send_notification(notification_type='email',recipient="sanchit10gawde@gmail.com",message="Hello I am email")
    system.send_notification(notification_type='sms',recipient="9029187708",message="Hello I am text message")
    system.send_notification(notification_type='push',recipient="FRIDAY_USER",message="Hello I am firebase message")

    #NEGATIVE:
    system.send_notification(notification_type='sms',recipient="abc@gmail",message="Hello I am text message")
    
    This part should not be done via direct NotificationSystem
    
    instead we create a FACADE 
    """

    notifier = NotificationFacade()
    notifier.notify(notification_type='email',recipient="sanchit10gawde@gmail.com",message="Hello I am email")
    notifier.notify(notification_type='sms',recipient="9029187708",message="Hello I am text message")
    notifier.notify(notification_type='push',recipient="FRIDAY_USER",message="Hello I am firebase message")

