import asyncio
import random
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.institution import Institution
from app.models.bureau import Bureau, RegionalOffice
from app.models.complaint import Complaint, ComplaintCategory, SourceSystem, ComplaintStatus, ComplaintPriority
from app.models.auth import User
from app.services.overlap_engine import OverlapDetectionEngine

SAMPLE_INSTITUTIONS = [
    {
        "aicte_permanent_id": "1-10293847",
        "name": "Pune Institute of Advanced Technology",
        "alternate_names": ["PIAT Pune", "PIAT College"],
        "institution_type": "Engineering & Technology",
        "address": "Survey No 45, Kothrud",
        "city": "Pune",
        "district": "Pune",
        "state": "Maharashtra",
        "pincode": "411038",
        "approval_status": "Approved",
    },
    {
        "aicte_permanent_id": "1-29481023",
        "name": "Bangalore Institute of Computer Sciences",
        "alternate_names": ["BICS Bangalore", "BICS Tech"],
        "institution_type": "Autonomous",
        "address": "K.R. Road, V.V. Puram",
        "city": "Bengaluru",
        "district": "Bengaluru Urban",
        "state": "Karnataka",
        "pincode": "560004",
        "approval_status": "Approved",
    },
    {
        "aicte_permanent_id": "1-38491024",
        "name": "Coimbatore National College of Engineering",
        "alternate_names": ["CNCE Coimbatore", "National Tech Coimbatore"],
        "institution_type": "Engineering & Technology",
        "address": "Avinashi Road, Civil Aerodrome Post",
        "city": "Coimbatore",
        "district": "Coimbatore",
        "state": "Tamil Nadu",
        "pincode": "641014",
        "approval_status": "Approved",
    },
    {
        "aicte_permanent_id": "1-48201934",
        "name": "Noida Institute of Technological Sciences",
        "alternate_names": ["NITS Greater Noida", "Noida Tech"],
        "institution_type": "Management & Technology",
        "address": "Knowledge Park II",
        "city": "Greater Noida",
        "district": "Gautam Buddha Nagar",
        "state": "Uttar Pradesh",
        "pincode": "201306",
        "approval_status": "Approved",
    },
    {
        "aicte_permanent_id": "1-59102938",
        "name": "Hyderabad Academy of Technical Studies",
        "alternate_names": ["HATS Hyderabad", "HATS Engineering"],
        "institution_type": "Engineering & Technology",
        "address": "Gachibowli Main Road",
        "city": "Hyderabad",
        "district": "Hyderabad",
        "state": "Telangana",
        "pincode": "500032",
        "approval_status": "Approved",
    },
    {
        "aicte_permanent_id": "1-60293847",
        "name": "Kolkata Institute of Engineering & Management",
        "alternate_names": ["KIEM Kolkata", "KIEM Tech"],
        "institution_type": "Autonomous",
        "address": "Sector V, Salt Lake City",
        "city": "Kolkata",
        "district": "North 24 Parganas",
        "state": "West Bengal",
        "pincode": "700091",
        "approval_status": "Approved",
    },
    {
        "aicte_permanent_id": "1-71029384",
        "name": "Bhopal Technical College of Science",
        "alternate_names": ["BTCS Bhopal", "Bhopal Tech"],
        "institution_type": "Engineering & Technology",
        "address": "Raisen Road, Patel Nagar",
        "city": "Bhopal",
        "district": "Bhopal",
        "state": "Madhya Pradesh",
        "pincode": "462021",
        "approval_status": "Approved",
    },
    {
        "aicte_permanent_id": "1-82019384",
        "name": "Chandigarh Polytechnic & Engineering College",
        "alternate_names": ["CPEC Chandigarh"],
        "institution_type": "Polytechnic & Diploma",
        "address": "Sector 26, Madhya Marg",
        "city": "Chandigarh",
        "district": "Chandigarh",
        "state": "Chandigarh",
        "pincode": "160019",
        "approval_status": "Approved",
    },
]

