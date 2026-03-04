---
hide:
  - navigation
---

# Ravyn

<p align="center">
  <a href="https://ravyn.dev"><img src="https://res.cloudinary.com/dymmond/image/upload/v1759490296/ravyn/img/logo_pb3fis.png" alt='Ravyn'></a>
</p>

<p align="center">
    <em>🚀 Performance, type safety, and elegance. A next-generation async Python framework for APIs, microservices, and web applications. 🚀</em>
</p>

<p align="center">
<a href="https://github.com/dymmond/ravyn/actions/workflows/test-suite.yml/badge.svg?event=push&branch=main" target="_blank">
    <img src="https://github.com/dymmond/ravyn/actions/workflows/test-suite.yml/badge.svg?event=push&branch=main" alt="Test Suite">
</a>

<a href="https://pypi.org/project/ravyn" target="_blank">
    <img src="https://img.shields.io/pypi/v/ravyn?color=%2334D058&label=pypi%20package" alt="Package version">
</a>

<a href="https://pypi.org/project/ravyn" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/ravyn.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>

---

**Документация**: [https://ravyn.dev](https://www.ravyn.dev) 📚

**Исходный код**: [https://github.com/dymmond/ravyn](https://github.com/dymmond/ravyn)

---
Ravyn — это современный, мощный, гибкий и высокопроизводительный веб-фреймворк, созданный для построения
не только API, но и полноценных масштабируемых приложений — от самых малых до уровня крупных компаний.

Ravyn разрабатывался для Python 3.9+ и использует стандартные подсказки типов (type hints) Python,
основан на широко
известном [Lilya](https://github.com/dymmond/lilya) и [Pydantic](https://github.com/samuelcolvin/pydantic)/[msgspec](https://jcristharif.com/msgspec/).

!!! Success
    **Официально поддерживается только последняя выпущенная версия**.

## Мотивация

Существуют отличные фреймворки такие, как FastAPI, Flama, Flask, Django и другие, решающие большинство
повседневных задач для 99% приложений, но оставляющие тот 1%, который обычно связан со структурой и
бизнес-логикой, без особых решений.

Ravyn черпает вдохновение в этих фреймворках и обладает всеми их известными возможностями,
но также учитывает потребности бизнеса.
Например, Starlite вдохновил на создание трансформеров и моделей Signature, что помогло интеграции с Pydantic.
FastAPI вдохновил дизайн API, Django — систему разрешений, Flask — простоту,
NestJS — контроллеры и многое другое.

Для качественной работы всегда требуется как драйвер, так и источник вдохновения.

## Требования

* Python 3.9+

Ravyn не был бы возможен без следующих двух компонентов:

* <a href="https://lilya.dev/" class="external-link" target="_blank">Lilya</a>
* <a href="https://pydantic-docs.helpmanual.io/" class="external-link" target="_blank">Pydantic</a>

## Установка

```shell
$ pip install ravyn
```

Для работы в продакшене также потребуется ASGI сервер, рекомендуем [Palfrey](https://palfrey.dymmond.com), но выбор остается за вами.

```shell
$ pip install palfrey
```

**Поддержка встроенного планировщика:**:

```shell
$ pip install ravyn[schedulers]
```

**Поддержка JWT, используемого внутри Ravyn:**:

```shell
$ pip install ravyn[jwt]
```

**Для использования клиента тестирования Ravyn:**:

```shell
$ pip install ravyn[test]
```

**Для использования оболочки Ravyn:**:

Подробнее [здесь](./directives/shell.md) по теме в [документации](./directives/shell.md).

```shell
$ pip install ravyn[ipython] # default shell
$ pip install ravyn[ptpython] # ptpython shell
```

### Начало проекта с использованием директив

!!! Warning
    Директивы рассчитаны на опытных пользователей, которые уже знакомы с Ravyn (или Python в целом),
    или если использование директив не вызывает затруднений. Если пока не чувствуете уверенности, продолжайте
    изучать документацию и знакомиться с Ravyn.

Чтобы начать Ravyn проект с простой предложенной структурой, выполните:

```shell
ravyn createproject <YOUR-PROJECT-NAME> --simple
```

Это создаст каркас проекта с некоторыми предопределенными файлами для простого запуска приложения Ravyn.

Также будет создан файл для тестов с использованием RavynTestClient, так что выполните:

```shell
$ pip install ravyn[test]
```

Эту часть можно пропустить, если не хотите использовать RavynTestClient.

Подробная [информация](./directives/directives.md) об этой директиве и примерах ее использования.

!!! Warning
    Запуск этой [директивы](./directives/directives.md) создает только каркас проекта, и для его
    запуска потребуются дополнительные данные.
    Этот каркас лишь предоставляет структуру файлов для начала работы, **но не является обязательным**.

## Основные функции
* **Быстрый и эффективный**: Благодаря Lilya и Pydantic/msgpec.
* **Быстрое развитие**: Простота дизайна значительно сокращает время разработки.
* **Интуитивно понятный**: Если знакомы с другими фреймворками, работать с Ravyn не составит труда.
* **Простота**: Создан с учетом удобства и легкости в изучении.
* **Компактный**: Благодаря встроенной поддержке ООП нет необходимости дублировать код. Поддержка SOLID.
* **Готовый к работе**: Приложение запускается с готовым к продакшену кодом.
* **ООП и функциональный стиль**: Проектируйте API любым удобным способом, поддержка ООП и функционального стиля.
* **Асинхронный и синхронный**: Поддерживает как синхронный, так и асинхронный режимы.
* **Middleware**: Применяйте middleware на уровне приложения или API.
* **Обработчики исключений**: Применяйте обработчики на любом уровне.
* **Permissions**: Применяйте правила и permissions для каждого API.
* **Interceptors**: Перехватывайте запросы и добавляйте логику перед обработкой.
* **Плагины**: Создавайте плагины для Ravyn и интегрируйте их в любое приложение, или опубликуйте свой пакет.
* **DAO и AsyncDAO**: Избегайте вызовов базы данных напрямую из API, используйте бизнес-объекты.
* **Поддержка ORM**: Поддержка [Edgy][_orm].
* **Поддержка ODM**: Поддержка [Mongoz][mongoz_odm].
* **Controller**: Контроллеры в виде классов.
* **JSON сериализация/десериализация**: Поддержка UJSON и ORJSON.
* **Lifespan**: Поддержка lifespan Lilya.
* **Внедрение зависимостей**: Как в любом хорошем фреймворке.
* **Планировщик**: Поддержка задач в фоне.
* **Настройки**: Поддержка системы настроек для чистоты кода.
* **msgspec** — поддержка `msgspec`.

## Отношение к Lilya и другим фреймворкам

Ravyn использует Lilya. Это решение обусловлено высокой производительностью и отсутствием проблем с маршрутизацией.

Ravyn поощряет стандартные практики и подходы к дизайну, что позволяет использовать его как для малых,
так и для крупных приложений, не испытывая проблем с масштабируемостью.

## Быстрый старт

Пример как быстро начать работу с Ravyn.
Для быстрого старта используйте `palfrey`.

```python
#!/usr/bin/env python
import palfrey

from ravyn import Ravyn, Gateway, JSONResponse, Request, get


@get()
def welcome() -> JSONResponse:
    return JSONResponse({"message": "Welcome to Ravyn"})


@get()
def user(user: str) -> JSONResponse:
    return JSONResponse({"message": f"Welcome to Ravyn, {user}"})


@get()
def user_in_request(request: Request) -> JSONResponse:
    user = request.path_params["user"]
    return JSONResponse({"message": f"Welcome to Ravyn, {user}"})


app = Ravyn(
    routes=[
        Gateway("/ravyn", handler=welcome),
        Gateway("/ravyn/{user}", handler=user),
        Gateway("/ravyn/in-request/{user}", handler=user_in_request),
    ]
)

if __name__ == "__main__":
    palfrey.run(app, port=8000)
```

Затем вы можете получить доступ к endpoints.

### Использование Ravyn в качестве декоратора

Чтобы быстро начать работу с Ravyn, вы также можете использовать его как декоратор. Вот как это
сделать на примере с `palfrey`.

```python
#!/usr/bin/env python
import palfrey

from ravyn import Ravyn, Gateway, JSONResponse, Request, get

app = Ravyn()


@app.get("/ravyn")
def welcome() -> JSONResponse:
    return JSONResponse({"message": "Welcome to Ravyn"})


@app.get("/ravyn/{user}")
def user(user: str) -> JSONResponse:
    return JSONResponse({"message": f"Welcome to Ravyn, {user}"})


@app.get("/ravyn/in-request/{user}")
def user_in_request(request: Request) -> JSONResponse:
    user = request.path_params["user"]
    return JSONResponse({"message": f"Welcome to Ravyn, {user}"})


if __name__ == "__main__":
    palfrey.run(app, port=8000)
```

## Настройки

Как и в любом другом фреймворке, при запуске приложения множество [настроек](./application/settings.md)
можно или необходимо передать главному объекту, что иногда выглядит сложно и неудобно для поддержки и восприятия.

Ravyn изначально учитывает [настройки](./application/settings.md). Набор параметров по умолчанию можно
изменить, используя собственный модуль настроек, но при этом вы также можете использовать классический подход,
передавая все параметры непосредственно при создании экземпляра Ravyn.

**Пример классического подхода**:

```python
from example import ApplicationObjectExample

# ExampleObject — это экземпляр другого приложения,
# и он служит только в качестве примера

app = ApplicationObjectExample(setting_one=..., setting_two=..., setting_three=...)

```

Вдохновленный замечательным [Django](https://www.djangoproject.com/) и используя pydantic,
Ravyn предоставляет объект по умолчанию, готовый к использованию сразу «из коробки».

**Ravyn**:

```python
from ravyn import Ravyn

app = Ravyn()

```

И это все! **Все настройки по умолчанию загружаются автоматически**! Почему?
Потому что **приложение ищет переменную окружения `RAVYN_SETTINGS_MODULE` для запуска**,
и если она не найдена, используются глобальные настройки приложения. Это просто, но можно ли
переопределить их внутри объекта? Да, конечно.

```python
from ravyn import Ravyn

app = Ravyn(app_name='My App', title='My title')

```

То же самое, что и классический подход.

Давайте поговорим о [модуле настроек Ravyn](#ravyn-settings-module).

### Модуль настроек Ravyn

При запуске приложения система ищет переменную окружения
`RAVYN_SETTINGS_MODULE`. Если переменная не указана, система по умолчанию использует настройки
`RavynSettings` и запускается.

### Пользовательские настройки

В наше время важно разделять настройки по окружениям и стандартных настроек Ravyn будет недостаточно
для любого приложения.

Настройки соответствуют стандарту pydantic и, следовательно, совместимы с Ravyn.
Система предоставляет несколько значений по умолчанию, которые можно использовать сразу, хотя это необязательно.
Окружение по умолчанию — **production**.

```python
from ravyn import RavynSettings
from ravyn.conf.enums import EnvironmentType


class Development(RavynSettings):
    app_name: str = 'My app in dev'
    environment: str = EnvironmentType.DEVELOPMENT

```

**Загрузка настроек в ваше приложение Ravyn**:

Предположим, ваше приложение Ravyn находится в файле `src/app.py`.

=== "MacOS & Linux"

    ```console
    RAVYN_SETTINGS_MODULE='myapp.settings.Development' python -m src.app.py
    ```

=== "Windows"

    ```console
    $env:RAVYN_SETTINGS_MODULE="myapp.settings.Development"; python -m src.app.py
    ```

## Gateway, WebSocketGateway и Include

Lilya предлагает классы `Path` для простых назначений путей, но это также очень ограничивает,
если у вас есть что-то более сложное. Ravyn расширяет эту функциональность и добавляет немного
'стиля', улучшая её с помощью [Gateway](./routing/routes.md#gateway),
[WebSocketGateway](./routing/routes.md#websocketgateway) и [Include](./routing/routes.md#include).

Эти специальные объекты позволяют происходить всей магии Ravyn.


**Для классического, прямого подхода в одном файле**:

=== "In a nutshell"

    ```python title='src/app.py'
    from ravyn import Ravyn, Gateway, JSONResponse, Request, Websocket, WebSocketGateway, get, status


    @get(status_code=status.HTTP_200_OK)
    async def home() -> JSONResponse:
        return JSONResponse({
            "detail": "Hello world"
        })


    @get()
    async def another(request: Request) -> dict:
        return {
            "detail": "Another world!"
        }


    @websocket(path="/{path_param:str}")
    async def world_socket(socket: Websocket) -> None:
        await socket.accept()
        msg = await socket.receive_json()
        assert msg
        assert socket
        await socket.close()


    app = Ravyn(routes=[
        Gateway(handler=home),
        Gateway(handler=another),
        WebSocketGateway(handler=world_socket),
    ])

    ```

## Дизайн маршрутов

Хороший дизайн всегда приветствуется и Ravyn позволяет создавать сложные маршруты на любом
[уровне](./application/levels.md).

### Обработчики (контроллеры)

```python title="src/myapp/accounts/controllers.py"
{!> ../../../docs_src/routing/routes/include/controllers.py!}
```

Если `path` не указан, по умолчанию используется `/`.

### Gateways (urls)

```python title="myapp/accounts/urls.py" hl_lines="5-10"
from ravyn import Gateway, WebSocketGateway
from .controllers import home, another, world_socket, World

route_patterns = [
    Gateway(handler=home),
    Gateway(handler=another),
    Gateway(handler=World),
    WebSocketGateway(handler=world_socket),
]

```

Если `path` не указан, по умолчанию используется `/`.

### Include

Это специальный объект, который позволяет `импортировать` любой маршрут из любого места в приложении.

`Include` принимает импорт через `namespace` или через список `routes`, но не оба одновременно.

При использовании `namespace` `Include` будет искать список объектов по умолчанию `route_patterns` в
импортированном пространстве имен, если не указано другое.

!!! note
    Шаблон (route_patterns) работает только в том случае, если импорт выполнен через `namespace`, а не через `routes`.

=== "Importing using namespace"

    ```python title='src/urls.py' hl_lines="3"
    {!> ../../../docs_src/routing/routes/include/app/urls.py!}
    ```

=== "Importing using routes"

    ```python title='src/myapp/urls.py' hl_lines="5"
    {!> ../../../docs_src/routing/routes/include/routes_list.py!}
    ```

Если `path` не указан, по умолчанию используется `/`.

#### Using a different pattern

```python title="src/myapp/accounts/urls.py" hl_lines="5"
{!> ../../../docs_src/routing/routes/include/different_pattern.py!}
```

=== "Importing using namespace"

    ```python title='src/myapp/urls.py' hl_lines="3"
    {!> ../../../docs_src/routing/routes/include/namespace.py!}
    ```

## Include и Ravyn

`Include` может быть очень полезен, особенно когда цель — избежать множества импортов и огромного списка объектов,
которые нужно передать в один единственный объект. Это может быть особенно полезно для создания экземпляра Ravyn.

**Пример**:

```python title='src/urls.py' hl_lines="3"
{!> ../../../docs_src/routing/routes/include/app/urls.py!}
```

```python title='src/app.py' hl_lines="3"
{!> ../../../docs_src/routing/routes/include/app/app.py!}
```

## Запуск приложения

Как уже упоминалось, мы рекомендуем использовать palfrey в производственной среде, но это не обязательно.

**Использование palfrey**:

```shell
palfrey src:app --reload

INFO:     Palfrey running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Запуск приложения с пользовательскими настройками

**Использование palfrey**:

=== "MacOS & Linux"

    ```shell
    RAVYN_SETTINGS_MODULE=myapp.AppSettings palfrey src:app --reload

    INFO:     Palfrey running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

=== "Windows"

    ```shell
    $env:RAVYN_SETTINGS_MODULE="myapp.AppSettings"; palfrey src:app --reload

    INFO:     Palfrey running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

## Документация OpenAPI

Ravyn также имеет встроенную документацию OpenAPI.

Ravyn автоматически запускает документацию OpenAPI, внедряя настройки OpenAPIConfig по умолчанию
и предоставляет вам элементы Swagger, ReDoc и Stoplight "из коробки".

Чтобы получить доступ к OpenAPI, просто запустите вашу локальную разработку и перейдите по адресу:

* **Swagger** - `/docs/swagger`.
* **Redoc** - `/docs/redoc`.
* **Stoplight Elements** - `/docs/elements`.
* **Rapidoc** - `/docs/rapidoc`.

В этой документации есть более подробная информация о том, как настроить OpenAPIConfig [здесь](./configurations/openapi/config.md).

Также представлено хорошее объяснение о том, как использовать [OpenAPIResponse](./responses.md#openapi-responses).

## Заметки

Это всего лишь очень общее демонстрационное описание того, как быстро начать и что может предложить Ravyn.
Существует множество других возможностей, которые вы можете использовать с Ravyn. Наслаждайтесь! 😊

## Спонсоры

В настоящее время у Ravyn нет спонсоров, но вы можете финансово помочь и поддержать автора через
[GitHub sponsors](https://github.com/sponsors/tarsil) и стать **Особенным** или **Легендой**.

[edgy_orm]: ./databases/edgy/motivation.md
[mongoz_odm]: ./databases/mongoz/motivation.md
