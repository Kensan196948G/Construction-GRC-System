import apiClient from "@/api/client";

export interface GRCDashboardData {
  risks: {
    total: number;
    by_level: Record<string, number>;
    by_status: Record<string, number>;
    by_category: Record<string, number>;
  };
  compliance: {
    total: number;
    compliant: number;
    non_compliant: number;
    partial: number;
    unknown: number;
    rate: number;
  };
  controls: {
    total_applicable: number;
    implemented: number;
    in_progress: number;
    not_started: number;
    partially: number;
    rate: number;
  };
  audits: {
    total_audits: number;
    completed: number;
    in_progress: number;
    planned: number;
    total_findings: number;
    open_findings: number;
    by_type: Record<string, number>;
  };
}

export async function getDashboardData(): Promise<GRCDashboardData> {
  const response = await apiClient.get<GRCDashboardData>(
    "/api/v1/dashboard/"
  );
  return response.data;
}

export async function downloadDashboardPdf(): Promise<Blob> {
  const response = await apiClient.get(
    "/api/v1/reports/generate/dashboard-pdf/",
    { responseType: "blob" }
  );
  return response.data;
}

export async function downloadCompliancePdf(): Promise<Blob> {
  const response = await apiClient.get(
    "/api/v1/reports/generate/compliance-pdf/",
    { responseType: "blob" }
  );
  return response.data;
}

export async function downloadRiskPdf(): Promise<Blob> {
  const response = await apiClient.get(
    "/api/v1/reports/generate/risk-pdf/",
    { responseType: "blob" }
  );
  return response.data;
}
