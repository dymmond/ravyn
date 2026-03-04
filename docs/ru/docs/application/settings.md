# Настройки

С увеличением сложности проекта и распределением настроек по всему коду, начинается беспорядок.

Отличный фреймворк Django предоставляет свой способ управления настройками, но из-за наследия кода и сложности,
накопившейся за почти 20 лет разработки, они стали громоздкими и трудными для поддержки.

Вдохновленный Django и опытом 99% разработанных приложений, Ravyn оснащен механизмом для работы с
настройками на нативном уровне,
используя [Pydantic](https://pydantic-docs.helpmanual.io/visual_studio_code/#basesettings-and-ignoring-pylancepyright-errors) для их обработки.

!!! Note
    Начиная с версии 0.8.X, Ravyn позволяет использовать настройки на разных [уровнях](./levels.md),
    делая их полностью модульными.

## Способы использования настроек

В приложении Ravyn существует два способа использования объекта настроек:

* Использование **RAVYN_SETTINGS_MODULE**
* Использование **[settings_module](#the-settings_module)**

Каждый из этих методов имеет свои специфические случаи применения, но также они могут работать вместе.

## RavynSettings и приложение

При запуске экземпляра Ravyn, если параметры не указаны, автоматически загружаются настройки по умолчанию
из системного объекта настроек — `RavynSettings`.

=== "No parameters"

    ```python hl_lines="4"
    {!> ../../../docs_src/settings/app/no_parameters.py!}
    ```

=== "With Parameters"

    ```python hl_lines="6"
    {!> ../../../docs_src/settings/app/with_parameters.py!}
    ```

## Пользовательские настройки

Использование настроек по умолчанию из `RavynSettings` возможно не будет достаточно
для большинства приложений.

Поэтому требуются пользовательские настройки.

**Все пользовательские настройки должны быть унаследованы от `RavynSettings`**.

Предположим, у нас есть три среды для одного приложения: `production`, `testing`, `development` и файл
базовых настроек, содержащий общие настройки для всех трех сред.

=== "Base"

    ```python
    {!> ../../../docs_src/settings/custom/base.py!}
    ```

=== "Development"

    ```python
    {!> ../../../docs_src/settings/custom/development.py!}
    ```

=== "Testing"

    ```python
    {!> ../../../docs_src/settings/custom/testing.py!}
    ```

=== "Production"

    ```python
    {!> ../../../docs_src/settings/custom/production.py!}
    ```

Что произошло

1. Создан `AppSettings`, унаследованный от `RavynSettings` с общими свойствами для всех сред.
2. Создан по одному файлу настроек для каждой среды, унаследованных от базового `AppSettings`.
3. Импортированы специфические настройки базы данных для каждой среды и добавлены события `on_startup` и `on_shutdown`, уникальные для каждой среды.


## Модуль настроек Ravyn

По умолчанию Ravyn ищет переменную окружения `RAVYN_SETTINGS_MODULE` для выполнения любых
пользовательских настроек. Если переменная не указана, будут выполнены настройки приложения по умолчанию.

=== "Without RAVYN_SETTINGS_MODULE"

    ```shell
    palfrey src:app --reload

    INFO:     Palfrey running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

=== "With RAVYN_SETTINGS_MODULE MacOS & Linux"

    ```shell
    RAVYN_SETTINGS_MODULE=src.configs.production.ProductionSettings palfrey src:app

    INFO:     Palfrey running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

=== "With RAVYN_SETTINGS_MODULE Windows"

    ```shell
    $env:RAVYN_SETTINGS_MODULE="src.configs.production.ProductionSettings"; palfrey src:app

    INFO:     Palfrey running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

Это очень просто: `RAVYN_SETTINGS_MODULE` ищет класс пользовательских настроек, созданный для приложения
и загружает его в ленивом режиме.


## Модуль настроек (settings_module)

Это отличный инструмент для того, чтобы сделать ваши приложения Ravyn полностью независимыми и модульными.
Бывают случаи, когда вам просто нужно подключить существующее приложение Ravyn к другому, а это приложение
уже имеет уникальные настройки и значения по умолчанию.

`settings_module` — это параметр, доступный в каждом экземпляре `Ravyn` и `ChildRavyn`.

### Создание settings_module

`settings_module` имеет **абсолютно тот же принцип**, что и
[RavynSettings](#ravynapisettings-and-the-application), это означает, что каждый `settings_module`
**должен быть унаследован от RavynSettings**, иначе будет выброшено исключение `ImproperlyConfigured`.

Причина этого заключается в том, чтобы сохранить целостность приложения и настроек.

```python hl_lines="22"
{!> ../../../docs_src/application/settings/settings_config/example2.py !}
```

Ravyn упрощает управление настройками на каждом уровне, сохраняя при этом целостность.

Посмотрите [порядок приоритетов](#order-of-priority), чтобы понять это немного лучше.

## Порядок приоритетов

Существует порядок приоритетов, в котором Ravyn считывает ваши настройки.

Если в экземпляр Ravyn передан `settings_module`, этот объект имеет приоритет над всем остальным.

Предположим следующее:

* Приложение Ravyn с обычными настройками.
* ChildRavyn со специфическим набором конфигураций, уникальных для него.

```python hl_lines="11"
{!> ../../../docs_src/application/settings/settings_config/example1.py !}
```

**Что здесь происходит**

В приведенном выше примере мы:

1. Создали объект настроек, унаследованный от основного `RavynSettings передали некоторые
значения по умолчанию.
2. Передали `ChildRavynSettings` в экземпляр `ChildRavyn`.
3. Передали `ChildRavyn` в приложение `Ravyn`.

Итак, как осуществляется приоритет с использованием `settings_module`?

1. Если значение параметра (при создании экземпляра), например `app_name`, не указано, будет проверено
это же значение внутри `settings_module`.
2. Если `settings_module` не предоставляет значение `app_name`, оно будет искать значение в
`RAVYN_SETTINGS_MODULE`.
3. Если переменная окружения `RAVYN_SETTINGS_MODULE` вами не указана, то будет использовано значение
по умолчанию Ravyn. [Узнайте больше об этом здесь](#ravyn-settings-module).

Таким образом, порядок приоритетов:

1. Значение параметра экземпляра имеет приоритет над `settings_module`.
2. `settings_module` имеет приоритет над `RAVYN_SETTINGS_MODULE`.
3. `RAVYN_SETTINGS_MODULE` проверяется последним.

## Конфигурация настроек и settings_module Ravyn

Красота этого модульного подхода заключается в том, что он позволяет использовать **оба** подхода одновременно
([порядок приоритетов](#order-of-priority)).

Рассмотрим пример, где:

1. Мы создаем основной объект настроек Ravyn, который будет использоваться `RAVYN_SETTINGS_MODULE`.
2. Мы создаем `settings_module`, который будет использоваться экземпляром Ravyn.
3. Мы запускаем приложение, используя оба варианта.

Также предположим, что у вас все настройки находятся в директории `src/configs`.

**Создайте конфигурацию для использования RAVYN_SETTINGS_MODULE**

```python title="src/configs/main_settings.py"
{!> ../../../docs_src/application/settings/settings_config/main_settings.py !}
```

**Создайте конфигурацию для использования в setting_config**

```python title="src/configs/app_settings.py"
{!> ../../../docs_src/application/settings/settings_config/app_settings.py !}
```

**Создайте экземпляр Ravyn**

```python title="src/app.py" hl_lines="14"
{!> ../../../docs_src/application/settings/settings_config/app.py !}
```

Теперь мы можем запустить сервер, используя `AppSettings` в качестве глобальных настроек, а `InstanceSettings`,
передавая их при создании экземпляра. `AppSettings` из файла main_settings.py используется для вызова из
командной строки.

=== "MacOS & Linux"

    ```shell
    RAVYN_SETTINGS_MODULE=src.configs.main_settings.AppSettings palfrey src:app --reload

    INFO:     Palfrey running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

=== "Windows"

    ```shell
    $env:RAVYN_SETTINGS_MODULE="src.configs.main_settings.AppSettings"; palfrey src:app --reload

    INFO:     Palfrey running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

Отлично! Теперь мы  использовали `settings_module` и `RAVYN_SETTINGS_MODULE` одновременно!

Посмотрите на [порядок приоритетов](#order-of-priority), чтобы понять, какое значение имеет приоритет и
как Ravyn их считывает.

## Параметры

Параметры, доступные внутри `RavynAPIExceptionSettingsмогут быть переопределены любыми пользовательскими настройками.
Подробнее в [справочнике по настройкам](../references/application/settings.md).

!!! Check
    Все конфигурации являются объектами Pydantic. Ознакомьтесь с [CORS](../configurations/cors.md),
    [CSRF](../configurations/csrf.md), [Session](../configurations/session.md), [JWT](../configurations/session.md),
    [StaticFiles](../configurations/staticfiles.md), [Template](../configurations/template.md) и
    [OpenAPI](../configurations/openapi/config.md), чтобы узнать, как их использовать.

**Примечание**: Чтобы понять, какие параметры существуют, а также соответствующие значения, обратитесь к
[справочнику по настройкам](../references/application/settings.md).


## Доступ к настройкам

Существует несколько способов доступа к настройкам приложения:

=== "Из request приложения"

    ```python hl_lines="6"
    {!> ../../../docs_src/settings/access/within_app.py!}
    ```

=== "Из глобальных настроек"

    ```python hl_lines="1 6"
    {!> ../../../docs_src/settings/access/global.py!}
    ```

=== "Из настроек конфигурации"

    ```python hl_lines="2 7"
    {!> ../../../docs_src/settings/access/conf.py!}
    ```

!!! info
    Некоторая информация могла быть упомянута в других частях документации, но мы предполагаем,
    что читатели могли её пропустить.

## Порядок важности

Использование настроек для запуска приложения вместо предоставления параметров напрямую в момент создания
экземпляра не означает, что одно будет работать с другим.

При создании экземпляра приложения **либо вы передаете параметры напрямую, либо используете настройки,
либо смешиваете оба подхода**.

Передача параметров в объект всегда будет переопределять значения из настроек по умолчанию.

```python
from ravyn import RavynSettings
from ravyn.middleware.https import HTTPSRedirectMiddleware
from ravyn.types import Middleware
from lilya.middleware import DefineMiddleware


class AppSettings(RavynSettings
debug: bool = False

              @ property


def middleware(self) -> List[Middleware]:
    return [DefineMiddleware(HTTPSRedirectMiddleware)]

```

Приложение будет:

1. Запущено с `debug` как `False`.
2. Запущено с промежуточным ПО `HTTPSRedirectMiddleware`.

Запуск приложения с вышеуказанными настройками обеспечит наличие начального
`HTTPSRedirectMiddleware` и значения `debug`, **но** что произойдет, если вы используете настройки вместе
с параметрами при создании экземпляра?

```python
from ravyn import Ravyn

app = Ravyn(debug=True, middleware=[])
```

Приложение будет:

1. Запущено с `debug` как `True`.
2. Запущено без пользовательских middlewares, если `HTTPSRedirectMiddleware` был переопределён на `[]`.

Хотя в настройках было указано начать с `HTTPSRedirectMiddleware` и `debug` как `False`,
как только вы передаете разные значения при создании объекта `Ravyn`,
эти значения становятся приоритетными.

**Объявление параметров в экземпляре всегда будет иметь приоритет над значениями из ваших настроек**.

Причина, по которой вы должны использовать настройки, заключается в том, что это сделает ваш код более
организованным и облегчит его поддержку.

!!! Check
    Когда вы передаете параметры при создании объекта Ravyn, а не через параметры, при доступе к
    значениям через `request.app.settings` эти значения **не будут находиться в настройках**,
    так как они были переданы через создание приложения, а не через объект настроек.
    Доступ к этим значениям можно получить, например, непосредственно через `request.app.app_name`.
