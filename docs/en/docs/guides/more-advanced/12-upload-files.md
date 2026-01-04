# Upload Files in Ravyn

Uploading files is a common functionality in web applications, and Ravyn makes this process simple using the `UploadFile` class. This guide will walk you through how to upload files, both single and multiple, and leverage Ravyn’s powerful features.

## 📂 Accessing `UploadFile`

To use the `UploadFile` class, you can import it as follows:

```python
from ravyn.core.datastructures import UploadFile
```

Alternatively:

```python
from ravyn import UploadFile
```

This class provides an interface for handling file uploads in Ravyn.

---

## 🌐 Supported Content Types for File Uploads

Ravyn supports different content types for file uploads, which can be specified via the `media_type` parameter in the `Body` decorator.

Available content types are:

- `application/x-www-form-urlencoded`
- `multipart/form-data`
- `application/json`

You can access the `EncodingType` enum to use these content types:

```python
from ravyn.utils.enums import EncodingType
```

From Ravyn version `0.8+`, you can handle file uploads using `Body` with `media_type`, or use `File` and `Form` directly for form and file uploads.

---

## 🗂 Single File Upload

To upload a single file, use the `UploadFile` class. Here's an example of how to handle a single file upload:

### Example: Single File Upload

```python
from ravyn import Ravyn, Gateway, JSONResponse, UploadFile, Body, post
from ravyn.utils.enums import EncodingType

@post("/upload")
async def upload_file(data: UploadFile = Body(media_type=EncodingType.MULTI_PART)) -> JSONResponse:
    """
    Uploads a single file to the server.
    """
    content = await data.read()
    filename = data.filename
    return JSONResponse({"filename": filename, "content": content.decode()})

app = Ravyn(routes=[Gateway(handler=upload_file, name="upload-file")])
```

### Explanation:

- The `data` parameter is typed as `UploadFile` to accept the file.
- The `media_type=EncodingType.MULTI_PART` ensures the body is processed as multipart form data.
- The file’s content is read asynchronously, and the filename and content are returned.

---

## 🗃 Multiple File Uploads

Ravyn allows you to upload multiple files in one request by accepting a list of `UploadFile` objects.

### Example: Multiple File Upload

```python
from typing import List
from ravyn import Ravyn, Gateway, JSONResponse, UploadFile, File, post

@post("/upload")
async def upload_files(data: List[UploadFile] = File()) -> JSONResponse:
    """
    Uploads multiple files to the server.
    """
    file_details = []
    for file in data:
        content = await file.read()
        file_details.append({"filename": file.filename, "content": content.decode()})
    return JSONResponse({"files": file_details})

app = Ravyn(routes=[Gateway(handler=upload_files, name="upload-files")])
```

### Explanation:

- The `data` parameter is typed as `List[UploadFile]`, allowing multiple files.
- The `File()` decorator simplifies handling multiple file uploads by automatically setting the content type to multipart form data.
- Each file’s content is read asynchronously, and the details are returned as a JSON array.

---

## 📝 Using the `File` Parameter

You can also use `File` directly, which inherits from `Body`, to handle file uploads. This makes your code cleaner, as you don't need to specify the `media_type=EncodingType.MULTI_PART`. it’s set automatically.

### Example: Single File Upload with `File`

```python
from ravyn import Ravyn, Gateway, JSONResponse, UploadFile, File, post

@post("/upload")
async def upload_file(data: UploadFile = File()) -> JSONResponse:
    """
    Uploads a single file to the server.
    """
    content = await data.read()
    filename = data.filename
    return JSONResponse({"filename": filename, "content": content.decode()})

app = Ravyn(routes=[Gateway(handler=upload_file, name="upload-file")])
```

### Example: Multiple File Upload with `File`

```python
from typing import List
from ravyn import Ravyn, Gateway, JSONResponse, UploadFile, File, post

@post("/upload")
async def upload_files(data: List[UploadFile] = File()) -> JSONResponse:
    """
    Uploads multiple files to the server.
    """
    file_details = []
    for file in data:
        content = await file.read()
        file_details.append({"filename": file.filename, "content": content.decode()})
    return JSONResponse({"files": file_details})

app = Ravyn(routes=[Gateway(handler=upload_files, name="upload-files")])
```

### Explanation:

- The `File()` decorator automatically handles multipart form data and simplifies file handling.
- Both single and multiple file uploads can be managed easily using `File()`.

---

## File Upload Limits

You can limit the number of files uploaded or the file size using `max_length` and other parameters.

### Example: Limit Uploads to Three Files

```python
from ravyn import Ravyn, Gateway, JSONResponse, UploadFile, File, post

@post("/upload")
async def upload_files(data: List[UploadFile] = File(..., max_length=3)) -> JSONResponse:
    """
    Uploads a maximum of three files to the server.
    """
    file_details = []
    for file in data:
        content = await file.read()
        file_details.append({"filename": file.filename, "content": content.decode()})
    return JSONResponse({"files": file_details})

app = Ravyn(routes=[Gateway(handler=upload_files, name="upload-files")])
```

In this case, attempting to upload more than three files will raise a `ValidationErrorException`.

---

## 🧳 File Handling from Parameters

You can also use the `File` parameter from the `params` module. This differs from `UploadFile`, which is used in the data structure.

```python
from ravyn.core.datastructures import File  # data structure
```

or

```python
from ravyn.params import File  # parameter
```

This distinction allows you to handle files with different configurations based on your needs.

---

## 📄 API Reference

For more detailed information on `UploadFile` and its methods, check the [Ravyn API Reference](../../references/uploadfile.md).

---

## 📌 Conclusion

Ravyn makes handling file uploads seamless and flexible, whether you need to upload single or multiple files,
apply limits, or use different encoders. By using the `UploadFile` and `File` parameters, you can efficiently
manage file uploads in your applications while leveraging Ravyn’s validation and features.