COMPLAINT_TEMPLATES = [
    {
        "title": "Demanding Capitation Fee for Computer Engineering Admission",
        "desc": "Management is explicitly demanding 1.5 Lakh INR in cash over and above statutory tuition fee before confirming allotment.",
        "cat_code": "CAPITATION_FEE",
        "priority": ComplaintPriority.CRITICAL,
    },
    {
        "title": "Withholding Original 10th and 12th Marksheets on Transfer",
        "desc": "College registrar refused to return original educational certificates when student requested transfer certificate.",
        "cat_code": "CERTIFICATE_WITHHOLDING",
        "priority": ComplaintPriority.HIGH,
    },
    {
        "title": "Gross Faculty Shortage and Fake Faculty List Submitted for EOA",
        "desc": "Inspection records indicate 40 percent vacant faculty posts. Guest faculties are listed as regular professors for AICTE approval.",
        "cat_code": "FACULTY_SHORTAGE",
        "priority": ComplaintPriority.CRITICAL,
    },
    {
        "title": "Unapproved Evening Shift Classes and Infrastructure Deficit",
        "desc": "Institution is operating unapproved second shift classes without laboratory space, violating sanctioned student-faculty ratio.",
        "cat_code": "INFRASTRUCTURE",
        "priority": ComplaintPriority.HIGH,
    },
    {
        "title": "Non-Refund of Caution Deposit Following Course Completion",
        "desc": "Graduating batch of 2025 has not received caution money refund despite submitting no-dues clearance 6 months ago.",
        "cat_code": "CAPITATION_FEE",
        "priority": ComplaintPriority.MEDIUM,
    },
    {
        "title": "Arbitrary Exam Hall Ticket Fee Levied 2 Days Before Exams",
        "desc": "Institution has locked digital student portals and demands mandatory Rs 5,000 special examination infrastructure fee.",
        "cat_code": "CAPITATION_FEE",
        "priority": ComplaintPriority.HIGH,
    },
    {
        "title": "Serious Safety Violations in Chemical Engineering Laboratories",
        "desc": "Absence of fire suppression systems and emergency eyewash stations in organic chemistry lab.",
        "cat_code": "INFRASTRUCTURE",
        "priority": ComplaintPriority.HIGH,
    },
    {
        "title": "Violation of AICTE Approved Intake Norms During Lateral Entry",
        "desc": "Direct second year lateral entry admission granted exceeding the statutory 10 percent approved supernumerary quota.",
        "cat_code": "ADMISSION_IRREGULARITY",
        "priority": ComplaintPriority.HIGH,
    },
]

