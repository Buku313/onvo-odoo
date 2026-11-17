# B2B implementation and acceptance plan

This is an implementation-ready proposal for the [B2B payment model](B2B_PAYMENT_MODEL.md) and [comprehensive term catalog](B2B_TERMS_CATALOG.md). It does not enable new commercial policies, send customer communications or modify invoices today.

## 1. Delivery architecture

Keep `payment_onvo` as the reusable payment gateway. Add optional B2B modules so a simple checkout merchant does not have to install a contract-billing system.

| Proposed module | Responsibility | Dependencies/capability |
| --- | --- | --- |
| `onvo_b2b` | Invoice/quote portal actions, policy selection, payment readiness and accounting linkage | `payment_onvo`, `sale`, `account_payment`; reuse their portal/mail support |
| `onvo_b2b_terms` | Policy versions, obligation rules, calendars, milestone evidence and amendments | B2B foundation plus confirmed native accounting capabilities |
| `onvo_b2b_collections` | Reminders, promises, disputes, credit holds, approvals and exception work queues | Terms and accounting integration |
| `onvo_b2b_settlement` | Settlement import/API adapters, fees, matching and reconciliation exceptions | Verified provider/bank data sources |
| Future capability modules | Refund automation, mandates, recurring collection, usage integrations or embedded wallets | Individually verified provider capabilities and merchant authorization |

Names are proposed. Final module boundaries should follow a native-feature audit; do not duplicate Odoo Subscription, project billing, accounting follow-up or localization features when an installed edition already supplies them.

## 2. Data ownership

| Object | Implementation direction |
| --- | --- |
| Customer, order, invoice, currency and company | Existing Odoo models remain authoritative. |
| Contract/payment terms | Reuse `account.payment.term`, quote prepayment and existing agreement fields where sufficient. |
| Collection policy/version | Add only configuration, immutable revisions, approval scope and rule definitions not represented natively. |
| Collection obligation | A commercial schedule/projection linked to its source document, revision and relevant invoice maturity lines. Its outstanding accounting amount is derived from Odoo, not maintained as a second receivables ledger. |
| Collection request/link | Reuse native portal/payment links first. Add a durable wrapper only for required revision, expiry, delegated payer or multi-obligation semantics that native links cannot enforce. |
| Payment attempt | Extend `payment.transaction`; preserve core order/invoice relationships and add the minimum accepted-amount/policy/request metadata needed for safe reconciliation. |
| Accounting receipt/allocation | Existing `account.payment` and reconciliation records. Planned allocation is not itself an accounting payment. |
| Provider-event inbox | Deduplicated verified events, processing status and minimal redacted evidence. |
| Outbound operation | Durable command/outbox state for session creation, expiry and future financial operations, including unknown outcomes. |
| Settlement evidence | Import batches, provider references, bank matches and finance exceptions; retain source checksums/audit history. |

An obligation identity must be deterministic for a given accepted document/policy revision. Generate new revisions or compensating adjustments instead of mutating previously settled obligations. Terms operators are versioned, typed and whitelisted. Store every calculation's source facts and human-readable explanation.

## 3. Payment execution contract

1. Resolve the link's company, document and limited access capability. Check role/portal ownership/delegation, current revision, supported currency and collection eligibility.
2. Compute current due/residual/discount/credit choices on the server and show them to the customer. Required acceptance and purchase-order information precede authorization to collect.
3. On submit, lock the collection decision, recheck the accepted revision and balance, and persist a durable attempt/reservation before making the remote request. Reuse an eligible pending attempt.
4. Create ONVO Checkout with an exact immutable amount/currency snapshot and minimal attribution metadata. Keep API keys server-side. If the outcome is ambiguous, mark it unknown and prevent blind replacement sessions.
5. Redirect only to validated ONVO checkout hosts. Hosted Apple Pay remains an account/device capability; it does not require a new B2B payment protocol.
6. Verify webhook authenticity and environment, deduplicate, fetch authoritative provider state, and compare identity, amount, currency and account/document context before recording success.
7. Apply native Odoo payment post-processing and reconciliation idempotently. Confirm orders or release holds only when their full policy conditions are satisfied.
8. Show an accurate customer state: received, processing, partially paid, satisfied, failed or exception. Send a receipt/notification once through the approved merchant workflow.
9. Handle abandoned/expired sessions, background reconciliation, changed documents, bank payments and excess collections through explicit recovery paths.

