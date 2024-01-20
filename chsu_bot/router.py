"""Обёртка для aiogram."""

from abc import ABC, abstractmethod
from typing import Any, Coroutine

from aiogram import Dispatcher
from aiogram.dispatcher import filters, FSMContext


class Router(ABC):
    """Абстрактный класс для создания хэндлеров всех типов."""

    def __init__(
        self,
        handler: Coroutine[Any, Any, None],
        message_filters: filters = None,
        state: FSMContext = None,
    ) -> None:
        self.filter = message_filters
        self.state = state
        self.handler = handler

    @abstractmethod
    def register(self, router: Dispatcher) -> None:
        """Регистрация всех типов хэндлеров."""
        pass


class MessageRouter(Router):
    """Класс для создания хэндлеров, отвечающих на текстовые сообщения."""

    def register(self, router: Dispatcher) -> None:
        """Регистрация хэндлеров."""
        # router.message_handler(self.filter)(self.handler)
        router.register_message_handler(self.handler, self.filter)


class CallbackRouter(Router):
    """Класс для создания хэндлеров, отвечающих на callback сообщения."""

    def register(self, router: Dispatcher) -> None:
        """Регистрация хэндлеров."""
        #router.callback_query_handler(state=self.state)(self.handler)
        router.register_callback_query_handler(
            callback=self.handler,
            state=self.state,
        )


class ErrorRouter(Router):
    """Класс для создания хэндлеров, отрабатывающих при ошибках."""

    def register(self, router: Dispatcher) -> None:
        """Регистрация хэндлеров, отвечающих на ошибки."""
        #router.errors_handler(self.filter)(self.handler)
        router.register_errors_handler(self.handler, self.filter)


class Routes(Router):
    """Класс для регистрации хэндлеров."""

    def __init__(self, *routes: Router) -> None:
        self.routes = routes

    def register(self, router: Dispatcher) -> None:
        """Регистрация хендлеров бота."""
        for route in self.routes:
            route.register(router)
