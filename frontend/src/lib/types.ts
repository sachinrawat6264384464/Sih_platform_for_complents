export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  designation?: string;
  is_active: boolean;
  is_superuser: boolean;
  bureau_assignments?: Array<{
    id: string;
    bureau_id: string;
    bureau_name?: string;
    role: string;
    is_primary: boolean;
  }>;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Institution {
  id: string;
  aicte_permanent_id: string;
  current_application_id?: string;
  name: string;
  alternate_names: string[];
  institution_type: string;
  address: string;
  city: string;
  district: string;
  state: string;
  pincode: string;
  regional_office_id?: string;
  regional_office_name?: string;
  approval_status: string;
  contact_email?: string;
  contact_phone?: string;
  complaint_count?: number;
  active_case_count?: number;
  created_at: string;
}

export interface ComplaintCategory {
  id: string;
  name: string;
  code: string;
  description?: string;
}

export interface Bureau {
  id: string;
  code: string;
  name: string;
  description?: string;
  contact_email?: string;
  is_active: boolean;
}

export interface RegionalOffice {
  id: string;
  code: string;
  name: string;
  states_covered: string[];
  headquarters_city: string;
}

export interface Complaint {
  id: string;
  complaint_number: string;
  source_system_id?: string;
  source_bureau_id?: string;
  source_reference_id?: string;
  institution_id: string;
  institution_name?: string;
  aicte_permanent_id?: string;
  bureau_id: string;
  bureau_name?: string;
  category_id: string;
  category_name?: string;
  title: string;
  description: string;
  priority: "Low" | "Medium" | "High" | "Critical";
  status: string;
  received_date: string;
  assigned_officer_id?: string;
  assigned_officer_name?: string;
  sla_target_date?: string;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
  audit_entries?: ComplaintAudit[];
}

export interface ComplaintAudit {
  id: string;
  from_status?: string;
  to_status: string;
  action_type: string;
  performed_by_id: string;
  performer_name?: string;
  remarks?: string;
  created_at: string;
}

export interface OverlapCandidate {
  id: string;
  source_complaint_id: string;
  target_complaint_id: string;
  source_complaint_number?: string;
  target_complaint_number?: string;
  institution_id: string;
  institution_name?: string;
  source_bureau_name?: string;
  target_bureau_name?: string;
  overall_score: number;
  stage_scores: Record<string, number>;
  signals: Record<string, any>;
  review_status: "Pending" | "Confirmed" | "Rejected";
  review_remarks?: string;
  created_at: string;
}

export interface DashboardMetrics {
  total_institutions: number;
  total_complaints: number;
  pending_complaints: number;
  under_process_complaints: number;
  disposed_complaints: number;
  transferred_complaints: number;
  escalated_complaints: number;
  overdue_complaints: number;
  potential_overlapping_cases: number;
  confirmed_linked_cases: number;
  sla_compliance_rate?: number;
  integration_health_score?: number;
  bureau_workload?: Array<{
    bureau_code?: string;
    bureau_name: string;
    total_complaints?: number;
    count?: number;
    pending?: number;
    under_process?: number;
    disposed?: number;
    escalated?: number;
  }>;
  regional_workload?: Array<{
    region_code?: string;
    region_name: string;
    city?: string;
    total_institutions?: number;
    total_complaints?: number;
    count?: number;
    pending?: number;
  }>;
  region_workload?: Array<{
    region_code?: string;
    region_name: string;
    city?: string;
    total_institutions?: number;
    total_complaints?: number;
    count?: number;
    pending?: number;
  }>;
  complaint_ageing?: {
    under_7_days: number;
    days_8_to_30: number;
    days_31_to_90: number;
    over_90_days: number;
  };
  monthly_trends?: Array<{ month: string; disposed: number; received: number }>;
  monthly_disposal_trends?: Array<{ month: string; disposed: number; received: number }>;
  sla_compliance?: {
    within_sla_count: number;
    overdue_count: number;
    compliance_percentage: number;
  };
  integration_health?: Array<{
    connector_name: string;
    is_active: boolean;
    last_sync_time?: string;
    records_synced_total: number;
  }>;
}

export interface MCPServerInfo {
  server_id: string;
  name: string;
  description: string;
  version: string;
  status: string;
  tools: Array<{
    name: string;
    description: string;
    parameters: Record<string, any>;
  }>;
}

