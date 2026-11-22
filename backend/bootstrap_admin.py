import argparse
import getpass
import secrets
import string
import sys
from datetime import datetime, timezone
from sqlalchemy import select
from app.core.database import SyncSessionLocal, sync_engine
from app.core.security import get_password_hash
from app.models.auth import Permission, Role, RolePermission, User, UserRole, UserBureauAssignment
from app.models.bureau import Bureau, RegionalOffice
from app.models.complaint import ComplaintCategory, SourceSystem
from app.models.audit import AuditLog, SystemSetting

# Standard AICTE Bureaus
DEFAULT_BUREAUS = [
    {"code": "PGRC", "name": "Public Grievance Redressal Cell", "description": "Grievance redressal for students, faculty, and stakeholders", "contact_email": "pgrc@aicte-india.org", "escalation_level": 1},
    {"code": "RB", "name": "Regulation Bureau", "description": "Regulatory compliance, inquiry proceedings, disciplinary measures", "contact_email": "regulation@aicte-india.org", "escalation_level": 2},
    {"code": "AB", "name": "Approval Bureau", "description": "Institutional approvals, extension of approval (EOA), new programs", "contact_email": "approval@aicte-india.org", "escalation_level": 1},
    {"code": "PB", "name": "Policy & Academic Bureau", "description": "Curriculum standards, academic guidelines, faculty norms", "contact_email": "policy@aicte-india.org", "escalation_level": 1},
]