async def seed():
    async with AsyncSessionLocal() as db:
        print("Checking database records...")

        # 1. Fetch Bureaus, Categories, and Source Systems
        bureaus = (await db.execute(select(Bureau))).scalars().all()
        bureau_map = {b.code: b for b in bureaus}

        categories = (await db.execute(select(ComplaintCategory))).scalars().all()
        cat_map = {c.code: c for c in categories}

        sources = (await db.execute(select(SourceSystem))).scalars().all()
        source_sys = sources[0] if sources else None

        admin_user = (await db.execute(select(User).where(User.username == "admin"))).scalar_one()

        # 2. Add sample institutions
        created_institutions = []
        for inst_data in SAMPLE_INSTITUTIONS:
            existing = (await db.execute(select(Institution).where(Institution.aicte_permanent_id == inst_data["aicte_permanent_id"]))).scalar_one_or_none()
            if not existing:
                inst = Institution(**inst_data)
                db.add(inst)
                created_institutions.append(inst)
            else:
                created_institutions.append(existing)

        await db.commit()
        for inst in created_institutions:
            await db.refresh(inst)
        print(f"Total institutions active: {len(created_institutions)}")

        # 3. Add rich multi-bureau complaints
        pgrc_bureau = bureau_map.get("PGRC") or bureaus[0]
        rb_bureau = bureau_map.get("RB") or (bureaus[1] if len(bureaus) > 1 else bureaus[0])

        created_complaints = []
        statuses = [
            ComplaintStatus.RECEIVED,
            ComplaintStatus.ACKNOWLEDGED,
            ComplaintStatus.UNDER_REVIEW,
            ComplaintStatus.ASSIGNED,
            ComplaintStatus.UNDER_PROCESS,
            ComplaintStatus.INVESTIGATION,
        ]

        for i, inst in enumerate(created_institutions):
            c1_tpl = COMPLAINT_TEMPLATES[i % len(COMPLAINT_TEMPLATES)]
            c2_tpl = COMPLAINT_TEMPLATES[(i + 2) % len(COMPLAINT_TEMPLATES)]

            # Complaint 1: In PGRC
            c1 = Complaint(
                complaint_number=f"AICTE-2026-{random.randint(100000, 999999)}",
                institution_id=inst.id,
                bureau_id=pgrc_bureau.id,
                source_system_id=source_sys.id,
                category_id=cat_map.get(c1_tpl["cat_code"], categories[0]).id,
                title=f"{c1_tpl['title']} - {inst.name}",
                description=c1_tpl["desc"],
                priority=c1_tpl["priority"],
                status=random.choice(statuses),
                received_date=datetime.now(timezone.utc) - timedelta(days=random.randint(2, 60)),
                due_date=datetime.now(timezone.utc) + timedelta(days=random.randint(5, 25)),
            )
            db.add(c1)
            created_complaints.append(c1)

            # Complaint 2: In Regulation Bureau (Creates high overlap signal for same college!)
            c2 = Complaint(
                complaint_number=f"AICTE-2026-{random.randint(100000, 999999)}",
                institution_id=inst.id,
                bureau_id=rb_bureau.id,
                source_system_id=source_sys.id,
                category_id=cat_map.get(c2_tpl["cat_code"], categories[0]).id,
                title=f"{c2_tpl['title']} - {inst.name}",
                description=c2_tpl["desc"],
                priority=c2_tpl["priority"],
                status=random.choice(statuses),
                received_date=datetime.now(timezone.utc) - timedelta(days=random.randint(5, 45)),
                due_date=datetime.now(timezone.utc) + timedelta(days=random.randint(1, 20)),
            )
            db.add(c2)
            created_complaints.append(c2)

        # Add 4 disposed complaints for historical trend curves
        for j in range(4):
            c_disp = Complaint(
                complaint_number=f"AICTE-2026-{random.randint(100000, 999999)}",
                institution_id=created_institutions[j % len(created_institutions)].id,
                bureau_id=pgrc_bureau.id,
                source_system_id=source_sys.id,
                category_id=categories[0].id,
                title=f"Resolved: Caution Deposit Redressal - {created_institutions[j].name}",
                description="Statutory grievance amicably resolved following joint verification by PGRC officer.",
                priority=ComplaintPriority.MEDIUM,
                status=ComplaintStatus.DISPOSED,
                received_date=datetime.now(timezone.utc) - timedelta(days=random.randint(30, 90)),
                disposed_date=datetime.now(timezone.utc) - timedelta(days=random.randint(2, 10)),
                due_date=datetime.now(timezone.utc) + timedelta(days=20),
            )
            db.add(c_disp)
            created_complaints.append(c_disp)

        await db.commit()
        print(f"Successfully seeded {len(created_complaints)} realistic complaints.")

        # 4. Trigger Overlap Scan for newly seeded complaints
        print("Running 8-Stage Sieve Engine on all active complaints...")
        from app.services.overlap_engine import scan_complaint_for_overlaps
        total_overlaps = 0
        for c in created_complaints:
            cands = await scan_complaint_for_overlaps(db, c.id)
            total_overlaps += len(cands)
        print(f"Overlap scanning complete. Generated {total_overlaps} overlap candidate pairs.")

if __name__ == "__main__":
    asyncio.run(seed())