No client request may arbitrarily select a different company, debtor, invoice, currency, discount or amount. No provider callback may choose an unrelated accounting document. Partial refunds, write-offs, credit reallocations and hold overrides require separate authorization and audit.

## 4. Phase 0 — native-feature audit and financial proof

**Goal:** prove the existing Odoo/ONVO integration can link a real quote/invoice payment to the correct financial records before adding broad rules.

- Inventory quote online-confirmation, prepayment, payment links, portal templates, invoice QR options, installment/discount computation and journal configuration in Odoo 17, 18, 19 and 20.
- Odoo 17 already has quote prepayment and payment-link amount logic. Odoo 20 has installment-aware invoice link values and invoice QR generation. Treat API/template differences as adapters, not copied implementations.
- Validate `_post_process`, accounting payment creation and reconciliation after webhook-only success, browser return and scheduled recovery. The connector's current payment-only CI does not prove invoice reconciliation.
- Confirm company journals, payment-method lines, outstanding accounts, fiscal localization and automatic-invoice settings with the merchant's finance owner.
- Resolve remote-create ambiguity before treating the gateway as production-ready for repeated B2B link clicks. Obtain a documented idempotency/recovery contract from ONVO if available; otherwise keep unknown-outcome attempts quarantined for recovery.
- Define sandbox and live activation gates. Never test new policy logic against a production customer's posted invoice.

Exit: signed-off capability matrix and passing end-to-end quote/invoice/accounting proof for each supported version and intended edition. No claim of Enterprise certification from Community tests alone.

## 5. Phase 1 — complete basic collections

Deliver native-based buttons for posted customer invoices and eligible quotations, matching email/portal/PDF language and branding, secure current-balance links, quote acceptance/prepayment and full-residual invoice payment. Include partial-payment behavior only where policy and version support have been validated.

Add a self-service merchant readiness screen: company/currency, test/live keys, webhook health, active payment method, payment journal, default quote/invoice policy, portal/public HTTPS URL and supported wallets. Show evidence-based status, not optimistic checkboxes. Provide isolated sample quote/invoice tests with no customer emails or fiscal issuance outside the configured test environment.

Exit: full, deposit, failed, repeated, expired and already-paid document flows work; payments reconcile once; no duplicate fulfillment; old links cannot collect an obsolete amount; all required financial exceptions are visible.

## 6. Phase 2 — policy engine and advanced terms

Implement merchant defaults, customer agreements, authorized document overrides, immutable policy versions, native term adapters, deterministic schedules, date/calendar primitives, fixed/percentage/remainder amounts, deposits, installment options, milestone evidence, retainage and approved discounts.

Ship presets and a preview/explanation UI before exposing advanced rule composition. Add amendment handling and simulations for partial payment, late payment, cancellation, holiday/leap-day boundaries and changed totals. Introduce per-line and progressive-delivery terms only after the basic allocation model is proven.

Exit: published policies pass validation, accepted documents keep their agreed versions, generated obligations reconcile to the agreed total, amendments do not rewrite posted history, and buyer explanations match calculated dates/amounts.

## 7. Phase 3 — finance operations and recurring billing

Add credit limits/holds, payment promises, dispute/short-payment handling, configurable reminder sequences, customer-credit allocations and a consolidated exceptions dashboard. Support statement selection across eligible same-debtor/company/currency documents.

Integrate installed subscription/project/usage capabilities for recurring invoice generation, minimum commitments, proration and true-ups. Recurring invoice issuance and payment-link reminders can precede automatic charging. Automatic debits need a separately implemented mandate/token lifecycle, consent, cancellation, retry and revocation model.

