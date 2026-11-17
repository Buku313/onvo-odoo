# B2B payment terms: catalog and rule semantics

This is the target configurable model, not a list of features already shipped. The goal is broad composability rather than a finite dropdown of contracts. Every preset compiles to explicit obligations and a customer-readable preview. See [the product model](B2B_PAYMENT_MODEL.md) and [delivery plan](B2B_IMPLEMENTATION_PLAN.md).

Support labels: **Native** means an existing Odoo concept to reuse and validate per version; **Extension** means planned policy/orchestration work; **Conditional** requires additional provider capabilities, agreements, localization or regulated-service review. Even Native rows need ONVO end-to-end validation.

## 1. Calendar and date terms

| Family | Supported configuration target | Delivery basis |
| --- | --- | --- |
| Immediate | Due on issue, acceptance, confirmation or a specified event | Native + Extension |
| Net days | Net 7/15/30/45/60/90 or any permitted integer; merchant/customer override | Native |
| Business-day offsets | N working days with a named holiday calendar | Extension |
| End of month | EOM, EOM plus N days, last business day of month | Native where available + Extension |
| Fixed monthly date | Day 1/15/25, next month's day, N months after anchor | Native where available + Extension |
| Cutoff billing | Invoices before cutoff due this cycle; later ones move to next cycle | Extension |
| Receipt-based terms | N days after documented invoice receipt rather than issue | Extension; authenticated receipt event |
| Delivery/acceptance based | Due after shipment, delivery, service acceptance or certificate | Extension |
| Fixed date | Contractual calendar date, with amendment handling | Native + Extension |
| Grace periods | Reminder grace, collection grace and fulfillment grace separately | Extension |
| Seasonal terms | Harvest dates, campaign windows or annual budget-cycle dates | Extension |
| Deferred start | No amount due until a specified date/event; subsequent schedule follows | Extension |

Dates must define the anchor, calendar, timezone, cutoff time, day-count convention and holiday adjustment. Support following, preceding and modified-following business-day adjustment. Month-end and leap-year behavior must be explicit: preserve month end, clamp to last valid day, or move according to the selected calendar rule. Date-only accounting maturity remains a date; an expiry timestamp belongs to a collection attempt and must not change the contractual due date.

## 2. Deposits, installments and performance terms

| Family | Configuration target | Delivery basis |
| --- | --- | --- |
| Full prepayment | 100% before order confirmation or release | Native |
| Percentage deposit | Percentage of an explicit gross/net/eligible-line basis | Native + Extension for richer bases |
| Fixed deposit | Fixed amount with cap at collectible total | Extension |
| Minimum/maximum deposit | Percentage bounded by contractual floor/ceiling | Extension |
| Deposit plus balance | Deposit at acceptance; remainder on date/event/Net terms | Native + Extension |
| Multiple deposits | Reservation, mobilization, procurement and final balance | Extension |
| Equal installments | N parts with deterministic final rounding adjustment | Native where available + Extension |
| Unequal installments | Fixed/percentage tranches with a final residual | Native where available + Extension |
| Balloon/bullet | Small periodic obligations and a larger final payment | Extension |
| Step-up/step-down | Increasing or decreasing scheduled amounts | Extension |
| Milestones | Design approval, shipment, delivery, acceptance, go-live, completion | Extension |
| Progress billing | Certified percentage complete or approved work quantities | Extension |
| Partial-delivery billing | Collect/invoice only qualifying delivered quantities | Native invoicing concepts + Extension |
| Retainage | Percentage withheld from eligible progress amounts, released on event/date | Extension; accounting/localization approval |
| Warranty release | Final retention after warranty/defect-period acceptance | Extension |
| Delivery payment | Pay before dispatch, at dispatch or on delivery | Extension; collection method compatibility |
| Cash/credit mix | A defined upfront part and remaining approved credit balance | Extension |
| Per-line terms | Different eligibility, retainage or schedules by contract line | Extension |
| Purchase-order call-offs | Release amounts against a blanket agreement as orders are issued | Native commercial concepts + Extension |
| Refundable/security deposit | Separate collection, permitted application and release/refund conditions | Conditional on contract and accounting design |
| Non-refundable reservation | Explicit agreed cancellation/application rules and required disclosures | Conditional on merchant-approved legal policy |
| Consignment/sell-through | Obligation triggered by approved sale/consumption reports, with returns | Extension; inventory/contract integration |
| Documentary conditions | Pay after agreed certificates, shipping documents or PO/receipt matching | Extension; authorized evidence and approval |
| Contingent third-party payment | Pay-when-paid/pay-if-paid or another agreed external trigger, with review/long-stop conditions | Conditional; contract/legal review and verified event evidence |

