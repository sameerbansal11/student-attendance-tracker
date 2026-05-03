#!/usr/bin/env python3
"""
student-attendance-tracker — Complete CLI App
Author: Sameer Bansal | RA2311032010061
SRM Institute of Science and Technology | B.Tech CSE IoT 2023-2027
"""

import os
import csv
import json
import datetime
from collections import defaultdict

# ── Colors ────────────────────────────────────────────────
R = "\033[0m"
BOLD = "\033[1m"
G = "\033[92m"
RED = "\033[91m"
Y = "\033[93m"
C = "\033[96m"
B = "\033[94m"
DIM = "\033[2m"
M = "\033[95m"

DATA_FILE = "attendance_data.json"
EXPORT_CSV = "attendance_report.csv"


# ── Persistence ───────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"students": {}, "subjects": [], "records": []}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Helpers ───────────────────────────────────────────────
def clear():
    os.system("cls" if os.name == "nt" else "clear")


def today():
    return datetime.date.today().isoformat()


def banner():
    print(f"{BOLD}{'='*56}")
    print("       🎓 STUDENT ATTENDANCE TRACKER")
    print("       Sameer Bansal | RA2311032010061 | SRMIST")
    print(f"{'='*56}{R}")


def pause():
    input(f"\n  {DIM}Press ENTER to continue...{R}")


def confirm(msg):
    return input(f"  {Y}⚠  {msg} [y/n]: {R}").strip().lower() == "y"


# ── Student Management ────────────────────────────────────
def add_student(data):
    print(f"\n  {BOLD}ADD STUDENT{R}")
    roll = input("  Roll Number : ").strip().upper()
    if not roll:
        print(f"  {RED}Roll number cannot be empty.{R}")
        return
    if roll in data["students"]:
        print(f"  {Y}Student {roll} already exists.{R}")
        return
    name = input("  Full Name   : ").strip()
    branch = input("  Branch      : ").strip()
    if not name:
        print(f"  {RED}Name cannot be empty.{R}")
        return
    data["students"][roll] = {"name": name, "branch": branch}
    save_data(data)
    print(f"  {G}✅ Added: {name} ({roll}){R}")


def remove_student(data):
    print(f"\n  {BOLD}REMOVE STUDENT{R}")
    roll = input("  Roll Number : ").strip().upper()
    if roll not in data["students"]:
        print(f"  {RED}Student not found.{R}")
        return
    name = data["students"][roll]["name"]
    if confirm(f"Remove {name} ({roll}) and ALL their records?"):
        del data["students"][roll]
        data["records"] = [r for r in data["records"] if r["roll"] != roll]
        save_data(data)
        print(f"  {G}✅ Removed {name}.{R}")


def list_students(data):
    if not data["students"]:
        print(f"  {Y}No students added yet.{R}")
        return
    print(f"\n  {BOLD}{'Roll':<12} {'Name':<24} {'Branch'}{R}")
    print(f"  {'─'*50}")
    for roll, info in sorted(data["students"].items()):
        print(f"  {C}{roll:<12}{R} {info['name']:<24} {DIM}{info['branch']}{R}")


# ── Subject Management ────────────────────────────────────
def add_subject(data):
    sub = input("\n  Subject Name: ").strip().upper()
    if not sub:
        print(f"  {RED}Subject cannot be empty.{R}")
        return
    if sub in data["subjects"]:
        print(f"  {Y}Subject already exists.{R}")
        return
    data["subjects"].append(sub)
    save_data(data)
    print(f"  {G}✅ Added subject: {sub}{R}")


def list_subjects(data):
    if not data["subjects"]:
        print(f"  {Y}No subjects added yet.{R}")
        return
    print(f"\n  {BOLD}Subjects:{R}")
    for i, s in enumerate(data["subjects"], 1):
        print(f"  [{i}] {C}{s}{R}")


