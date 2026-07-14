from __future__ import annotations

from io import BytesIO
from pathlib import Path
import pickle
import sys
import traceback

from iars_parser import build_records


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: iars_extract_worker.py INPUT.pkl OUTPUT.pkl", file=sys.stderr)
        return 2

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    try:
        with input_path.open("rb") as handle:
            payload = pickle.load(handle)

        pdf_file = BytesIO(bytes(payload.get("pdf_bytes") or b""))
        result_df, header, items = build_records(
            pdf_file,
            payload.get("master_df"),
            auditors_df=payload.get("auditors_df"),
            master_sheets=payload.get("master_sheets"),
        )

        response = {
            "ok": True,
            "result_df": result_df,
            "header": header,
            "items": items,
        }
        with output_path.open("wb") as handle:
            pickle.dump(response, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return 0
    except BaseException as exc:
        response = {
            "ok": False,
            "error": str(exc) or exc.__class__.__name__,
            "traceback": traceback.format_exc(limit=20),
        }
        try:
            with output_path.open("wb") as handle:
                pickle.dump(response, handle, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception:
            pass
        print(response["traceback"], file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
