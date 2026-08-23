# Local Data-Center Alignment Policy Playbook

**Purpose.** This playbook turns the Alignment Theorem’s data-center social-contract mathematics into tools that a city, town, county, borough, township, municipal utility, or regional authority can use now.

It is a policy-design template, not jurisdiction-specific legal advice. State enabling law, utility regulation, tax law, public-finance restrictions, constitutional limits, and federal preemption differ. Local counsel should translate each recommendation into the lawful instrument available in the jurisdiction: zoning ordinance, special-use permit, development agreement, host-community agreement, franchise agreement, public land lease, utility tariff intervention, tax-incentive agreement, performance bond, mitigation fee, or trust agreement.

## Governing principle

A local government should not ask only whether a data center creates jobs, tax revenue, or aggregate economic activity. It should ask whether the project can satisfy all senior physical and household obligations before any public benefit is advertised.

For one settlement period, define:

\[
R=(G-C)_+,
\]

where \(G\) is authenticated gross public rent or legally committed project payment and \(C\) is the sum of senior claims:

\[
C=C_{grid}+C_{reliability}+C_{water/env}+C_{roads/public\ safety}+C_{decommission}+C_{admin/audit}.
\]

For household \(i\):

\[
d_i=(L_i-B_i)_+,
\qquad
h_i=\max\{m,d_i\},
\]

where \(L_i\) is an authenticated project-caused loss, \(B_i\) is a direct benefit that actually reaches the household, and \(m\) is a universal resident benefit floor. The least protective household reserve is:

\[
H(m)=\sum_i h_i
    =nm+\sum_i(d_i-m)_+.
\]

The project’s public-benefit promise is funded only when:

\[
G\ge C+H(m).
\]

A separately promised compute floor \(c\) for \(n\) eligible households also requires a separately authenticated compute reserve:

\[
Q\ge nc.
\]

Compute is not cash and must not be counted as compensation for utility bills, property loss, health burdens, displacement, or other cash-equivalent harms unless a conservative conversion rule is independently justified.

---

# The local policy package

## 1. Make large data centers a conditional use, not a by-right use

Require a special exception, conditional-use permit, planned-development approval, or equivalent legislative approval for every facility above locally selected thresholds for peak load, floor area, acreage, water demand, backup generation, or expansion.

The approval should attach to a defined project identity, site, peak megawatt envelope, water envelope, noise envelope, and construction schedule. A sale, end-user change, material redesign, or expansion above the approved envelope should trigger a new review.

**Why:** A project with rapidly changing load, ownership, and infrastructure demands cannot be adequately governed by a one-time ministerial permit. Loudoun County moved data centers in several industrial districts from by-right treatment to special-exception review in 2025.

## 2. Ban secret siting bargains and require an early public project data sheet

Before the first discretionary hearing, require disclosure of at least:

- beneficial owner, developer, operator, and known end users;
- parcel map, campus acreage, building area, height, phasing, and construction schedule;
- requested peak electric demand, expected annual consumption, load ramp, and interconnection status;
- proposed generation, storage, substations, transmission, distribution, and backup power;
- water source, maximum day demand, annual withdrawal and consumption, wastewater, and drought plan;
- expected PUE and WUE, cooling design, heat-reuse plan, and equipment refresh assumptions;
- generator type, fuel storage, emissions, testing schedule, and emergency operations;
- baseline and modeled operational noise, including low-frequency and steady tonal noise;
- expected permanent jobs, construction jobs, local procurement, tax assumptions, and requested incentives;
- requested confidentiality and the exact legal basis for each redaction.

Do not permit a nondisclosure agreement to prevent elected officials or the public from learning the project facts necessary for land-use, fiscal, utility, environmental, or public-safety decisions.

**Why:** GAO reports that key AI energy and water details remain poorly disclosed. Pennsylvania’s 2026 GRID framework requires footprint reporting and early community engagement.

## 3. Adopt “growth pays for growth” as a binding cost-allocation rule

Require the project—not existing households and small businesses—to fund every reasonably attributable incremental cost, including:

- interconnection studies and facilities;
- generation, transmission, substations, feeders, distribution, and network upgrades;
- capacity, ancillary service, congestion, balancing, and stranded-asset exposure;
- water and sewer upgrades;
- roads, traffic controls, fire and emergency response capacity;
- independent technical, fiscal, environmental, acoustic, security, and legal review;
- decommissioning and site restoration.

