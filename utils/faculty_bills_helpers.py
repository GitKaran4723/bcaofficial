"""Helper functions for faculty bills/teaching records processing."""

import logging
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any, Tuple
import pandas as pd

logger = logging.getLogger(__name__)

# Exact combined header name required in the UI and DOCX
COMBINED_HEADER = "Particulars / chapter / lectures (as per Time Table) I / II / III / IV / V / VI Sem"


def find_col_by_variants(cols: List[str], *variants) -> Optional[str]:
    """Find a column name in cols matching any variant (case-insensitive).
    
    Args:
        cols: List of column names
        variants: Possible column name variants to search for
        
    Returns:
        Matching column name or None
    """
    lower_map = {c.lower(): c for c in cols}
    for v in variants:
        if v is None:
            continue
        key = str(v).lower()
        if key in lower_map:
            return lower_map[key]
    return None


def parse_date_val(v: Any) -> Optional[date]:
    """
    Tolerant parse into datetime.date, returning None if invalid.
    - Parses ISO timestamps like '2025-07-17T18:30:00.000Z' as UTC then converts to local TZ (Asia/Kolkata).
    - Falls back to flexible pandas parsing or explicit formats.
    - If an ISO-like string without timezone is provided, tries to parse it directly.
    
    Args:
        v: Value to parse (can be string, datetime, date, or pandas Timestamp)
        
    Returns:
        Parsed date or None if parsing fails
    """
    if pd.isna(v):
        return None

    # If it's already a date/datetime/timestamp, return its date (no timezone adjustment).
    if isinstance(v, (pd.Timestamp, datetime, date)):
        # pandas Timestamp may be tz-aware; convert to local if tz-aware.
        if isinstance(v, pd.Timestamp) and v.tz is not None:
            try:
                local = v.tz_convert("Asia/Kolkata")
                return local.date()
            except Exception:
                # fallback: use UTC-normalized date
                return v.tz_convert(None).date() if hasattr(v, 'tz_convert') else v.date()
        return v.date() if not isinstance(v, date) else v

    s = str(v).strip()
    if s == "":
        return None

    # 1) Try pandas flexible parser with utc=True (handles '...Z' correctly)
    dt = pd.to_datetime(s, utc=True, errors="coerce")
    if not pd.isna(dt):
        # dt is timezone-aware (UTC). Convert to local timezone to match Google Sheets display.
        try:
            local = dt.tz_convert("Asia/Kolkata")
            return local.date()
        except Exception:
            # if tz_convert fails for any reason, fall back to the UTC date
            return dt.date()

    # 2) Try explicit common formats (date-only or naive ISO)
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(s, fmt)
            # parsed is naive — treat as local date (no tz shift)
            return parsed.date()
        except Exception:
            pass

    # 3) As a last resort, if it looks like ISO 'YYYY-MM-DD...' take the date part
    if "T" in s:
        try:
            date_part = s.split("T", 1)[0]
            return datetime.strptime(date_part, "%Y-%m-%d").date()
        except Exception:
            pass

    return None


def contains_lab(*texts: Any) -> bool:
    """Return True if any text contains 'lab' (case-insensitive).
    
    Args:
        texts: Variable number of text values to check
        
    Returns:
        True if any text contains 'lab', False otherwise
    """
    for t in texts:
        if t is None:
            continue
        if "lab " in str(t).lower():
            return True
    return False