Exit: finance users can resolve exceptions without editing transaction states manually; communication suppression and deduplication work; statement allocation is deterministic; recurring terms do not imply unsupported charging behavior.

## 8. Phase 4 — provider and settlement automation

Implement only after confirming current ONVO contracts/APIs: partial/full refund synchronization, dispute events, payout/fee evidence, settlement imports/APIs, and any saved-method or bank-debit collection capability. Apply approval thresholds, idempotent operation tracking and audit to money-moving operations.

Embedded Apple Pay is an optional later frontend capability, not a dependency for invoice/quote collection. Financing, escrow, intercompany netting and marketplace split payouts are separate product decisions with explicit provider, financial and legal sign-off.

## 9. Acceptance matrix

Run applicable cases on Odoo 17–20, both CRC/USD, and each enabled merchant/company configuration.

| Area | Required scenarios |
| --- | --- |
| Quotes | Full prepay; percentage/fixed deposit; signature before payment; approved credit; expired/revised quote; partial delivery; minimum threshold; cancelled order after session creation. |
| Invoices | Full residual; installment; approved partial; already-paid invoice; credit note; draft blocked; cancelled/reversed invoice; early discount eligible/expired; amount changed elsewhere. |
| Timing | EOM; cutoff; business holiday; leap day; month-day 31; timezone boundary; missing trigger; retrospective amendment; warranty-release event. |
| Allocation | Multiple receipts; same invoice paid via bank and ONVO; partial credit; withholding claim; overpayment; multi-invoice statement; mixed company/currency rejected. |
| Reliability | Double click; parallel tabs; replayed webhook; out-of-order event; expired signature; duplicate payment; remote timeout before/after creation; DB rollback; restart; webhook-only success; missing browser return. |
| Accounting | Correct debtor/company/journal/currency; native post-processing; exact allocation; reconciliation only once; fees separate from gross receipts; partial refund; credit-note matching; unallocated cash exception. |
| Access | Forwarded scoped link; guessed/tampered token; wrong customer; unauthorized policy edit; unauthorized refund/hold override; multi-company isolation; exposed secret checks; invoice details outside scope blocked. |
| Customer experience | English/Spanish email and PDF; mobile portal; QR; accessible fallback; Apple Wallet available/unavailable; cancellation; failure; accurate pending/success/exception messages. |
| Operations | Reminder suppression; duplicate notification prevention; broken promise; dispute pause; hold approval; immutable audit; settlement mismatch; aged unknown outcome. |

## 10. Rollout and measurable completion

Start with an internal sandbox company, then a small merchant pilot with explicitly selected policy profiles. Keep advanced features disabled until their tests and merchant approvals pass. Use per-company feature controls and reversible UI/template deployments. Rollback must preserve financial/audit history and continue reconciliation for payments already in flight.

Track merchant-local metrics: collection-link conversion, time to verified receipt, stale/unknown attempts, unmatched receipts, overdue obligations, reconciliation exceptions and manual interventions. Define service targets from measured provider behavior; do not promise real-time bank settlement based on checkout success.

Completion requires an auditable path from every confirmed processor receipt to an accounting allocation or an owned exception, no duplicate accounting/fulfillment in the tested retry scenarios, and customer-visible balances that agree with Odoo. A large preset catalog alone is not completion.

## 11. Decisions and assumptions

- Confirmed by owner: configurable deposits and payment terms per merchant/customer; a comprehensive extensible B2B model.
- Recommended: native Odoo commercial/accounting features first, secure portal links, one currency/company per collection, configurable but approved partial payments, and gateway capability gates.
- Still to decide before implementation: first pilot industries, mandatory PO/acceptance rules, permitted fee/interest policies, installed editions/localizations, automatic invoicing defaults, settlement data source and demand for recurring automatic debit.
- No need to block this design on those choices. They become configuration and rollout inputs; unsupported capabilities remain off.