The local government should intervene before the state utility commission or relevant tariff authority when needed, because zoning approval alone cannot determine retail or transmission cost allocation.

Use minimum-demand charges, take-or-pay commitments, security deposits, letters of credit, parent guarantees, and exit fees where legally available to prevent speculative reservations or early departure from shifting sunk costs to ratepayers.

**Why:** FERC’s June 18, 2026 large-load orders explicitly focus on preventing cost shifting and increasing transmission-cost transparency. Pennsylvania’s GRID requirements likewise require developers to pay the full cost of incremental capacity and grid infrastructure.

## 4. Put physical and public-safety vetoes ahead of money

Some burdens should not be purchasable. The permit should contain hard operating envelopes for:

- peak grid draw and ramp rate;
- emergency curtailment response;
- water withdrawal and consumptive use under normal and drought conditions;
- steady-state, low-frequency, and tonal noise at property and residential receptors;
- generator hours, testing windows, emissions, and fuel storage;
- lighting, setbacks, screening, building height, and viewsheds;
- wetlands, high-quality waters, habitat corridors, historic resources, and heat discharge;
- fire, battery, chemical, cybersecurity, and emergency-response requirements.

A missing or failed measurement should not be interpreted as compliance. Exceeding a hard envelope should trigger automatic escalation: notice, cure period where appropriate, monetary penalty, load curtailment, permit suspension, or revocation.

**Why:** Virginia localities have adopted special-exception review, setbacks, noise studies, soundproofing, generator-hour limits, and specific enforcement for steady tonal noise associated with industrial equipment and data centers.

## 5. Require funded performance, remediation, and decommissioning security before operation

Before energization, require independently valued and periodically refreshed security sufficient to cover:

- unfinished public infrastructure;
- nonperformance of community-benefit commitments;
- environmental remediation;
- emergency response and temporary service arrangements;
- equipment removal and site restoration;
- unpaid monitoring, audit, and enforcement expenses.

The security should be bankruptcy-remote to the extent lawful and should not rely solely on the operating subsidiary’s future solvency. Acceptable forms may include cash escrow, letter of credit, surety bond, parent guarantee, or a layered package.

## 6. Negotiate a residual-rent community agreement, not a headline donation

The community agreement should contain three layers:

1. **Nonavoidable capacity or concession payment.** A fixed payment tied to land, permit, capacity reservation, public infrastructure, or a public lease; this prevents a zero-accounting-profit strategy from eliminating the public floor.
2. **Full senior-cost recovery.** All project-attributable grid, environmental, public-service, and decommissioning obligations are paid before a dividend is calculated.
3. **Variable residual share.** A defined share of audited residual rent, revenue above a threshold, or another legally measurable surplus indicator.

Do not base the entire bargain on a share of operator accounting profit. Profit can be zero because of competition, transfer pricing, affiliate fees, depreciation choices, leverage, or genuine business conditions even while the community continues to bear fixed burdens.

The agreement should define consolidated affiliates, arm’s-length pricing, audit rights, anti-avoidance rules, dispute procedures, and a conservative interim escrow during disputes.

## 7. Create a universal resident benefit plus targeted no-harm top-ups

After senior claims are funded, establish a broad resident floor \(m\), delivered through whatever vehicle state law permits, such as:

- utility bill credits;
- property-tax or rent rebates;
- a resident dividend from a public trust;
- local energy-assistance credits;
- universal public-service credits;
- community-owned infrastructure or household resilience benefits with a clearly measured household value.

Then provide targeted top-ups where authenticated project-caused deficits exceed the universal floor:

\[
h_i=\max\{m,(L_i-B_i)_+\}.
\]

This structure is both populist and efficient: everyone shares in the bargain, while the households bearing the greatest modeled loss are not sacrificed to the average.

A uniform payment alone is insufficient. A project can fully fund a small universal benefit and still leave a highly affected household worse off.

## 8. Keep a distinct host-zone share

Households and public institutions closest to substations, transmission corridors, generator yards, cooling infrastructure, water withdrawals, or construction routes may bear burdens that a jurisdiction-wide average conceals.

Create a geographically defined host-zone account for:

- verified property and quality-of-life impacts;
- home insulation, acoustic mitigation, landscaping, or relocation assistance;
- neighborhood resilience and backup power;
- emergency services and road repair;
- conservation and watershed projects;
- locally chosen long-horizon investments.