# ── Mark Attendance ───────────────────────────────────────
def mark_attendance(data):
    if not data["students"]:
        print(f"  {Y}Add students first.{R}")
        return
    if not data["subjects"]:
        print(f"  {Y}Add subjects first.{R}")
        return

    print(f"\n  {BOLD}MARK ATTENDANCE{R}")
    list_subjects(data)
    sub_input = input("\n  Subject number or name: ").strip()
    try:
        idx = int(sub_input) - 1
        subject = data["subjects"][idx]
    except (ValueError, IndexError):
        subject = sub_input.upper()
        if subject not in data["subjects"]:
            print(f"  {RED}Subject not found.{R}")
            return

    date_input = input(f"  Date [YYYY-MM-DD, blank=today ({today()})]: ").strip()
    date = date_input if date_input else today()
    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        print(f"  {RED}Invalid date format.{R}")
        return

    already = {
        r["roll"]
        for r in data["records"]
        if r["subject"] == subject and r["date"] == date
    }
    if already:
        print(
            f"\n  {Y}Attendance for {subject} on {date} already recorded for "
            f"{len(already)} student(s).{R}"
        )
        if not confirm("Overwrite?"):
            return
        data["records"] = [
            r
            for r in data["records"]
            if not (r["subject"] == subject and r["date"] == date)
        ]

    print(f"\n  {BOLD}Marking attendance — {subject} | {date}{R}")
    print(f"  {DIM}P=Present  A=Absent  L=Leave  (default P){R}\n")

    count = {"P": 0, "A": 0, "L": 0}
    for roll, info in sorted(data["students"].items()):
        status_in = (
            input(f"  {C}{roll}{R} {info['name']:<22} [P/A/L]: ").strip().upper()
        )
        status = status_in if status_in in ("P", "A", "L") else "P"
        data["records"].append(
            {
                "roll": roll,
                "name": info["name"],
                "subject": subject,
                "date": date,
                "status": status,
            }
        )
        color = G if status == "P" else RED if status == "A" else Y
        print(f"         → {color}{status}{R}", end="\r")
        count[status] += 1

    save_data(data)
    total = sum(count.values())
    print(
        f"\n  {G}✅ Attendance saved!{R}  "
        f"{G}Present:{count['P']}{R}  {RED}Absent:{count['A']}{R}  "
        f"{Y}Leave:{count['L']}{R}  Total:{total}"
    )


# ── Reports ───────────────────────────────────────────────
def _student_stats(data, roll):
    records = [r for r in data["records"] if r["roll"] == roll]
    by_sub = defaultdict(lambda: {"P": 0, "A": 0, "L": 0, "total": 0})
    for r in records:
        by_sub[r["subject"]][r["status"]] += 1
        by_sub[r["subject"]]["total"] += 1
    return by_sub


def report_student(data):
    if not data["students"]:
        print(f"  {Y}No students.{R}")
        return
    list_students(data)
    roll = input("\n  Enter Roll Number: ").strip().upper()
    if roll not in data["students"]:
        print(f"  {RED}Not found.{R}")
        return
    info = data["students"][roll]
    stats = _student_stats(data, roll)
    print(f"\n  {BOLD}📋 Report: {info['name']} ({roll}) — {info['branch']}{R}")
    print(f"  {'─'*54}")
    if not stats:
        print(f"  {Y}No attendance records found.{R}")
        return
    print(
        f"  {BOLD}{'Subject':<16} {'Total':>6} {'Present':>8} {'Absent':>7} "
        f"{'Leave':>6} {'%':>6}{R}"
    )
    print(f"  {'─'*54}")
    overall_p = overall_t = 0
    for sub, s in sorted(stats.items()):
        pct = (s["P"] / s["total"] * 100) if s["total"] else 0
        color = G if pct >= 75 else Y if pct >= 60 else RED
        print(
            f"  {sub:<16} {s['total']:>6} {G}{s['P']:>8}{R} {RED}{s['A']:>7}{R} "
            f"{Y}{s['L']:>6}{R} {color}{pct:>5.1f}%{R}"
        )
        overall_p += s["P"]
        overall_t += s["total"]
    pct_overall = (overall_p / overall_t * 100) if overall_t else 0
    color = G if pct_overall >= 75 else Y if pct_overall >= 60 else RED
    print(f"  {'─'*54}")
    print(
        f"  {'OVERALL':<16} {overall_t:>6} {G}{overall_p:>8}{R} "
        f"  {DIM}—{R}     {DIM}—{R}  {color}{pct_overall:>5.1f}%{R}"
    )
    low = [
        s
        for s, st in stats.items()
        if st["total"] > 0 and (st["P"] / st["total"] * 100) < 75
    ]
    if low:
        print(f"\n  {RED}⚠  Low attendance (<75%): {', '.join(low)}{R}")


