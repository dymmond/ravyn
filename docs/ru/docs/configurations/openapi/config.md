# OpenAPIConfig

`OpenAPIConfig` — это простая конфигурация с основными полями для автогенерируемой документации в Ravyn.

До версии 2 для документации требовались две отдельные настройки, но теперь они объединены в одну,
упрощенную конфигурацию.

!!! Tip
    Больше информации о
    <a href="https://swagger.io/" target='_blank'>OpenAPI</a>.

Вы можете создать `OpenAPIConfig` и заполнить все необходимые переменные или просто
переопределить атрибуты настроек.
Выбор за вами.

!!! Warning
    При передаче атрибутов OpenAPI через создание экземпляра, например, `Ravyn(docs_url='/docs/swagger',...)`,
    эти параметры всегда будут использоваться вместо настроек или пользовательской конфигурации.

## OpenAPIConfig и приложение

`OpenAPIConfig` содержит набор простых полей, необходимых для отображения документации,
которые можно легко переопределить.

На данный момент, по умолчанию, URL для документации следующие:

* **Swagger** - `/docs/swagger`.
* **Redoc** - `/docs/redoc`.
* **Stoplight** - `/docs/elements`.
* **Rapidoc** - `/docs/rapidoc`.

## Параметры

Все параметры и значения по умолчанию доступны в [справочнике OpenAPIConfig](../../references/configurations/openapi.md).

### Как использовать или создать OpenAPIConfig

На самом деле это очень просто.

```python hl_lines="4 12"
{!> ../../../docs_src/configurations/openapi/example1.py !}
```

Это создаст ваш собственный `OpenAPIConfig` и передаст его приложению Ravyn, но как насчет
изменения текущего пути по умолчанию `/docs`?

Давайте рассмотрим пример.

```python
{!> ../../../docs_src/configurations/openapi/controller.py !}
```

Теперь URL для доступа к `swagger`, `redoc` и `stoplight` будет следующим:

* **Swagger** - `/another-url/swagger`.
* **Redoc** - `/another-url/redoc`.
* **Stoplight** - `/another-url/stoplight`.

## OpenAPIConfig и настройки приложения

В соответствии со стандартом конфигурации Ravyn, также можно включить конфигурацию OpenAPI через настройки.

```python
{!> ../../../docs_src/configurations/openapi/settings.py !}
```

Запуск сервера с пользовательскими настройками.

=== "MacOS & Linux"

    ```shell
    RAVYN_SETTINGS_MODULE=AppSettings palfrey src:app --reload

    INFO:     Palfrey running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

=== "Windows"

    ```shell
    $env:RAVYN_SETTINGS_MODULE="AppSettings"; palfrey src:app --reload

    INFO:     Palfrey running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [28720]
    INFO:     Started server process [28722]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```