The host-zone share is additional to make-whole compensation. Payment for harm is not the same as participation in upside.

## 9. Require verifiable load flexibility and emergency curtailment

Condition approval on a tested flexible-load plan that states:

- how much load can be reduced;
- how quickly reduction begins;
- minimum duration;
- rebound limits;
- on-site generation or storage used during curtailment;
- prohibited fuel or emissions outcomes;
- consequences for nonperformance.

Require periodic drills and public aggregate performance receipts. Do not award flexibility credit for an unenforced promise.

This can turn a data center from an inflexible peak burden into a partially dispatchable partner, but the credit should reflect verified performance, not nameplate claims.

## 10. Make tax incentives conditional, recurring, and clawback-enabled

No incentive should vest permanently at groundbreaking. Tie each year’s benefit to current compliance with:

- cost-recovery and tariff obligations;
- jobs, wage, apprenticeship, and local-procurement commitments;
- public reporting;
- energy and water envelopes;
- community-benefit payments;
- audit cooperation;
- operational milestones.

Allow suspension, proportional clawback, or full recapture for material breach. Publish the gross incentive, present value, performance received, and net fiscal result.

## 11. Establish an independent measurement, audit, and public-challenge system

Require independent or regulator-readable meters for electricity, water, backup generation, emissions, noise, and curtailment performance. Publish a public dashboard with signed epoch receipts and machine-readable data, subject only to narrow lawful redactions.

Residents should have a defined process to challenge:

- missing reports;
- stale evidence;
- meter anomalies;
- noise or water exceedances;
- affiliate transactions;
- underfunded reserves;
- duplicate or misdirected benefit claims.

A contested amount should remain in escrow until resolution. Auditors should rotate, disclose conflicts, and face liability or bond forfeiture for reckless attestation.

## 12. Use staged permits and anti-speculation milestones

A large requested load can alter regional planning even when the project is never completed. Use milestone dates for land control, financing, interconnection deposits, construction, equipment delivery, energization, and minimum utilization.

Unused capacity rights should expire or incur escalating reservation charges. Materially inflated load forecasts, dormant permits, or serial ownership transfers should trigger review.

## 13. Require periodic constitutional review, not ad hoc renegotiation

Every approval should include:

- an annual operational review;
- a major review at a fixed interval, such as five years;
- automatic reopening for material expansion or ownership/end-user change;
- emergency amendment procedures;
- a rule that amendments may not silently weaken senior claims, hard physical limits, auditability, or funded household floors.

The community should be able to improve the rules without destroying the guarantees that induced consent.

## 14. Form a regional minimum-standard compact

Localities should coordinate on minimum disclosure, cost recovery, water, noise, bond, audit, and benefit standards. Otherwise developers can create a race to the bottom by threatening to move one jurisdiction away while using the same regional grid and watershed.

A compact can preserve local control over siting while preventing communities from externalizing costs onto neighbors.

---

# A Tau-ready local approval structure

The existing Alignment Theorem research packet maps a local approval into ten authenticated facts:

1. `policy_root_ok`
2. `project_identity_authenticated`
3. `local_consent_authenticated`
4. `incremental_energy_costs_reserved`
5. `reliability_curtailment_plan_ok`
6. `water_emissions_land_limits_ok`
7. `decommissioning_bond_funded`
8. `no_harm_compensation_funded`
9. `universal_dividend_compute_floor_funded`
10. `public_audit_receipt_current`

The Tau gate admits the project only when all ten are true. The complete 1,024-row packet accepts only the all-true row. A false or missing fact rejects.

This gate should control a bounded action—permit activation, one settlement epoch, one benefit distribution, one load-envelope renewal—not claim that the entire real-world project is eternally safe.

## Evidence adapters

Tau should consume signed facts produced by separate, reviewable adapters:

| Fact | Possible local evidence source |
|---|---|
| Policy root | clerk-certified ordinance/development-agreement digest |
| Project identity | beneficial-ownership filing and permit identity |
| Local consent | final approval record after required hearings and appeals |
| Energy costs reserved | utility/regulator filing, security agreement, and paid invoices |
| Reliability plan | system-operator/utility study and successful curtailment drill |
| Environmental limits | permit data, independent meters, inspections, and laboratory reports |
| Decommissioning bond | custodian-signed balance and enforceability opinion |
| No-harm reserve | actuarial/economic assessment and escrow receipt |
| Cash/compute floor | cash custodian plus metered compute-capacity receipt |
| Audit current | independent signed epoch report with no unresolved blocking exception |