def report_subject(data):
    if not data["subjects"]:
        print(f"  {Y}No subjects.{R}")
        return
    list_subjects(data)
    sub_input = input("\n  Subject number or name: ").strip()
    try:
        subject = data["subjects"][int(sub_input) - 1]
    except (ValueError, IndexError):
        subject = sub_input.upper()
        if subject not in data["subjects"]:
            print(f"  {RED}Not found.{R}")
            return
    records = [r for r in data["records"] if r["subject"] == subject]
    if not records:
        print(f"  {Y}No records for {subject}.{R}")
        return
    by_student = defaultdict(lambda: {"P": 0, "A": 0, "L": 0, "total": 0, "name": ""})
    for r in records:
        by_student[r["roll"]][r["status"]] += 1
        by_student[r["roll"]]["total"] += 1
        by_student[r["roll"]]["name"] = r["name"]
    print(f"\n  {BOLD}📋 Subject Report: {subject}{R}")
    print(f"  {'─'*56}")
    print(f"  {BOLD}{'Roll':<10} {'Name':<22} {'P':>4} {'A':>4} {'L':>4} {'%':>7}{R}")
    print(f"  {'─'*56}")
    low_count = 0
    for roll, s in sorted(by_student.items()):
        pct = (s["P"] / s["total"] * 100) if s["total"] else 0
        color = G if pct >= 75 else Y if pct >= 60 else RED
        if pct < 75:
            low_count += 1
        print(
            f"  {C}{roll:<10}{R} {s['name']:<22} {G}{s['P']:>4}{R} "
            f"{RED}{s['A']:>4}{R} {Y}{s['L']:>4}{R} {color}{pct:>6.1f}%{R}"
        )
    dates = sorted({r["date"] for r in records})
    print(f"\n  Total classes held : {len(dates)}")
    print(f"  Students below 75% : {RED}{low_count}{R}")


def report_date(data):
    date_input = input(f"\n  Date [YYYY-MM-DD, blank=today ({today()})]: ").strip()
    date = date_input if date_input else today()
    records = [r for r in data["records"] if r["date"] == date]
    if not records:
        print(f"  {Y}No records for {date}.{R}")
        return
    subjects = sorted({r["subject"] for r in records})
    print(f"\n  {BOLD}📋 Attendance on {date}{R}")
    for sub in subjects:
        sub_recs = [r for r in records if r["subject"] == sub]
        p = sum(1 for r in sub_recs if r["status"] == "P")
        a = sum(1 for r in sub_recs if r["status"] == "A")
        l = sum(1 for r in sub_recs if r["status"] == "L")
        print(
            f"\n  {BOLD}{sub}{R}  —  {G}Present:{p}{R}  {RED}Absent:{a}{R}  {Y}Leave:{l}{R}"
        )
        print(f"  {'─'*46}")
        for r in sorted(sub_recs, key=lambda x: x["roll"]):
            color = G if r["status"] == "P" else RED if r["status"] == "A" else Y
            print(f"  {C}{r['roll']:<10}{R} {r['name']:<22} {color}{r['status']}{R}")


def export_csv(data):
    if not data["records"]:
        print(f"  {Y}No records to export.{R}")
        return
    with open(EXPORT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["date", "roll", "name", "subject", "status"]
        )
        writer.writeheader()
        for r in sorted(data["records"], key=lambda x: (x["date"], x["roll"])):
            writer.writerow(r)
    print(f"  {G}✅ Exported {len(data['records'])} records → {EXPORT_CSV}{R}")


def low_attendance_alert(data, threshold=75):
    print(f"\n  {BOLD}🚨 LOW ATTENDANCE ALERT (< {threshold}%){R}")
    print(f"  {'─'*52}")
    found = False
    for roll, info in sorted(data["students"].items()):
        stats = _student_stats(data, roll)
        for sub, s in stats.items():
            if s["total"] == 0:
                continue
            pct = s["P"] / s["total"] * 100
            if pct < threshold:
                print(
                    f"  {RED}{roll:<10}{R} {info['name']:<22} "
                    f"{Y}{sub:<14}{R} {RED}{pct:.1f}%{R}"
                )
                found = True
    if not found:
        print(f"  {G}✅ All students above {threshold}% attendance!{R}")


