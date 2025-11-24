import { NextFunction, Request, RequestHandler, Response } from "express";
import { ZodError, ZodIssue, ZodTypeAny } from "zod";
import { ApiRouteError } from "./errorHandler";

interface RequestSchemas {
  body?: ZodTypeAny;
  query?: ZodTypeAny;
  params?: ZodTypeAny;
}

function formatZodError(error: ZodError) {
  return error.issues.map((issue: ZodIssue) => ({
    path: issue.path.join("."),
    message: issue.message,
    code: issue.code,
  }));
}

export function validateRequest(schemas: RequestSchemas): RequestHandler {
  return (req: Request, _res: Response, next: NextFunction) => {
    try {
      if (schemas.query) {
        const parsedQuery = schemas.query.parse(req.query);
        req.query = parsedQuery as any;
      }

      if (schemas.params) {
        const parsedParams = schemas.params.parse(req.params);
        req.params = parsedParams as any;
      }

      if (schemas.body) {
        const parsedBody = schemas.body.parse(req.body);
        req.body = parsedBody;
      }

      next();
    } catch (err) {
      const apiError: ApiRouteError = new Error("Invalid request");
      apiError.statusCode = 400;
      apiError.code = "INVALID_REQUEST";

      if (err instanceof ZodError) {
        apiError.details = formatZodError(err);
        apiError.message = "Request validation failed";
      }

      next(apiError);
    }
  };
}
