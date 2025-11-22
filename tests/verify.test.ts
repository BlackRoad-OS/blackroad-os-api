import express from "express";
import request from "supertest";
import {
  CoreVerificationError,
  VerificationServiceClient,
} from "../src/lib/coreVerificationClient";
import { createVerificationRouter } from "../src/routes/v1/verify";

describe("Verification routes", () => {
  const app = express();
  app.use(express.json());

  const mockClient: jest.Mocked<VerificationServiceClient> = {
    createVerificationJob: jest.fn(),
    getVerificationJob: jest.fn(),
    getTruthState: jest.fn(),
    getProvenance: jest.fn(),
  };

  app.use("/v1", createVerificationRouter(mockClient));

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("POST /v1/verify", () => {
    it("creates a verification job", async () => {
      mockClient.createVerificationJob.mockResolvedValue({
        job_id: "job-123",
        snapshot_id: "snap-1",
        claim_hash: "claim-xyz",
        status: "pending",
        created_at: "2024-07-01T00:00:00Z",
        policy_id: "policy-1",
        domain: "news",
      });

      const response = await request(app).post("/v1/verify").send({
        text: "Example text",
        domain: "news",
      });

      expect(response.status).toBe(202);
      expect(response.body).toMatchObject({
        job: {
          id: "job-123",
          snapshot_id: "snap-1",
          status: "pending",
          domain: "news",
        },
        truth_state: null,
      });
      expect(mockClient.createVerificationJob).toHaveBeenCalledWith({
        text: "Example text",
        domain: "news",
      });
    });

    it("validates missing text", async () => {
      const response = await request(app).post("/v1/verify").send({});

      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty("error_code", "INVALID_REQUEST");
    });
  });

  describe("GET /v1/verify/jobs/:jobId", () => {
    it("returns job details", async () => {
      mockClient.getVerificationJob.mockResolvedValue({
        job_id: "job-123",
        snapshot_id: "snap-1",
        claim_hash: "claim-xyz",
        status: "running",
        created_at: "2024-07-01T00:00:00Z",
        assessments: [
          {
            agent_id: "agent:alpha",
            verdict: "confirmed",
            confidence: 0.92,
            created_at: "2024-07-01T01:00:00Z",
            evidence_uris: ["https://example.com"],
          },
        ],
        truth_state: {
          claim_hash: "claim-xyz",
          status: "confirmed",
          aggregate_confidence: 0.9,
          job_ids: ["job-123"],
          minority_reports: [],
          last_updated: "2024-07-01T02:00:00Z",
          policy_id: "policy-1",
          domain: "news",
        },
        snapshot: {
          id: "snap-1",
          source_uri: "https://example.com/post",
          author_id: "author-1",
          parent_snapshot_id: null,
          created_at: "2024-07-01T00:00:00Z",
          ps_sha_infinity: "hash123",
        },
      });

      const response = await request(app).get("/v1/verify/jobs/job-123");

      expect(response.status).toBe(200);
      expect(response.body.job).toMatchObject({ id: "job-123", status: "running" });
      expect(response.body.snapshot).toMatchObject({ id: "snap-1", hash: "hash123" });
      expect(response.body.assessments.count).toBe(1);
      expect(response.body.truth_state).toMatchObject({ status: "confirmed" });
    });

    it("maps 404 errors from core", async () => {
      mockClient.getVerificationJob.mockRejectedValue(
        new CoreVerificationError("Not found", 404, {
          error_code: "VERIFICATION_JOB_NOT_FOUND",
          message: "Verification job not found",
        })
      );

      const response = await request(app).get("/v1/verify/jobs/unknown");

      expect(response.status).toBe(404);
      expect(response.body).toHaveProperty("error_code", "VERIFICATION_JOB_NOT_FOUND");
    });
  });

  describe("GET /v1/truth/:claimHash", () => {
    it("returns truth state", async () => {
      mockClient.getTruthState.mockResolvedValue({
        claim_hash: "claim-xyz",
        status: "confirmed",
        aggregate_confidence: 0.8,
        job_ids: ["job-1"],
        minority_reports: [],
        last_updated: "2024-07-01T03:00:00Z",
        policy_id: "policy-1",
        domain: "news",
      });

      const response = await request(app).get("/v1/truth/claim-xyz");

      expect(response.status).toBe(200);
      expect(response.body).toMatchObject({
        claim_hash: "claim-xyz",
        status: "confirmed",
        aggregate_confidence: 0.8,
      });
    });

    it("returns 404 for unknown claim", async () => {
      mockClient.getTruthState.mockRejectedValue(
        new CoreVerificationError("Unknown claim", 404, {
          error_code: "TRUTH_STATE_NOT_FOUND",
          message: "Truth state not found",
        })
      );

      const response = await request(app).get("/v1/truth/missing-claim");

      expect(response.status).toBe(404);
      expect(response.body).toHaveProperty("error_code", "TRUTH_STATE_NOT_FOUND");
    });
  });

  describe("GET /v1/provenance/:snapshotId", () => {
    it("returns provenance graph", async () => {
      mockClient.getProvenance.mockResolvedValue({
        snapshot: {
          id: "snap-1",
          source_uri: "https://example.com/post",
          author_id: "author-1",
          parent_snapshot_id: null,
          created_at: "2024-07-01T00:00:00Z",
          ps_sha_infinity: "hash123",
        },
        parent_snapshot: null,
        derived_snapshots: [
          {
            id: "snap-2",
            parent_snapshot_id: "snap-1",
            created_at: "2024-07-01T02:00:00Z",
          },
        ],
        related_jobs: [{ id: "job-1", status: "pending" }],
        ledger_entries: [{ id: "ledger-1", type: "snapshot" }],
      });

      const response = await request(app).get("/v1/provenance/snap-1");

      expect(response.status).toBe(200);
      expect(response.body.snapshot).toMatchObject({ id: "snap-1" });
      expect(response.body.derived_snapshots[0]).toMatchObject({ id: "snap-2" });
      expect(response.body.related_jobs[0]).toMatchObject({ id: "job-1" });
    });

    it("maps missing snapshot to 404", async () => {
      mockClient.getProvenance.mockRejectedValue(
        new CoreVerificationError("Not found", 404, {
          error_code: "SNAPSHOT_NOT_FOUND",
          message: "Snapshot not found",
        })
      );

      const response = await request(app).get("/v1/provenance/unknown");

      expect(response.status).toBe(404);
      expect(response.body).toHaveProperty("error_code", "SNAPSHOT_NOT_FOUND");
    });
  });
});