def summary_dashboard(data):
    total_s = len(data["students"])
    total_sub = len(data["subjects"])
    total_r = len(data["records"])
    dates = sorted({r["date"] for r in data["records"]})
    p_count = sum(1 for r in data["records"] if r["status"] == "P")
    overall_pct = (p_count / total_r * 100) if total_r else 0
    print(f"\n  {BOLD}📊 DASHBOARD SUMMARY{R}")
    print(f"  {'─'*40}")
    print(f"  Students      : {C}{total_s}{R}")
    print(f"  Subjects      : {C}{total_sub}{R}")
    print(f"  Total Records : {C}{total_r}{R}")
    print(f"  Classes Held  : {C}{len(dates)}{R}")
    if dates:
        print(f"  First Date    : {DIM}{dates[0]}{R}")
        print(f"  Latest Date   : {DIM}{dates[-1]}{R}")
    color = G if overall_pct >= 75 else Y if overall_pct >= 60 else RED
    print(f"  Overall Pct   : {color}{overall_pct:.1f}%{R}")


# ── Sample Data Loader ────────────────────────────────────
def load_sample(data):
    if not confirm("Load sample data? (overwrites existing)"):
        return
    data["students"] = {
        "RA001": {"name": "Sameer Bansal", "branch": "CSE IoT"},
        "RA002": {"name": "Priya Sharma", "branch": "CSE IoT"},
        "RA003": {"name": "Arjun Mehta", "branch": "CSE AI"},
        "RA004": {"name": "Sneha Iyer", "branch": "CSE AI"},
        "RA005": {"name": "Rohan Verma", "branch": "CSE CORE"},
    }
    data["subjects"] = ["PYTHON", "DBMS", "OS", "NETWORKS"]
    data["records"] = []
    import random

    base = datetime.date(2026, 4, 1)
    for day_offset in range(10):
        d = (base + datetime.timedelta(days=day_offset)).isoformat()
        for sub in data["subjects"]:
            for roll in data["students"]:
                status = random.choices(["P", "A", "L"], weights=[80, 15, 5])[0]
                data["records"].append(
                    {
                        "roll": roll,
                        "name": data["students"][roll]["name"],
                        "subject": sub,
                        "date": d,
                        "status": status,
                    }
                )
    save_data(data)
    print(f"  {G}✅ Sample data loaded ({len(data['records'])} records).{R}")


# ── Main Menu ─────────────────────────────────────────────
def main():
    data = load_data()
    while True:
        clear()
        banner()
        summary_dashboard(data)
        print(f"""
  {BOLD}STUDENTS{R}
  [1] Add student        [2] Remove student      [3] List students

  {BOLD}SUBJECTS{R}
  [4] Add subject        [5] List subjects

  {BOLD}ATTENDANCE{R}
  [6] Mark attendance

  {BOLD}REPORTS{R}
  [7] Student report     [8] Subject report      [9] Date report
  [a] Low attendance     [e] Export CSV

  {BOLD}TOOLS{R}
  [s] Load sample data   [q] Quit
""")
        choice = input("  → ").strip().lower()
        clear()
        banner()

        if choice == "1":
            add_student(data)
        elif choice == "2":
            remove_student(data)
        elif choice == "3":
            list_students(data)
        elif choice == "4":
            add_subject(data)
        elif choice == "5":
            list_subjects(data)
        elif choice == "6":
            mark_attendance(data)
        elif choice == "7":
            report_student(data)
        elif choice == "8":
            report_subject(data)
        elif choice == "9":
            report_date(data)
        elif choice == "a":
            low_attendance_alert(data)
        elif choice == "e":
            export_csv(data)
        elif choice == "s":
            load_sample(data)
        elif choice == "q":
            print(f"\n  👋 Goodbye!\n")
            break
        else:
            print(f"  {Y}Invalid choice.{R}")
        pause()


if __name__ == "__main__":
    main()
