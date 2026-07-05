# JWTConfig

JWT расшифровывается как JSON Web Token. Его можно использовать с любым middleware
аутентификации на ваш выбор, включая `AuthenticationMiddleware`.

!!! Tip
    Больше информации о JWT
    <a href="https://jwt.io/introduction" target='_blank'>тут</a>.

## Зависимости

Ravyn использует `pyjwt` и `passlib` для интеграции с JWT. Вы можете установить их, выполнив:

```shell
$ pip install ravyn[jwt]
```

## JWTConfig и приложение

Для использования JWTConfig с middleware.

```python hl_lines="5 8-10 12"
{!> ../../../docs_src/configurations/jwt/example1.py!}
```

!!! info
    В примере используется [JWTAuthMiddleware](../databases/edgy/middleware.md#jwtauthmiddleware)
    из Ravyn с Edgy ORM.

## Параметры

Все параметры и значения по умолчанию доступны в [справке по JWTConfig](../references/configurations/jwt.md).

## JWTConfig и настройки приложения

Конфигурацию JWTConfig можно выполнить напрямую через [инициализацию приложения](#jwtconfig-and-application),
а также с помощью настроек.

```python
{!> ../../../docs_src/configurations/jwt/settings.py!}
```

Это поможет вам поддерживать настройки в чистоте, без перегруженного экземпляра **Ravyn**.

## Модель токена

Ravyn предоставляет стандартный объект токена, который позволяет легко генерировать и декодировать токены.

```python
from ravyn.security.jwt.token import Token

token = Token(exp=..., iat=..., sub=...)
```

Параметры являются стандартными для
[Python JOSE](https://pyjwt.readthedocs.io/en/latest/), так что вы можете чувствовать себя комфортно,
используя их.

### Генерация токена (кодирование)

[Токен](#token-model) предоставляет стандартные операции для взаимодействия с `pyjwt`.

```python
from ravyn.security.jwt.token import Token
from ravyn.conf import settings

# Создание модели токена
token = Token(exp=..., iat=..., sub=...)

# Генерация JWT токена
jwt_token = Token.encode(key=settings.secret_key, algorithm="HS256", **claims)
```

### Декодирование токена (decode)

Функция декодирования также предоставляется.

```python
from ravyn.security.jwt.token import Token
from ravyn.conf import settings

# Декодирование JWT токена
jwt_token = Token.decode(token=..., key=settings.secret_key, algorithms=["HS256"])
```

Метод `Token.decode` возвращает объект [Token](#token-model).

!!! Note
    Эта функциональность сильно зависит от библиотеки `pyjwt`, но её использование не является обязательным.
    Вы можете использовать любую библиотеку, которая соответствует вашим требованиям.
    Ravyn просто предлагает примеры и альтернативы.

### Поля claims

Параметр `**claims` может быть очень полезен, особенно если вы хотите генерировать токены
`access` и `refresh`.
При использовании `claims` вы можете передавать любые дополнительные параметры, которые после
[декодирования](#decode-a-token-decode) будут доступны для манипуляций.

[Интеграция с базой данных](../databases/edgy/example.md) содержит пример выполнения таких операций,
но давайте рассмотрим еще пример.

Мы будем использовать middleware и сгенерируем `access_token` и `refresh_token` для определённого API.

Предположим следующие вещи:

* Есть модель `User` в файле `accounts/models.py`.
* Контроллеры находятся в `accounts/controllers.py`.
* Мы будем наследовать существующий [middleware](../databases/edgy/middleware.md) для упрощения.
* `middleware` находится в файле `accounts/middleware.py`.
* [JWTConfig](#jwtconfig) уже настроен в файле с настройками.
* Класс `Token` будет унаследован для добавления дополнительных параметров, таких как `token_type`.
* В файле `accounts/backends.py` находятся операции для аутентификации и обновления токена.

### Класс Token

Вы должны создать подкласс для `Token`, если хотите добавить дополнительные параметры для своих нужд. Например,
чтобы иметь дополнительный параметр `token_type`, указывающий, является ли токен `access`, `refresh`
или каким-либо другим типом, который вы хотите использовать для ваших claims.

Пример может выглядеть так:

```python
{!> ../../../docs_src/configurations/jwt/claims/token.py!}
```

Это будет особенно полезно на следующих этапах, так как мы будем использовать `token_type`,
чтобы различать `access_token` и `refresh_token`.

#### Middleware

Давайте воспользуемся существующим middleware из [contrib](../databases/edgy/middleware.md), чтобы упростить задачу.
Этот middleware будет служить **только для доступа** к API **и не для обновления токена**.

!!! Tip
    Не стесняйтесь создавать свой собственный middleware, это приведено для пояснения.

```python
{!> ../../../docs_src/configurations/jwt/claims/middleware.py!}
```

Здесь происходит много всего, но в основном мы делаем следующее:

* Проверяем наличие `token` в заголовке.
* Проверяем, является ли `token_type` типом `access_token` (имя по умолчанию из JWTConfig и может быть любым другим)
и вызываем исключение, если это не `access_token`.
* Возвращаем объект `AuthResult` с данными пользователя из БД.

Middleware также содержит обертку под названием `AuthMiddleware`. Она будет использоваться позже в
user controllers.

#### Backend

Здесь мы разместим логику, которая обрабатывает аутентификацию и обновление токена.

!!! Warning
    Пример ниже использует [Edgy](https://edgy.dymmond.com) из [contrib](../databases/edgy/models.md),
    чтобы упростить объяснение и запросы.

```python
{!> ../../../docs_src/configurations/jwt/claims/backends.py!}
```

Довольно много кода, верно? Да, но в основном это логика, используемая для аутентификации и обновления
существующего токена.

Вы видели `BackendAuthentication` и `RefreshAuthentication`? Теперь это будет очень полезно.

`RefreshAuthentication` — это то место, где мы проверяем `refresh_token`. Помните [middleware](#the-middleware),
который позволяет использовать только `access_token`? Middleware будет использоваться только для API,
которые требуют аутентификации, а `refresh_token`, как правило, должен только обновлять access токен и ничего больше.

Поскольку refresh токен уже содержит всю информацию, необходимую для генерации нового access токена,
нет необходимости снова запрашивать `user` и проходить весь процесс.

Способ, которым был спроектирован и передан refresh токен в `claims`, также позволяет нам напрямую
использовать его для генерации нового `access_token`.

Помните [Token](#the-token-class)? Вот где `token_type` играет роль в определении,
какой тип токена проверяется и отправляется.

`access_token` отправляется через `headers` **как и должно быть**, а `refresh_token` отправляется через `POST`.

#### Контроллеры

Теперь пришло время собрать всё в контроллерах, где у нас будут:

* `/auth/create` - Конечная точка для создания пользователей.
* `/auth/signin` - Конечная точка для входа пользователя.
* `/auth/users` - Конечная точка, которая возвращает список всех пользователей.
* `/auth/refresh-access` - Конечная точка, ответственная **только за обновление access_token**.

В итоге, что-то вроде этого:

```python
{!> ../../../docs_src/configurations/jwt/claims/controllers.py!}
```

Как видите, мы теперь собрали всё вместе. Путь `/auth/users` требует аутентификации для доступа,
а `/auth/refresh-access` гарантирует, что будет возвращён только новый `access_token`.
