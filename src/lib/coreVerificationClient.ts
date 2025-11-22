import axios, { AxiosError, AxiosInstance } from "axios";
import { env } from "../config/env";

const DEFAULT_TIMEOUT_MS = 15_000;

export type VerificationJobPayload = {
  text: string;
  source_uri?: string;
  author_id?: string;
  claim_hash?: string;
  domain?: string;
  policy_id?: string;
  requested_by?: string;
};

export type CoreAssessment = {
  agent_id?: string;
  verdict?: string;
  confidence?: number;
  created_at?: string;
  evidence_uris?: string[];
};

export type CoreSnapshot = {
  id: string;
  source_uri?: string;
  author_id?: string;
  parent_snapshot_id?: string | null;
  created_at?: string;
  ps_sha_infinity?: string;
};

export type CoreTruthState = {
  claim_hash: string;
  status: string;
  aggregate_confidence?: number | null;
  job_ids?: string[];
  minority_reports?: string[];
  last_updated?: string;
  policy_id?: string;
  domain?: string;
};

export type CoreVerificationJob = {
  job_id: string;
  snapshot_id?: string;
  claim_hash?: string;
  status: string;
  created_at?: string;
  domain?: string;
  policy_id?: string;
  truth_state?: CoreTruthState | null;
  snapshot?: CoreSnapshot;
  assessments?: CoreAssessment[];
};

export type CoreProvenanceGraph = {
  snapshot: CoreSnapshot;
  parent_snapshot?: CoreSnapshot | null;
  derived_snapshots?: CoreSnapshot[];
  related_jobs?: { id: string; status?: string }[];
  ledger_entries?: { id: string; type: string }[];
};

export class CoreVerificationError extends Error {
  status?: number;
  data?: any;

  constructor(message: string, status?: number, data?: any) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

const createClient = (): AxiosInstance =>
  axios.create({
    baseURL: env.CORE_VERIFICATION_BASE_URL,
    timeout: DEFAULT_TIMEOUT_MS,
  });

const mapAxiosError = (error: AxiosError): CoreVerificationError => {
  const status = error.response?.status;
  const data = error.response?.data;
  const message =
    (data && typeof data === "object" && "message" in data
      ? (data as Record<string, any>).message
      : undefined) || error.message;

  return new CoreVerificationError(message, status, data);
};

export interface VerificationServiceClient {
  createVerificationJob(
    payload: VerificationJobPayload
  ): Promise<CoreVerificationJob>;
  getVerificationJob(jobId: string): Promise<CoreVerificationJob>;
  getTruthState(claimHash: string): Promise<CoreTruthState>;
  getProvenance(snapshotId: string): Promise<CoreProvenanceGraph>;
}

export class CoreVerificationClient implements VerificationServiceClient {
  private client: AxiosInstance;

  constructor(client: AxiosInstance = createClient()) {
    this.client = client;
  }

  async createVerificationJob(
    payload: VerificationJobPayload
  ): Promise<CoreVerificationJob> {
    try {
      const response = await this.client.post("/verification/jobs", payload);
      return response.data as CoreVerificationJob;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw mapAxiosError(error);
      }
      throw error;
    }
  }

  async getVerificationJob(jobId: string): Promise<CoreVerificationJob> {
    try {
      const response = await this.client.get(`/verification/jobs/${jobId}`);
      return response.data as CoreVerificationJob;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw mapAxiosError(error);
      }
      throw error;
    }
  }

  async getTruthState(claimHash: string): Promise<CoreTruthState> {
    try {
      const response = await this.client.get(`/truth/${claimHash}`);
      return response.data as CoreTruthState;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw mapAxiosError(error);
      }
      throw error;
    }
  }

  async getProvenance(snapshotId: string): Promise<CoreProvenanceGraph> {
    try {
      const response = await this.client.get(`/provenance/${snapshotId}`);
      return response.data as CoreProvenanceGraph;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw mapAxiosError(error);
      }
      throw error;
    }
  }
}

export const coreVerificationClient = new CoreVerificationClient();
