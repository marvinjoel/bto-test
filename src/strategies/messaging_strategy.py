from abc import ABC, abstractmethod


class MessagingStrategy(ABC):

    @abstractmethod
    def send_message(self, recipient, message) -> None:
        pass

    @abstractmethod
    def parse_webhook(self, request_data) -> None:
        pass