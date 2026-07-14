# Changelog — V4.4.65

## Duplicate notification investigation

The red duplicate notification was still present in V4.4.64. It appeared to
have disappeared because the duplicate-check block silently converted every
Archive-query or PDF-metadata error into an empty duplicate list:

```python
except Exception:
    duplicate_references = []
```

The check also used a 180-second cached Archive list, which could temporarily
miss a report saved by another user or earlier in the same session.

## Fixes

- Duplicate checking now loads the current PDF Archive records when PDFs are uploaded.
- Exceptions are no longer silently hidden.
- A visible warning appears when the duplicate check cannot be completed.
- Duplicate matching now uses:
  1. exact original PDF SHA256
  2. normalized IAD reference
  3. exact filename fallback
- Metadata errors are isolated per uploaded PDF.
- One unreadable PDF no longer disables duplicate checking for every file.
- The red notification now lists the archived reference/filename and match basis.
- Historical duplicate-list caches are invalidated after archive operations.

## Unchanged

- Generate Extraction parser
- isolated extraction worker
- PDF Tagging
- archive upload/storage implementation
- Dashboard and sidebar
- avatar and login features
- dependency pins and PyArrow stability fix from V4.4.64
