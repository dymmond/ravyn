# Sending Files

The `send_file` utility in Ravyn makes it easy to return files from your endpoints,
similar to Flask’s `send_file`.

It can return files from the filesystem or from in-memory file-like objects, and supports options
such as forcing downloads, setting custom filenames, and controlling cache headers.

---

## When to Use `send_file`

Use `send_file` when your API or application needs to:

* Serve static files on demand (e.g., reports, exports, PDFs).
* Allow users to download dynamically generated files.
* Stream file-like objects such as `BytesIO`.

For static assets (images, CSS, JS) you should use proper static file serving,
but for **API endpoints that return a file**, `send_file` is the right tool.

---

## Basic Example

Returning a text file directly:

```python
from ravyn import Ravyn, Gateway, get
from ravyn.contrib.responses.files import send_file

@get()
async def get_report():
    return send_file("reports/summary.txt")

app = Ravyn(routes=[
    Gaetway("/report", handler=get_report)
])
```

Request:

```bash
curl http://localhost:8000/report
```

Response body will contain the content of `summary.txt`.

---

## Force Download (Attachment)

To force the browser to download the file instead of displaying it inline:

```python
@get()
async def download_invoice():
    return send_file("invoices/invoice.pdf", as_attachment=True)
```

This adds a `Content-Disposition: attachment` header, prompting the browser to download the file.

---

## Custom Filename

You can customize the filename shown to the user:

```python
@get()
async def export_csv():
    return send_file(
        "exports/data.csv",
        as_attachment=True,
        attachment_filename="report.csv"
    )
```

The downloaded file will appear as `report.csv` instead of `data.csv`.

---

## Sending a File-Like Object

You can also send an in-memory file, such as a `BytesIO`:

```python
import io

@get()
async def stream_file():
    file_like = io.BytesIO(b"some dynamic content")
    return send_file(file_like, mimetype="text/plain")
```

This is useful for dynamically generated content that you don’t want to store on disk.

---

## Controlling Cache

Set `Cache-Control` headers with `max_age`:

```python
@get()
async def cached_pdf():
    return send_file("docs/manual.pdf", max_age=3600)
```

Response will include:

```
Cache-Control: public, max-age=3600
```

---

## API Reference

```python
send_file(
    filename_or_fp: Union[str, Path, IO[bytes]],
    mimetype: Optional[str] = None,
    as_attachment: bool = False,
    attachment_filename: Optional[str] = None,
    max_age: Optional[int] = None,
)
```

### Parameters

* **`filename_or_fp`** – Path to the file on disk (`str` or `Path`) or a file-like object (`IO[bytes]`).
* **`mimetype`** – Optional MIME type (e.g., `"application/pdf"`). If not provided, Ravyn attempts to infer.
* **`as_attachment`** – If `True`, adds `Content-Disposition: attachment` to force download.
* **`attachment_filename`** – Override the filename presented to the user.
* **`max_age`** – Sets `Cache-Control: public, max-age=<seconds>` for caching.

With `send_file`, Ravyn makes file downloads and streaming as simple and flexible as Flask, but fully async-native.
