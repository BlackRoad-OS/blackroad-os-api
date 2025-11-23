/**
 * Snapshot of key cash and revenue metrics produced by finance agents.
 * Values follow GAAP concepts but are advisory; see source system for audited numbers.
 */
export interface FinanceSummary {
  /** ISO currency code for the represented values. */
  currency: string;
  /** Current cash balance available. */
  cashBalance: number;
  /** Average monthly burn, used to calculate runway. */
  monthlyBurnRate: number;
  /** Estimated runway in months based on current burn. */
  runwayMonths: number;
  /** Monthly recurring revenue if available. */
  mrr?: number;
  /** Annual recurring revenue if available. */
  arr?: number;
  /** ISO timestamp when this summary was generated. */
  generatedAt: string;
}

/**
 * A bucket of projected cash movement for a date range.
 */
export interface CashForecastBucket {
  /** Inclusive start date for the bucket. */
  startDate: string;
  /** Inclusive end date for the bucket. */
  endDate: string;
  /** Net change in cash during the period. */
  netChange: number;
  /** Expected ending balance after applying the net change. */
  endingBalance: number;
}

/**
 * Cash forecast composed of sequential buckets.
 */
export interface CashForecast {
  /** ISO currency code for all buckets. */
  currency: string;
  /** Ordered list of forecast buckets. */
  buckets: CashForecastBucket[];
  /** ISO timestamp when the forecast was generated. */
  generatedAt: string;
}

/**
 * A single line item within a GAAP statement section.
 */
export interface StatementLineItem {
  /** Name of the account or classification. */
  account: string;
  /** Human readable label for the line item. */
  label: string;
  /** Monetary amount for the item. */
  amount: number;
}

/**
 * GAAP-inspired income statement.
 */
export interface IncomeStatement {
  /** Reporting period identifier (e.g. YYYY-MM or YYYY-Qn). */
  period: string;
  /** ISO currency code for the statement. */
  currency: string;
  /** Revenue line items. */
  revenue: StatementLineItem[];
  /** Cost of goods sold line items. */
  cogs: StatementLineItem[];
  /** Operating expense line items. */
  operatingExpenses: StatementLineItem[];
  /** Other income or expense adjustments. */
  otherIncomeExpenses: StatementLineItem[];
  /** Net income for the period. */
  netIncome: number;
}

/**
 * GAAP-inspired balance sheet representation.
 */
export interface BalanceSheet {
  /** Reporting period identifier. */
  period: string;
  /** ISO currency code for the statement. */
  currency: string;
  /** Asset line items. */
  assets: StatementLineItem[];
  /** Liability line items. */
  liabilities: StatementLineItem[];
  /** Equity line items. */
  equity: StatementLineItem[];
}

/**
 * GAAP-inspired cash flow statement representation.
 */
export interface CashFlowStatement {
  /** Reporting period identifier. */
  period: string;
  /** ISO currency code for the statement. */
  currency: string;
  /** Cash from operating activities. */
  operatingActivities: StatementLineItem[];
  /** Cash from investing activities. */
  investingActivities: StatementLineItem[];
  /** Cash from financing activities. */
  financingActivities: StatementLineItem[];
  /** Net change in cash across all activities. */
  netChangeInCash: number;
}

/**
 * Collection of GAAP-like statements for a given period.
 */
export interface FinancialStatements {
  /** Period identifier matching the source system (YYYY-MM or YYYY-Qn). */
  period: string;
  /** Income statement for the period. */
  incomeStatement: IncomeStatement;
  /** Balance sheet for the period. */
  balanceSheet: BalanceSheet;
  /** Cash flow statement for the period. */
  cashFlowStatement: CashFlowStatement;
}
