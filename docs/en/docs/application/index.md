# Application

Learn how to configure and use the Ravyn application class effectively.

## Conceptual map

```text
Ravyn()
  -> routes (what can be called)
  -> middleware/permissions (how requests are filtered)
  -> settings/config objects (how behavior is configured)
  -> lifespan hooks (how resources start/stop)
```

If you are new to Ravyn internals, read the pages in this section in order.

## In This Section

- [Applications](./applications.md) - The Ravyn class and configuration
- [Settings](./settings.md) - Application settings and configuration
- [Levels](./levels.md) - Understanding the application hierarchy

## Quick Links

### Getting Started

- [Create your first app](./applications.md#quick-start)
- [Configure settings](./settings.md#quick-start)
- [Understand levels](./levels.md#quick-overview)

### Common Tasks

- [Add routes](./applications.md#with-routes)
- [Configure CORS](./applications.md#complete-example)
- [Manage application state](./applications.md#application-state)
- [Use environment variables](./settings.md#environment-variables)

### Advanced Topics

- [Lifecycle management](./applications.md#lifecycle-management)
- [Multiple environments](./settings.md#multiple-environments)
- [ChildRavyn applications](./levels.md#using-childravyn)

## Recommended order

1. [Applications](./applications.md)
2. [Settings](./settings.md)
3. [Levels](./levels.md)

## Related sections

- [Configurations](../configurations/index.md)
- [Routing](../routing/index.md)
- [Lifespan Events](../lifespan-events.md)