def build_months_structure(df: pd.DataFrame) -> Tuple[Dict[str, List[Dict]], List[str]]:
    """
    Build months structure from faculty bills dataframe (no SL assignment here).

    Args:
        df: DataFrame with faculty bills data
        
    Returns:
        Tuple of (months_dict, faculty_list)
        
    months_dict structure:
      { "August 2025": [ 
          { 
            "week_start": date, 
            "week_end": date, 
            "entries": [...], 
            "week_total_actual": float, 
            "week_total_claiming": float 
          }, 
          ... 
        ] 
      }
      
    Each entry contains:
      "Dairy No.", "Date_iso", "Date" (dd-mm-yyyy), COMBINED_HEADER, 
      "Actual hours", "Claiming hours", "Subject code", "Faculty"
    """
    # detect source column names (variants added to match your sheet)
    col_date = find_col_by_variants(df.columns, "Date", "date")
    col_diary = find_col_by_variants(df.columns, "Diary Number", "Diary No", "Diary", "DiaryNumber")
    col_class = find_col_by_variants(df.columns, "Select Class and Section", "Select Class", "Class")
    col_subject_raw = find_col_by_variants(df.columns, "Choose Subject", "Subject")
    col_topics = find_col_by_variants(df.columns, "Topics Covered", "Topics", "Particulars")
    col_duration = find_col_by_variants(df.columns, "Duration", "Actual hours")
    col_claiming = find_col_by_variants(df.columns, "CLAMING HOURS", "Claiming Hours", "Claiming")
    col_faculty_raw = find_col_by_variants(df.columns, "Faculty Name - Email", "Faculty Name", "Faculty")

    if col_date is None:
        return {}, []  # return empty months and empty faculty list

    # Ensure duration column exists
    if col_duration is None:
        df["Duration"] = 0.0
        col_duration = "Duration"

    # coerce Duration to numeric
    df[col_duration] = pd.to_numeric(df[col_duration], errors="coerce").fillna(0.0)

    # parse dates and keep only rows with parsed date
    df["_parsed_date"] = df[col_date].apply(parse_date_val)
    df = df[~df["_parsed_date"].isna()].copy()
    if df.empty:
        return {}, []

    months = {}
    faculty_set = set()

    for _, row in df.iterrows():
        d = row["_parsed_date"]
        month_label = d.strftime("%B %Y")

        wd = d.weekday()
        week_start = d - timedelta(days=wd)
        week_end = week_start + timedelta(days=5)

        months.setdefault(month_label, [])
        weeks = months[month_label]

        week_obj = next((w for w in weeks if w["week_start"] == week_start), None)
        if not week_obj:
            week_obj = {
                "week_start": week_start,
                "week_end": week_end,
                "entries": [],
                "week_total_actual": 0.0,
                "week_total_claiming": 0.0
            }
            weeks.append(week_obj)

        # particulars
        particulars = ""
        if col_topics and col_topics in row and pd.notna(row[col_topics]):
            particulars = str(row[col_topics]).strip()

        # subject raw (might contain "Subject - CODE")
        subj_raw = ""
        subj = ""
        subj_code = ""
        if col_subject_raw and col_subject_raw in row and pd.notna(row[col_subject_raw]):
            subj_raw = str(row[col_subject_raw]).strip()
            if " - " in subj_raw:
                parts = subj_raw.rsplit(" - ", 1)
                subj = parts[0].strip()
                subj_code = parts[1].strip()
            else:
                subj = subj_raw
                subj_code = ""

        # class
        class_val = ""
        if col_class and col_class in row and pd.notna(row[col_class]):
            class_val = str(row[col_class]).strip()

        # combined field: combine particulars, subject, class into one string (non-empty parts separated by " - ")
        combined_parts = []
        if class_val:
            combined_parts.append(class_val)
        if subj:
            combined_parts.append(subj)
        if particulars:
            combined_parts.append(particulars)
        combined_value = " - ".join(combined_parts) if combined_parts else ""

        # faculty extract (from faculty raw column, get name part before ' - ')
        faculty_name = ""
        if col_faculty_raw and col_faculty_raw in row and pd.notna(row[col_faculty_raw]):
            fac_raw = str(row[col_faculty_raw]).strip()
            if " - " in fac_raw:
                faculty_name = fac_raw.split(" - ", 1)[0].strip()
            else:
                faculty_name = fac_raw
            if faculty_name:
                faculty_set.add(faculty_name)

        # detect lab
        is_lab = contains_lab(particulars, subj_raw, class_val)

        # actual hours
        actual_hours = float(row[col_duration]) if col_duration in row and pd.notna(row[col_duration]) else 0.0

        actual_hours = actual_hours % 12  # cap at 12 hours max per entry

        # claiming precedence
        claiming_raw = row[col_claiming] if col_claiming and col_claiming in row else None
        claiming_val = None
        try:
            if claiming_raw is not None and pd.notna(claiming_raw):
                claiming_val = float(claiming_raw)
        except Exception:
            claiming_val = None

        if is_lab:
            claiming_hours = round(actual_hours * (3.0 / 4.0), 2)
        else:
            claiming_hours = round(claiming_val if claiming_val is not None else actual_hours, 2)

        diary_no = row[col_diary] if col_diary and col_diary in row and pd.notna(row[col_diary]) else ""

        # store entry (no SL No assigned yet)
        entry = {
            "SL No": None,
            "Dairy No.": diary_no,
            "Date_iso": d.strftime("%Y-%m-%d"),
            "Date": d.strftime("%d-%m-%Y"),  # dd-mm-yyyy display
            COMBINED_HEADER: combined_value,
            "Actual hours": round(actual_hours, 2),
            "Claiming hours": claiming_hours,
            "Subject code": subj_code,
            "Faculty": faculty_name,
            "_is_lab": is_lab
        }

        week_obj["entries"].append(entry)
        week_obj["week_total_actual"] += entry["Actual hours"]
        week_obj["week_total_claiming"] += entry["Claiming hours"]

    # finalize months: sort weeks and entries, round totals
    for mlabel, weeks in months.items():
        weeks.sort(key=lambda w: w["week_start"])
        for w in weeks:
            w["entries"].sort(key=lambda e: (e["Date_iso"], str(e.get("Dairy No.", ""))))
            w["week_total_actual"] = round(w["week_total_actual"], 2)
            w["week_total_claiming"] = round(w["week_total_claiming"], 2)
            for e in w["entries"]:
                e["Actual hours"] = round(e["Actual hours"], 2)
                e["Claiming hours"] = round(e["Claiming hours"], 2)

    faculty_list = sorted(faculty_set)
    return months, faculty_list


