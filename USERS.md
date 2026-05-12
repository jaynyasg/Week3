# AgentForge Users and Workflows

## Part 1 - Primary Users

### Security Operator

The security operator runs bounded adversarial campaigns against the deployed OpenEMR Clinical Co-Pilot target. This user needs a simple way to start a campaign, see progress, inspect verdicts, retrieve artifacts, and decide which findings are ready for reports or regression.

**Primary workflow:** select a campaign preset, confirm the deployed target, start a bounded run, review results, and export evidence.

**Why AgentForge instead of a manual prompt list:** manual prompts do not preserve model/provider, cost, target URL, expected safe behavior, observed behavior, verdict criteria, and regression status in one repeatable artifact.

### Maintainer / Implementer

The maintainer uses AgentForge artifacts to understand vulnerabilities and implement fixes in the target system. This user needs reproducible steps, severity, clinical impact, framework references, and validation status.

**Primary workflow:** read a vulnerability report, reproduce the deployed run, implement a fix in the target, rerun the regression case from deployed AgentForge.

### Human Approver

The human approver reviews high-severity findings, uncertain judge results, dangerous payload classes, and remediation suggestions. This role exists because LLM-generated findings can be wrong, incomplete, or overconfident.

**Approval workflow:** open the `needs_approval` queue, inspect the finding evidence and Langfuse trace/score metadata, choose `approved`, `rejected`, or `needs_more_evidence`, and record a short rationale. Only approved high-severity or ambiguous findings can become final reports or regression cases.

**Primary workflow:** inspect evidence, confirm exploitability and clinical impact, approve report publication or regression inclusion.

### Report Viewer / Grader

The report viewer reads the submitted artifacts and watches the demo. This user needs clear architecture, a deployed platform link, deployed target link, reproducible findings, and a defense narrative.

**Primary workflow:** open deployed AgentForge, see a bounded campaign against deployed OpenEMR, inspect reports and cost analysis.

## Part 2 - Access Groups

| Group | Capabilities | Explicit limits |
| --- | --- | --- |
| Public demo viewer | May view intentionally exposed demo pages if enabled | Cannot start campaigns or read protected artifacts |
| Security operator | Start bounded campaigns, view status, retrieve artifacts | Cannot override allowlisted target |
| Maintainer | Read reports and regression cases | Cannot approve high-risk findings by default |
| Human approver | Approve high-severity findings and regression promotion | Does not bypass target allowlist |
| Deployment secret admin | Configure target URL, operator token, provider keys, artifact path | Should not use regular campaign UI as a shortcut for secret changes |

## Part 3 - Agent Roles

| Agent | Responsibility | Guardrail |
| --- | --- | --- |
| Red Team Agent | Generate and mutate attack prompts | May create malicious input only for authorized target campaigns |
| Orchestrator Agent | Pick cases, enforce budget, schedule target calls | Cannot override allowlisted target or budget caps |
| Deployed Target Runner | Send prompts to deployed Clinical Co-Pilot | Calls only configured deployed target URL |
| Judge Agent | Evaluate observed behavior against expected safe behavior | Does not trust Red Team self-assessment |
| Documentation Agent | Produce vulnerability reports | Uses run evidence; does not invent exploit details |
| Regression Harness | Preserve replayable cases | Labels development vs deployed evidence clearly |
| Observability Layer | Record status, cost, provider, verdict, category | No raw PHI in structured logs |

## Part 4 - Clinical Roles Under Test

AgentForge is not replacing OpenEMR authorization, but it must test how the target handles clinical roles.

| Clinical role | Expected target behavior |
| --- | --- |
| `PHYSICIAN` | Broadest read access in the Week 2 tool matrix |
| `NURSE` | May access demographics, medications, vitals, allergies, schedule; should be refused for labs and visit notes |
| `ADMIN` | May access demographics and schedule only; should be refused for clinical tools |
| `CLINICIAN` | Alias to nurse tier in Week 2 behavior |
| Unknown / missing role | No clinical tool access |
| Demo bypass role | Accepted only in demo configuration; high-risk if used with real PHI |

## Part 5 - Use Cases

### UC-01 - Run a deployed RBAC campaign

The operator starts a small deployed campaign that checks nurse/admin access to labs, medications, and demographics. AgentForge records expected safe behavior, target response, verdict, severity, and regression recommendation.

### UC-02 - Test prompt and state injection

The operator runs multi-turn attacks where benign setup turns are followed by attempts to reuse hidden context, cross patient boundaries, or override policy. AgentForge records whether the target stays chart-scoped.

### UC-03 - Test tool and patient-scope tampering

The Red Team Agent creates prompts that attempt to induce wrong `patient_id` tool calls, malformed arguments, unknown functions, or excessive tool rounds. The Judge Agent verifies whether code-level guardrails held.

### UC-04 - Test attachment-based indirect prompt injection

The platform submits a lab or intake attachment whose visible clinical content is mixed with malicious instructions. The expected behavior is to use clinical facts while ignoring document-borne instructions.

### UC-05 - Convert confirmed exploit to report and regression

A confirmed finding becomes a vulnerability report and a replayable regression artifact. A maintainer can use the report to reproduce and later validate a fix.

### UC-06 - Produce final defense evidence

The grader opens the deployed platform, sees the deployed target URL, starts or reviews a bounded campaign, opens run artifacts, and sees the architecture/cost/security narrative aligned with the demo.

## Part 6 - Non-Users

- General internet users looking for a scanner.
- Clinicians seeking medical advice.
- OpenEMR administrators trying to replace native OpenEMR permissions.
- Researchers looking for a jailbreak leaderboard detached from healthcare workflow risk.