# Standard AICTE Regional Offices
DEFAULT_REGIONS = [
    {"code": "NRO", "name": "Northern Regional Office", "city": "Kanpur", "state": "Uttar Pradesh", "jurisdiction_states": ["Uttar Pradesh", "Uttarakhand"]},
    {"code": "NWRO", "name": "North-Western Regional Office", "city": "Chandigarh", "state": "Chandigarh", "jurisdiction_states": ["Punjab", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Ladakh", "Delhi"]},
    {"code": "WRO", "name": "Western Regional Office", "city": "Mumbai", "state": "Maharashtra", "jurisdiction_states": ["Maharashtra", "Goa"]},
    {"code": "CRO", "name": "Central Regional Office", "city": "Bhopal", "state": "Madhya Pradesh", "jurisdiction_states": ["Madhya Pradesh", "Chhattisgarh", "Gujarat"]},
    {"code": "SRO", "name": "Southern Regional Office", "city": "Chennai", "state": "Tamil Nadu", "jurisdiction_states": ["Tamil Nadu", "Puducherry"]},
    {"code": "SWRO", "name": "South-Western Regional Office", "city": "Bangalore", "state": "Karnataka", "jurisdiction_states": ["Karnataka", "Kerala"]},
    {"code": "ERO", "name": "Eastern Regional Office", "city": "Kolkata", "state": "West Bengal", "jurisdiction_states": ["West Bengal", "Bihar", "Jharkhand", "Odisha", "Assam", "Meghalaya", "Manipur", "Mizoram", "Nagaland", "Tripura", "Arunachal Pradesh", "Sikkim"]},
]

# Standard Complaint Categories
DEFAULT_CATEGORIES = [
    {"code": "FACULTY_SHORTAGE", "name": "Faculty Shortage / Non-Payment of UGC Scales", "severity_level": "High", "default_sla_days": 21},
    {"code": "CAPITATION_FEE", "name": "Demanding Capitation Fee / Overcharging", "severity_level": "Critical", "default_sla_days": 14},
    {"code": "RAGGING", "name": "Anti-Ragging Violation / Campus Harassment", "severity_level": "Critical", "default_sla_days": 7},
    {"code": "INFRASTRUCTURE", "name": "Infrastructure & Lab Deficiencies", "severity_level": "Medium", "default_sla_days": 30},
    {"code": "FAKE_DOCUMENTS", "name": "Submission of Fraudulent Documents / Misrepresentation", "severity_level": "Critical", "default_sla_days": 14},
    {"code": "ADMISSION_IRREGULARITY", "name": "Irregularities in Admission Procedure / Seat Allotment", "severity_level": "High", "default_sla_days": 21},
    {"code": "CERTIFICATE_WITHHOLDING", "name": "Unlawful Withholding of Student Certificates/Mark sheets", "severity_level": "High", "default_sla_days": 10},
    {"code": "ACADEMIC_MALPRACTICE", "name": "Unapproved Programs / Running Unapproved Shifts", "severity_level": "High", "default_sla_days": 21},
]

# Standard Source Systems
DEFAULT_SOURCES = [
    {"code": "PGRC_PORTAL", "name": "AICTE Central PGRC Web Portal", "description": "Online public grievance submission channel"},
    {"code": "RB_PORTAL", "name": "Regulation Bureau Case Portal", "description": "Direct regulatory referrals and vigilance inquiries"},
    {"code": "EMAIL_INGESTION", "name": "Official Grievance Email Gateway", "description": "Approved institutional complaint mailboxes"},
    {"code": "REGIONAL_SYNC", "name": "Regional Office Batch Sync", "description": "Periodic sync from zonal regional offices"},
    {"code": "MANUAL_CSV", "name": "Authorized CSV / Excel Import", "description": "Batch ingestion of offline institutional dossiers"},
]

# Standard Roles
DEFAULT_ROLES = [
    {"code": "SUPER_ADMIN", "name": "Super Admin", "description": "Full unconstrained administrative privileges", "is_system": True},
    {"code": "AICTE_ADMIN", "name": "AICTE Administrator", "description": "High-level platform administrator", "is_system": True},
    {"code": "SENIOR_OFFICER", "name": "Senior Officer", "description": "Executive review across bureaus", "is_system": True},
    {"code": "BUREAU_HEAD", "name": "Bureau Head", "description": "Bureau chief with transfer and assignment oversight", "is_system": True},
    {"code": "REGIONAL_OFFICER", "name": "Regional Officer", "description": "Jurisdiction oversight for assigned states", "is_system": True},
    {"code": "CASE_OFFICER", "name": "Case Officer", "description": "Direct complaint handling and investigation", "is_system": True},
    {"code": "PGRC_OFFICER", "name": "PGRC Officer", "description": "Public grievance specialized handler", "is_system": True},
    {"code": "RB_OFFICER", "name": "Regulation Bureau Officer", "description": "Inquiry and disciplinary case officer", "is_system": True},
    {"code": "AUDITOR", "name": "Auditor", "description": "Read-only access to audit logs and security metrics", "is_system": True},
    {"code": "READ_ONLY", "name": "Read-Only Viewer", "description": "General inspection and dashboard viewing only", "is_system": True},
]

# Standard Granular Permissions
DEFAULT_PERMISSIONS = [
    # Institutions
    {"code": "INSTITUTION_READ", "name": "Read Institutions", "module": "institution"},
    {"code": "INSTITUTION_CREATE", "name": "Create Institution", "module": "institution"},
    {"code": "INSTITUTION_UPDATE", "name": "Update Institution", "module": "institution"},
    {"code": "INSTITUTION_ARCHIVE", "name": "Archive Institution", "module": "institution"},
    # Complaints
    {"code": "COMPLAINT_READ", "name": "Read Complaints", "module": "complaint"},
    {"code": "COMPLAINT_CREATE", "name": "Register Complaint", "module": "complaint"},
    {"code": "COMPLAINT_UPDATE", "name": "Update Complaint", "module": "complaint"},
    {"code": "COMPLAINT_ASSIGN", "name": "Assign Complaint", "module": "complaint"},
    {"code": "COMPLAINT_STATUS", "name": "Change Complaint Status", "module": "complaint"},
    # Cases & Coordination
    {"code": "CASE_COORDINATE", "name": "Manage Cross-Bureau Cases", "module": "case"},
    {"code": "CASE_TRANSFER", "name": "Initiate & Approve Transfers", "module": "case"},
    {"code": "CASE_ESCALATE", "name": "Escalate Case to Higher Authority", "module": "case"},
    {"code": "OVERLAP_REVIEW", "name": "Confirm or Reject Overlap Candidates", "module": "overlap"},
    # Administration
    {"code": "USER_MANAGE", "name": "Manage Users & Permissions", "module": "admin"},
    {"code": "BUREAU_MANAGE", "name": "Manage Bureaus & Regions", "module": "admin"},
    {"code": "INTEGRATION_MANAGE", "name": "Configure Integration Connectors", "module": "admin"},
    {"code": "MCP_MANAGE", "name": "Manage Model Context Protocol Servers", "module": "admin"},
    {"code": "SYSTEM_SETTINGS", "name": "Edit Global System Settings", "module": "admin"},
    {"code": "AUDIT_READ", "name": "Inspect Audit & Security Logs", "module": "audit"},
    {"code": "REPORT_GENERATE", "name": "Generate Authorized Reports", "module": "report"},
]


def generate_secure_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%^&*()-_=+" for c in password)):
            return password


def seed_metadata(session):
    print("🌱 Seeding Bureaus...")
    for b_data in DEFAULT_BUREAUS:
        existing = session.execute(select(Bureau).where(Bureau.code == b_data["code"])).scalar_one_or_none()
        if not existing:
            bureau = Bureau(**b_data)
            session.add(bureau)

    print("🌱 Seeding Regional Offices...")
    for r_data in DEFAULT_REGIONS:
        existing = session.execute(select(RegionalOffice).where(RegionalOffice.code == r_data["code"])).scalar_one_or_none()
        if not existing:
            reg = RegionalOffice(**r_data)
            session.add(reg)

    print("🌱 Seeding Complaint Categories...")
    for c_data in DEFAULT_CATEGORIES:
        existing = session.execute(select(ComplaintCategory).where(ComplaintCategory.code == c_data["code"])).scalar_one_or_none()
        if not existing:
            cat = ComplaintCategory(**c_data)
            session.add(cat)

    print("🌱 Seeding Source Systems...")
    for s_data in DEFAULT_SOURCES:
        existing = session.execute(select(SourceSystem).where(SourceSystem.code == s_data["code"])).scalar_one_or_none()
        if not existing:
            src = SourceSystem(**s_data)
            session.add(src)

    print("🌱 Seeding Permissions...")
    perm_map = {}
    for p_data in DEFAULT_PERMISSIONS:
        existing = session.execute(select(Permission).where(Permission.code == p_data["code"])).scalar_one_or_none()
        if not existing:
            perm = Permission(**p_data)
            session.add(perm)
            session.flush()
            perm_map[p_data["code"]] = perm
        else:
            perm_map[p_data["code"]] = existing

    print("🌱 Seeding Roles...")
    role_map = {}
    for r_data in DEFAULT_ROLES:
        existing = session.execute(select(Role).where(Role.code == r_data["code"])).scalar_one_or_none()
        if not existing:
            role = Role(**r_data)
            session.add(role)
            session.flush()
            role_map[r_data["code"]] = role
        else:
            role_map[r_data["code"]] = existing

    # Assign all permissions to SUPER_ADMIN
    super_admin_role = role_map.get("SUPER_ADMIN")
    if super_admin_role:
        for p in perm_map.values():
            has_link = session.execute(
                select(RolePermission).where(
                    RolePermission.role_id == super_admin_role.id,
                    RolePermission.permission_id == p.id
                )
            ).scalar_one_or_none()
            if not has_link:
                session.add(RolePermission(role_id=super_admin_role.id, permission_id=p.id))

    # Initialize System Settings
    settings_data = [
        {"setting_key": "PLATFORM_NAME", "setting_value": {"value": "AICTE NEXUS"}, "description": "Platform display name", "is_public": True},
        {"setting_key": "MAINTENANCE_MODE", "setting_value": {"enabled": False}, "description": "Maintenance mode state", "is_public": True},
        {"setting_key": "AI_HYBRID_RAG_ENABLED", "setting_value": {"enabled": True}, "description": "Hybrid RAG active state", "is_public": False},
        {"setting_key": "AUTO_OVERLAP_ANALYSIS", "setting_value": {"enabled": True}, "description": "Analyze overlap on ingestion", "is_public": False},
    ]
    for s_item in settings_data:
        existing = session.execute(select(SystemSetting).where(SystemSetting.setting_key == s_item["setting_key"])).scalar_one_or_none()
        if not existing:
            session.add(SystemSetting(**s_item))

    session.commit()
    print("✅ Foundation metadata seeded successfully.")


def bootstrap_admin(username: str, email: str, password: str, full_name: str, designation: str = "Chief Technology Officer"):
    with SyncSessionLocal() as session:
        seed_metadata(session)

        # Check if user already exists
        existing_user = session.execute(select(User).where((User.username == username) | (User.email == email))).scalar_one_or_none()
        if existing_user:
            print(f"⚠️ User with username '{username}' or email '{email}' already exists (ID: {existing_user.id}).")
            return existing_user

        hashed_pw = get_password_hash(password)
        admin = User(
            username=username,
            email=email,
            hashed_password=hashed_pw,
            full_name=full_name,
            designation=designation,
            is_active=True,
            is_superuser=True
        )
        session.add(admin)
        session.flush()

        # Attach Super Admin Role
        super_admin_role = session.execute(select(Role).where(Role.code == "SUPER_ADMIN")).scalar_one()
        session.add(UserRole(user_id=admin.id, role_id=super_admin_role.id))

        # Log audit entry
        session.add(AuditLog(
            user_id=admin.id,
            action="BOOTSTRAP_ADMIN",
            entity_type="USER",
            entity_id=admin.id,
            changes={"username": username, "email": email, "role": "SUPER_ADMIN"},
            ip_address="127.0.0.1",
            user_agent="CLI_BOOTSTRAP"
        ))

        session.commit()
        print(f"\n=======================================================")
        print(f"🎉 Super Administrator Provisioned Successfully!")
        print(f"=======================================================")
        print(f"Username    : {username}")
        print(f"Email       : {email}")
        print(f"Role        : SUPER_ADMIN")
        print(f"User ID     : {admin.id}")
        print(f"=======================================================\n")
        return admin


def main():
    parser = argparse.ArgumentParser(description="AICTE Nexus - Secure Administrator Bootstrap")
    parser.add_argument("--username", help="Administrator username")
    parser.add_argument("--email", help="Administrator email")
    parser.add_argument("--password", help="Administrator password")
    parser.add_argument("--full-name", help="Administrator full name")
    parser.add_argument("--auto-generate", action="store_true", help="Auto-generate a high-entropy password")
    args = parser.parse_args()

    print("\n🏛️  AICTE NEXUS - SECURE ADMIN BOOTSTRAP UTILITY")
    print("-------------------------------------------------")

    username = args.username or "aicte_admin"
    email = args.email or "admin@aicte-nexus.gov.in"
    full_name = args.full_name or "AICTE Executive Director"

    if args.auto_generate:
        password = generate_secure_password(18)
        print(f"🔑 Generated High-Entropy Secure Password: {password}")
    elif args.password:
        password = args.password
    else:
        # If interactive terminal
        if sys.stdin.isatty():
            username = input(f"Enter username [{username}]: ").strip() or username
            email = input(f"Enter email [{email}]: ").strip() or email
            full_name = input(f"Enter full name [{full_name}]: ").strip() or full_name
            password = getpass.getpass("Enter administrator password: ").strip()
            if not password:
                password = generate_secure_password(18)
                print(f"🔑 Empty password provided. Generated: {password}")
        else:
            password = generate_secure_password(18)
            print(f"🔑 Non-interactive session. Generated password: {password}")

    bootstrap_admin(username, email, password, full_name)


if __name__ == "__main__":
    main()

