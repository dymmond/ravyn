# How to Handle File Uploads

This guide demonstrates how to accept and process file uploads in your Ravyn application.

## Problem Statement

Web applications often need to receive files from users, such as profile pictures, documents, or CSV files. Handling these multi-part form data requests requires specific parsing and a way to access the file content and metadata safely.

## Solution

Ravyn uses the `UploadFile` class to represent uploaded files. You can use the `File` parameter from `ravyn.params` to define file upload fields in your handlers.

### 1. Simple file upload

Define a handler that accepts a single file.

```python
from ravyn import Ravyn, post, File, UploadFile

@post("/upload")
async def upload_file(data: UploadFile = File()) -> dict:
    # Access file metadata
    filename = data.filename
    content_type = data.content_type

    # Read file content
    content = await data.read()

    return {
        "filename": filename,
        "content_type": content_type,
        "size": len(content)
    }

app = Ravyn(routes=[upload_file])
```

### 2. Uploading multiple files

You can accept a list of files by typing the parameter as `list[UploadFile]`.

```python
from ravyn import Ravyn, post, File, UploadFile

@post("/upload-multiple")
async def upload_multiple(files: list[UploadFile] = File()) -> dict:
    uploaded_files = []
    for file in files:
        uploaded_files.append({
            "filename": file.filename,
            "size": len(await file.read())
        })

    return {"uploaded": uploaded_files}

app = Ravyn(routes=[upload_multiple])
```

### 3. Saving an uploaded file

Use standard Python file operations to save the uploaded content to the filesystem.

```python
import aiofiles
from ravyn import Ravyn, post, File, UploadFile

@post("/save-avatar")
async def save_avatar(avatar: UploadFile = File()) -> dict:
    destination = f"uploads/{avatar.filename}"

    async with aiofiles.open(destination, "wb") as f:
        content = await avatar.read()
        await f.write(content)

    return {"message": f"Avatar saved to {destination}"}

app = Ravyn(routes=[save_avatar])
```

## Explanation

- **`File()`**: This is a parameter marker that tells Ravyn to look for the value in the multi-part form data of the request.
- **`UploadFile`**: This object provides an interface to the uploaded file without loading the entire file into memory immediately. It's useful for large files.
- **`await file.read()`**: Reads the entire content of the file. For very large files, you might want to use a loop with `await file.read(chunk_size)`.
- **`await file.seek(0)`**: Moves the file pointer back to the beginning. Useful if you need to read the file multiple times.

## Common Pitfalls

- **Memory usage**: Reading a very large file with `await file.read()` loads the whole content into RAM. For large files, stream the content in chunks.
- **Async file I/O**: When saving files, use an async library like `aiofiles` to avoid blocking the main event loop.
- **File pointer**: After reading a file, the pointer is at the end. If you need to read it again (e.g., for validation then for saving), call `await file.seek(0)`.
- **Missing `multipart/form-data`**: Ensure your client sends the request with the correct `Content-Type`. Ravyn's `File()` parameter handles this automatically on the server side, but the client must provide it.

## Related pages

- [Upload Files Reference](../extras/upload-files.md)
- [Requests](../requests.md)
- [Responses](../responses.md)