Milestones need a responsible approver, evidence, approval date, allowed reversals and dispute handling. “Delivered” cannot be an arbitrary text flag supplied by the paying browser. A reversed milestone that already has collected funds creates an exception/amendment; it does not erase payment history.

## 3. Discounts, adjustments and credit arrangements

| Family | Configuration target | Delivery basis |
| --- | --- | --- |
| Early payment | Examples: 2/10 Net 30; multiple non-overlapping discount windows | Native + Extension |
| Partial early-payment discount | Apply eligible discounts to a qualifying portion | Conditional on accounting/tax support |
| Volume/contract discount | Agreed price/credit treatment, not a hidden checkout deduction | Native pricing/credit notes + Extension |
| Prompt-payment rebates | Rebate after eligibility is proven across a period | Extension |
| Credit notes | Apply existing credits to eligible receivables | Native |
| Customer advances | Apply a posted advance to future approved invoices | Native accounting + Extension orchestration |
| Prepaid balance/drawdown | Fund an account, consume it with auditable allocations | Extension; product/accounting review |
| Short-payment tolerance | Finance-approved small write-off policy with explicit thresholds | Native reconciliation concepts + Extension |
| Contractual withholding | Record documented withholding/retention separately from cash | Conditional on localization and evidence |
| Disputed deductions | Collect undisputed amounts while disputed amounts stay visible | Extension |
| Credit limits | Exposure limits by customer/entity, currency and risk policy | Native where available + Extension |
| Payment promises | Agreed promise date and amount, broken-promise tracking | Extension |
| Restructuring | Replace future schedule through a versioned approved amendment | Extension |
| Indexed adjustments | Contract-approved price/escalation/FX index, fixed source and effective date | Conditional; approved amendment/accounting treatment |
| Rebate clawback | Reverse an earned benefit through an approved adjustment when a documented condition fails | Extension; preserve original posted history |
| Moratorium/standstill | Pause collection or reminders with defined end/review date | Extension |
| Late charges/interest | Approved formula, grace, cap, compounding rule and posting process | Conditional; contract, legal and accounting review |
| Collection/payment fees | Transparent approved fee treatment with method restrictions | Conditional; provider/network and legal review |

A discount is not a write-off, a withholding claim is not a processor payment, and a pause is not debt cancellation. Model each explicitly. No fee, penalty, interest, compounding or financing rule is activated merely by selecting a template; require the merchant's approved policy and applicable capability gates.

## 4. Recurring and advanced contract models

| Family | Configuration target | Delivery basis |
| --- | --- | --- |
| Recurring invoices | Weekly/monthly/quarterly/annual, anniversary or calendar billing | Native subscription capability where installed + Extension |
| Advance/arrears billing | Invoice before or after service period | Extension orchestration |
| Usage billing | Metered quantities, approved usage, minimum commitments and overages | Extension |
| Tiered/volume rates | Graduated tiers versus all-units pricing, with explicit calculation | Native pricing where applicable + Extension |
| Proration | Mid-period start/end, upgrades, downgrades and suspended service | Extension |
| Minimum spend/true-up | Periodic reconciliation of committed versus actual usage | Extension |
| Mixed contract | Fixed retainer plus usage, milestones or expenses | Extension |
| Rollovers | Controlled unused balance/allowance rollover and expiry | Extension |
| Multi-invoice statement | One review/payment across permitted open documents | Extension |
| Split tenders | Allocate several independent receipts to one obligation | Extension; not assumed atomic across processors |
| Automatic collection | Charge a saved method under a valid mandate and retry policy | Conditional; not supported by the current connector |
| Bank debit | Mandate lifecycle, collection windows, returns and revocation | Conditional; separate supported rail required |
| Financing/installment lender | Approved lender product, disclosures and settlement model | Conditional; distinct from merchant-defined due dates |
| Escrow/holdback service | Regulated custody/release arrangements | Conditional; not ordinary ONVO hosted Checkout |
| Parent/subsidiary settlement | Group payer arrangements with intercompany restrictions | Conditional; explicit finance design |
| Non-cash setoff/barter | Approved accounting settlement with evidence; no fictitious processor receipt | Conditional; finance/localization design |
| Factoring/assignment | Track approved receivable ownership, notices and permitted beneficiary | Conditional; financing/collection agreement and provider constraints |
| Letter of credit/guarantee | Track instrument, expiry and documentary release conditions | Conditional; bank/instrument integration, not hosted card checkout |
| Cross-border/multi-currency | Invoice, collection and settlement currency rules with FX evidence | Conditional; current connector collects CRC/USD only |
| Marketplace split payouts | Beneficiary onboarding, allocation and payout controls | Conditional; separate platform scope |