Tau does not make any of these facts true. It makes the policy relation explicit: **no evidence, no admission; failed obligation, no settlement.**

---

# Model local resolution

A local governing body can begin with a resolution substantially like this:

> **Resolved**, that no high-energy-use data-center project shall receive discretionary land-use approval, public land, tax incentive, development support, or local utility commitment unless the governing body finds, on a public record, that: (1) the project identity and resource footprint are disclosed; (2) project-attributable infrastructure and public-service costs are fully funded without material cost shifting; (3) enforceable grid, water, noise, emissions, safety, and decommissioning protections are in place; (4) the project has entered a transparent community-benefit agreement containing a broad resident benefit and targeted mitigation for disproportionately affected households; (5) all monetary and compute promises are backed by separate authenticated reserves; and (6) continuing approval is conditioned on public reporting, independent audit, and enforceable remedies.

> **Further resolved**, that staff shall prepare a Tau-ready machine-readable policy schedule identifying each required fact, its authorized evidence source, expiration rule, appeal status, and the action that must fail closed when the fact is false, missing, stale, or disputed.

---

# Recommended adoption sequence

## First 30 days

- place a temporary pause on new by-right approvals where lawful;
- initiate a zoning text amendment or comprehensive-plan review;
- require a standard project data sheet;
- retain independent grid, water, fiscal, acoustic, and legal advisers funded by applicant deposits;
- inventory existing applications and grandfathering exposure.

## Days 31–90

- adopt conditional-use thresholds and interim hard envelopes;
- publish a model community-benefit term sheet;
- establish performance-bond and decommissioning-security methods;
- intervene in relevant utility or tariff proceedings;
- begin a regional compact with neighboring jurisdictions.

## Days 91–180

- adopt the full ordinance and enforcement schedule;
- create the public dashboard, complaint, appeal, and challenge process;
- select the lawful resident-benefit vehicle;
- publish the Tau-ready evidence schema and policy-root process;
- run shadow settlements without moving value.

## Pilot phase

For at least one year, run the Tau policy in shadow mode. Compare every machine decision with the legal approval record, audit exceptions, meter data, and human appeal outcomes. No production settlement claim should be made until the exact Tau interpreter, source pin, semantic packet, adapters, custody layer, and amendment process are independently replayed and reviewed.

---

# What communities should not promise

Local officials should not promise that:

- AGI automatically creates permanent monopoly profits;
- intelligence doubling automatically produces lower household prices;
- a profit share alone funds a durable dividend;
- compute credits replace money;
- every project can satisfy both community obligations and investor participation;
- passing a finite scenario model bounds all future losses;
- a Tau gate authenticates meters, identities, consent, or physical reality;
- the current Tau alpha/testnet is production-ready for public funds.

The theorem is strongest when it is used as a refusal rule: **when the authenticated residual does not fund the senior claims and household floor, government must not advertise the bargain as beneficial or solvent.**

---

# Primary public precedents and sources

- Lawrence Berkeley National Laboratory, *United States Data Center Energy Usage Report: 2025 Update*: https://datacenters.lbl.gov/publications/united-states-data-center-energy-2025
- FERC, June 18, 2026 large-load orders: https://www.ferc.gov/news-events/news/ferc-launches-aggressive-targeted-action-speed-large-load-integration
- Pennsylvania GRID Standards and local-government toolkit: https://www.pa.gov/governor/newsroom/2026-press-releases/gov-shapiro-releases-full-grid-standards-to-protect-pennsylvania
- Pennsylvania Executive Order 2026-05 summary: https://www.pa.gov/governor/newsroom/2026-press-releases/governor-shapiro-signs-executive-order-on-data-center-developmen
- U.S. GAO, *Generative AI’s Environmental and Human Effects*: https://www.gao.gov/products/gao-25-107172
- Loudoun County data-center standards and special-exception process: https://www.loudoun.gov/datacenterstandards
- Prince William County steady tonal noise enforcement: https://www.pwcva.gov/department/public-works/steady-tonal-noise
- Tau Language official repository: https://github.com/IDNI/tau-lang
