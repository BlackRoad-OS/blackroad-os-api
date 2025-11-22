import { Request, Response, Router } from "express";
import {
  CoreAssessment,
  CoreProvenanceGraph,
  CoreSnapshot,
  CoreTruthState,
  CoreVerificationJob,
  CoreVerificationError,
  VerificationServiceClient,
  VerificationJobPayload,
  coreVerificationClient,
} from "../../lib/coreVerificationClient";

const sanitizeAgentId = (agentId?: string): string | undefined => {
  if (!agentId) return undefined;
  const parts = agentId.split(":");
  return parts.length > 1 ? parts.slice(-1)[0] : agentId;
};

const mapAssessments = (assessments?: CoreAssessment[]) => {
  const items = (assessments || []).map((assessment) => ({
    agent_id: sanitizeAgentId(assessment.agent_id),
    verdict: assessment.verdict,
    confidence: assessment.confidence ?? null,
    created_at: assessment.created_at,
    evidence_uris: assessment.evidence_uris || [],
  }));

  return {
    count: items.length,
    items,
  };
};

const mapSnapshot = (snapshot?: CoreSnapshot) => {
  if (!snapshot) return null;
  return {
    id: snapshot.id,
    source_uri: snapshot.source_uri,
    author_id: snapshot.author_id,
    parent_snapshot_id: snapshot.parent_snapshot_id,
    created_at: snapshot.created_at,
    hash: snapshot.ps_sha_infinity,
  };
};

const mapTruthState = (truth?: CoreTruthState | null) => {
  if (!truth) return null;
  return {
    claim_hash: truth.claim_hash,
    status: truth.status,
    aggregate_confidence: truth.aggregate_confidence ?? null,
    job_ids: truth.job_ids || [],
    minority_reports: truth.minority_reports || [],
    last_updated: truth.last_updated,
    policy_id: truth.policy_id,
    domain: truth.domain,
  };
};

const mapJobSummary = (job: CoreVerificationJob) => ({
  id: job.job_id,
  snapshot_id: job.snapshot_id || job.snapshot?.id,
  claim_hash: job.claim_hash || job.truth_state?.claim_hash || null,
  status: job.status,
  created_at: job.created_at,
  policy_id: job.policy_id,
  domain: job.domain,
});

const mapProvenance = (graph: CoreProvenanceGraph) => ({
  snapshot: mapSnapshot(graph.snapshot),
  parent_snapshot: mapSnapshot(graph.parent_snapshot || undefined),
  derived_snapshots: (graph.derived_snapshots || []).map(mapSnapshot),
  related_jobs: graph.related_jobs || [],
  ledger_entries: graph.ledger_entries || [],
});

const buildValidationError = (message: string, details?: Record<string, any>) => ({
  error_code: "INVALID_REQUEST",
  message,
  details,
});

const handleCoreError = (res: Response, error: unknown) => {
  if (error instanceof CoreVerificationError) {
    const status = error.status || 502;
    const payload =
      error.data && typeof error.data === "object"
        ? error.data
        : {
            error_code:
              status === 404
                ? "VERIFICATION_RESOURCE_NOT_FOUND"
                : "CORE_VERIFICATION_ERROR",
            message: error.message,
          };
    return res.status(status).json(payload);
  }

  console.error(error);
  return res.status(502).json({
    error_code: "CORE_VERIFICATION_ERROR",
    message: "Core verification service unavailable",
  });
};

const parseVerifyRequest = (body: any): VerificationJobPayload | null => {
  if (!body || typeof body.text !== "string" || !body.text.trim()) {
    return null;
  }

  const payload: VerificationJobPayload = {
    text: body.text,
  };

  const optionalFields: (keyof VerificationJobPayload)[] = [
    "source_uri",
    "author_id",
    "claim_hash",
    "domain",
    "policy_id",
    "requested_by",
  ];

  optionalFields.forEach((field) => {
    const value = body[field];
    if (value !== undefined) {
      payload[field] = value;
    }
  });

  return payload;
};

export const createVerificationRouter = (
  client: VerificationServiceClient = coreVerificationClient
) => {
  const router = Router();

  router.post("/verify", async (req: Request, res: Response) => {
    const payload = parseVerifyRequest(req.body);

    if (!payload) {
      return res
        .status(400)
        .json(buildValidationError("`text` is required for verification"));
    }

    try {
      const job = await client.createVerificationJob(payload);
      return res.status(202).json({
        job: mapJobSummary(job),
        snapshot: mapSnapshot(job.snapshot) || null,
        truth_state: mapTruthState(job.truth_state),
      });
    } catch (error) {
      return handleCoreError(res, error);
    }
  });

  router.get("/verify/jobs/:jobId", async (req: Request, res: Response) => {
    const { jobId } = req.params;
    if (!jobId) {
      return res
        .status(400)
        .json(buildValidationError("`job_id` must be provided"));
    }

    try {
      const job = await client.getVerificationJob(jobId);
      return res.json({
        job: mapJobSummary(job),
        snapshot: mapSnapshot(job.snapshot) || null,
        assessments: mapAssessments(job.assessments),
        truth_state: mapTruthState(job.truth_state),
      });
    } catch (error) {
      return handleCoreError(res, error);
    }
  });

  router.get("/truth/:claimHash", async (req: Request, res: Response) => {
    const { claimHash } = req.params;
    if (!claimHash) {
      return res
        .status(400)
        .json(buildValidationError("`claim_hash` must be provided"));
    }

    try {
      const truth = await client.getTruthState(claimHash);
      return res.json(mapTruthState(truth));
    } catch (error) {
      return handleCoreError(res, error);
    }
  });

  router.get("/provenance/:snapshotId", async (req: Request, res: Response) => {
    const { snapshotId } = req.params;
    if (!snapshotId) {
      return res
        .status(400)
        .json(buildValidationError("`snapshot_id` must be provided"));
    }

    try {
      const provenance = await client.getProvenance(snapshotId);
      return res.json(mapProvenance(provenance));
    } catch (error) {
      return handleCoreError(res, error);
    }
  });

  return router;
};

const verificationRouter = createVerificationRouter();

export default verificationRouter;