Generating recurring invoices or reminder links is possible without automatic charging. The current connector has no saved-card, subscription debit, manual-capture, payout or Odoo-refund implementation. Keep those capabilities disabled until separately implemented and accepted.

## 5. Composable rule structure

Each policy consists of ordered, versioned obligation rules. A rule has:

| Dimension | Required semantics |
| --- | --- |
| Scope | Merchant company, customer agreement, contract/project, document and optional eligible lines |
| Amount basis | Gross total, untaxed eligible lines, residual, delivered value, certified work, usage or an explicit fixed value |
| Amount expression | Fixed amount, percentage, quantity × rate, tier result, bounded expression, or final remainder |
| Trigger | Document posting, accepted quote, dated event, approved milestone, period close or authorized amendment |
| Due rule | Anchor plus calendar/date adjustment; explicit timezone/calendar for timestamps |
| Preconditions | Approval, PO, credit status, signed terms, delivery evidence, minimum previous collection |
| Collection choices | Full due, full balance, approved partial, specific obligation or voluntary prepayment |
| Allocation | Target document/maturity lines, priority and credit application order |
| Adjustments | Eligible discounts/withholding/retainage with explicit precedence and approvals |
| Fulfillment | No hold, warning, confirmation hold, procurement hold, shipment hold or release condition |
| Communications | Language, document labels, reminder sequence, grace and suppression rules |
| Amendment rules | Who may change it, what requires reacceptance and what happens to existing sessions |

Use a typed declarative rule schema and whitelisted operators. Never execute merchant-supplied Python, SQL or JavaScript. Business users work with forms and previews; advanced integrations submit the same validated schema. New rule operators require versioned implementation, permissions and tests.

## 6. Deterministic calculation contract

The engine returns obligations with an explanation of each amount/date and the inputs used. Identical accepted-policy version, document revision and event history must produce identical results.

Validate before issuing documents:

- No circular triggers or dependencies; missing anchors produce a visible awaiting-event state, not an invented due date.
- No negative amounts, duplicate obligation identities, percentages above permitted bounds or installments exceeding the agreed collectible total.
- Every percentage identifies its basis. Taxes, shipping, discounts, withheld amounts and retainage cannot be included twice.
- Exactly one final-remainder rule may absorb agreed residual/rounding where needed. A partial contract schedule must explicitly identify the unallocated balance.
- Discount windows and priorities are unambiguous; late fees never compound unless a specifically approved rule permits it.
- Retroactive changes cannot rewrite posted documents or collected allocations. Generate amendments, adjustments or exceptions.
- Required payment capabilities, currencies, calendars and localization functions must be present before activation.
- Expose sample timelines, boundary dates, total due and exceptions before a merchant publishes a policy.

## 7. Worked scenarios

**Professional services:** USD 10,000 agreed collectible total, 20% at acceptance, 30% after approved delivery, 40% Net 45 after work acceptance, 10% retained until warranty release. Obligations are USD 2,000 / 3,000 / 4,000 / 1,000. An unapproved future milestone is not overdue. Down-payment/final invoice handling follows the configured accounting policy.

**Wholesale credit account:** Net 30, optional 2% discount within ten days under the merchant's approved accounting treatment, customer credit limit, and a shipping hold when exposure exceeds the approved threshold. An early-payment page recalculates eligibility at checkout creation. If a discount expires while a session is open, the attempt must follow the recorded offer-expiry policy; it cannot silently change the charged amount.

**Monthly statement:** Individual invoices remain the accounting source. The customer reviews due installments on a statement and pays a selected same-company/same-currency group. Show the allocation before payment and reconcile each invoice explicitly. An invoice paid elsewhere before checkout is removed or causes recalculation; an already submitted attempt goes through exception handling if necessary.

**Equipment with staged delivery:** A fixed reservation deposit is credited once; delivered equipment lines trigger their balance; installation requires customer sign-off; an approved retention is released later. Partial delivery cannot trigger payment for undelivered lines. A cancelled line adjusts future obligations and routes any excess deposit through credit/refund approval.

**Usage contract:** Monthly retainer in advance plus approved usage in arrears, a minimum commitment and quarterly true-up. The schedule can issue invoices and payment links first. Automatic charging remains a separately authorized capability requiring supported token/mandate behavior.

## 8. Merchant experience

Start with a preset, choose customer/default scope, fill amounts and dates, select approval/fulfillment behavior, and preview three examples: normal payment, partial/late payment, and cancellation/amendment. Present a plain-language summary alongside the generated schedule. Publishing a policy produces an immutable version; templates remain editable for future documents.

The customer sees the agreed terms, current amount due, available payment choices, discounts with expiry, scheduled future amounts and any dispute/credit status. Hide implementation details and unsupported methods. Keep an accessible non-wallet payment path on ONVO's hosted page where available.
