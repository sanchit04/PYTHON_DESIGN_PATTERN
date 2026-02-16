from abc import ABC, abstractmethod
import random
import time


# ==================================================
# SINGLETON
# ==================================================

class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def log(self, message):
        print(f"[LOG] {message}")

    def error(self, message):
        print(f"[ERROR] {message}")

    def warning(self, message):
        print(f"[WARNING] {message}")

    def success(self, message):
        print(f"[SUCCESS] {message}")


logger = Logger()


# ==================================================
# BUILDER + DOMAIN OBJECT
# ==================================================

class Notification:
    def __init__(self, notification_type, recipient, message,
                 priority="normal", retry_count=1, metadata=None):
        self.notification_type = notification_type
        self.recipient = recipient
        self.message = message
        self.priority = priority
        self.retry_count = retry_count
        self.metadata = metadata or {}


class NotificationBuilder:
    def __init__(self):
        self._notification_type = None
        self._recipient = None
        self._message = None
        self._priority = "normal"
        self._retry_count = 1
        self._metadata = {}

    def set_type(self, notification_type):
        self._notification_type = notification_type
        return self

    def set_recipient(self, recipient):
        self._recipient = recipient
        return self

    def set_message(self, message):
        self._message = message
        return self

    def set_priority(self, priority):
        self._priority = priority
        return self

    def set_retry(self, retry_count):
        self._retry_count = retry_count
        return self

    def add_metadata(self, key, value):
        self._metadata[key] = value
        return self

    def build(self):
        if not self._notification_type or not self._recipient or not self._message:
            raise ValueError("Missing required fields")
        return Notification(
            self._notification_type,
            self._recipient,
            self._message,
            self._priority,
            self._retry_count,
            self._metadata
        )


# ==================================================
# STRATEGY
# ==================================================

class NotificationStrategy(ABC):
    @abstractmethod
    def send(self, notification: Notification):
        pass


# ==================================================
# EXTERNAL APIs
# ==================================================

class SendGridAPI:
    def send_jumbo_mail(self, to_name, message_body):
        logger.success(f"JUMBO Mail sent to {to_name} with {message_body}")
        return True


class TwillioAPI:
    def send_text_message(self, mobile_number, message_content):
        logger.success(f"SMS sent to {mobile_number} with {message_content}")
        return True


class FireBaseAPI:
    def send_push_message(self, push_id, push_content):
        logger.success(f"PUSH sent to {push_id} with {push_content}")
        return True


# ==================================================
# ADAPTER
# ==================================================

class NotificationProvider(ABC):
    @abstractmethod
    def send(self, recipient, message):
        pass


class SendGridAdapter(NotificationProvider):
    def __init__(self):
        self.api = SendGridAPI()

    def send(self, recipient, message):
        return self.api.send_jumbo_mail(recipient, message)


class TwillioAdapter(NotificationProvider):
    def __init__(self):
        self.api = TwillioAPI()

    def send(self, recipient, message):
        return self.api.send_text_message(recipient, message)


class FireBaseAdapter(NotificationProvider):
    def __init__(self):
        self.api = FireBaseAPI()

    def send(self, recipient, message):
        return self.api.send_push_message(recipient, message)


# ==================================================
# STRATEGY IMPLEMENTATIONS
# ==================================================

class EmailNotification(NotificationStrategy):
    def __init__(self, provider):
        self.provider = provider

    def send(self, notification: Notification):
        if "@" not in notification.recipient:
            logger.error("Invalid email recipient")
            return False
        return self.provider.send(notification.recipient, notification.message)


class SMSNotification(NotificationStrategy):
    def __init__(self, provider):
        self.provider = provider

    def send(self, notification: Notification):
        if not notification.recipient.isdigit():
            logger.error("Invalid SMS recipient")
            return False
        return self.provider.send(notification.recipient, notification.message)


class PushNotification(NotificationStrategy):
    def __init__(self, provider):
        self.provider = provider

    def send(self, notification: Notification):
        return self.provider.send(notification.recipient, notification.message)


# ==================================================
# FACTORY
# ==================================================

class NotificationFactory:
    @staticmethod
    def create(notification_type):
        if notification_type == "email":
            return EmailNotification(SendGridAdapter())
        elif notification_type == "sms":
            return SMSNotification(TwillioAdapter())
        elif notification_type == "push":
            return PushNotification(FireBaseAdapter())
        else:
            raise ValueError("Invalid notification type")


# ==================================================
# CHAIN OF RESPONSIBILITY
# ==================================================

class Handler(ABC):
    def __init__(self):
        self.next_handler = None

    def set_next(self, handler):
        self.next_handler = handler
        return handler

    @abstractmethod
    def handle(self, context):
        pass


class RetryHandler(Handler):
    def handle(self, context):
        notification = context["notification"]
        strategy = context["strategy"]

        attempts = notification.retry_count

        for attempt in range(attempts):
            success = strategy.send(notification)
            if success:
                logger.success("Sent successfully")
                break
            logger.warning(f"Retry attempt {attempt + 1}")

        if not success:
            return False

        if self.next_handler:
            return self.next_handler.handle(context)
        return True


class MetricsHandler(Handler):
    def handle(self, context):
        logger.log("Notification processed")
        return True


# ==================================================
# OBSERVER
# ==================================================

class NotificationObserver(ABC):
    @abstractmethod
    def update(self, notification: Notification):
        pass


class AnalyticsObserver(NotificationObserver):
    def update(self, notification):
        print(f"[Analytics] {notification.notification_type} sent")


class AuditObserver(NotificationObserver):
    def update(self, notification):
        print(f"[Audit] Recipient: {notification.recipient}")


class BillingObserver(NotificationObserver):
    def update(self, notification):
        print(f"[Billing] Priority: {notification.priority}")


class NotificationEventManager:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def notify(self, notification):
        for observer in self._observers:
            observer.update(notification)


# ==================================================
# SUBSYSTEM
# ==================================================

class NotificationSystem:
    def __init__(self):
        self.chain = self._build_chain()
        self.event_manager = NotificationEventManager()

        self.event_manager.attach(AnalyticsObserver())
        self.event_manager.attach(AuditObserver())
        self.event_manager.attach(BillingObserver())

    def _build_chain(self):
        retry = RetryHandler()
        metrics = MetricsHandler()
        retry.set_next(metrics)
        return retry

    def send(self, notification: Notification):
        logger.log(f"Preparing to send {notification.notification_type}")

        strategy = NotificationFactory.create(notification.notification_type)

        context = {
            "notification": notification,
            "strategy": strategy
        }

        if self.chain.handle(context):
            self.event_manager.notify(notification)


# ==================================================
# FACADE
# ==================================================

class NotificationFacade:
    def __init__(self):
        self.system = NotificationSystem()

    def notify(self, notification: Notification):
        self.system.send(notification)


# ==================================================
# CLIENT
# ==================================================

if __name__ == "__main__":

    notifier = NotificationFacade()

    notification = (
        NotificationBuilder()
            .set_type("email")
            .set_recipient("test@gmail.com")
            .set_message("Hello Builder Pattern")
            .set_priority("high")
            .set_retry(2)
            .add_metadata("campaign", "Diwali Sale")
            .build()
    )

    notifier.notify(notification)
