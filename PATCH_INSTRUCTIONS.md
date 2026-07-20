# IARS V4.4.68 Patch Instructions

## Purpose

This patch corrects the Accounts Confirmation exclusion rule.

The report title must **not** suppress the entire report. The exclusion applies only when:

- the audit type is **Operations Audit**, and
- the individual **issue title/table title** is exactly **Accounts Confirmation**.

## Replace these files

Replace the following files in the current repository using the files in this patch:

1. `requirements.txt`
2. `iars_pdf_editor.py`
3. `iars_parser.py`

The first two files retain the PDF Tagging Components V2 fix from V4.4.67. The updated `iars_parser.py` removes only the report-title-level suppression.

After replacing the files, reboot the Streamlit app and perform a hard refresh (`Ctrl + F5`).