def filter_and_assign_sl(months: Dict[str, List[Dict]], selected_month: str, 
                          selected_faculty: str) -> List[Dict]:
    """
    Filter weeks by month and faculty, then assign sequential SL numbers.
    
    Args:
        months: Months structure from build_months_structure
        selected_month: Month to filter (e.g., "August 2025")
        selected_faculty: Faculty name to filter (or "All" for all faculty)
        
    Returns:
        List of week dictionaries with filtered entries and assigned SL numbers
    """
    if selected_month not in months:
        return []

    # compute month boundaries
    first_day = datetime.strptime(selected_month, "%B %Y").date().replace(day=1)
    next_month = (first_day.replace(day=28) + timedelta(days=4)).replace(day=1)
    last_day = next_month - timedelta(days=1)

    rendered_weeks = []
    for w in months[selected_month]:
        # filter entries inside this month
        entries_in_month = []
        for e in w["entries"]:
            e_date = datetime.strptime(e["Date_iso"], "%Y-%m-%d").date()
            if not (first_day <= e_date <= last_day):
                continue
            # filter by faculty if set
            if selected_faculty != "All":
                if e.get("Faculty", "") != selected_faculty:
                    continue
            entries_in_month.append(e)

        if not entries_in_month:
            continue

        display_start = max(w["week_start"], first_day)
        display_end = min(w["week_end"], last_day)

        rendered_weeks.append({
            "week_start": w["week_start"],
            "week_end": w["week_end"],
            "display_start": display_start,
            "display_end": display_end,
            "entries": entries_in_month,
            "week_total_actual": round(sum(e["Actual hours"] for e in entries_in_month), 2),
            "week_total_claiming": round(sum(e["Claiming hours"] for e in entries_in_month), 2)
        })

    # sort weeks and assign week numbers
    rendered_weeks.sort(key=lambda x: x["display_start"])
    for idx, rw in enumerate(rendered_weeks, start=1):
        rw["week_number"] = idx

    # Now assign sequential SL No across the entire filtered month
    flat = []
    for rw in rendered_weeks:
        for e in rw["entries"]:
            flat.append(e)
    flat.sort(key=lambda e: (e["Date_iso"], str(e.get("Dairy No.", ""))))
    for idx, e in enumerate(flat, start=1):
        e["SL No"] = idx

    return rendered_weeks
