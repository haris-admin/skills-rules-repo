# Technical Disaster Recovery (DR) & Failover Runbook

A procedural engineering runbook for executing cloud infrastructure failover, cross-region database promotion, DNS traffic redirection, and graceful reconciliation during high-impact outages.

---

## 1. Failover Architecture Patterns

| Pattern | Recovery Time (RTO) | Recovery Point (RPO) | Relative Cost | Best For |
| :--- | :---: | :---: | :---: | :--- |
| **Backup & Restore (Cold)** | $4 - 24\text{ hours}$ | $1 - 24\text{ hours}$ | Low ($\$$) | Tier 3 internal tooling, historical archives |
| **Pilot Light (Warm Core)** | $1 - 2\text{ hours}$ | $5 - 15\text{ mins}$ | Moderate ($\$\$$) | Tier 2 backoffice, batch analytics |
| **Warm Standby (Active-Passive)** | $15 - 30\text{ mins}$ | $\le 5\text{ mins}$ | High ($\$\$\$$) | Tier 1 core databases, primary B2B SaaS portals |
| **Multi-Region Active-Active** | $< 1\text{ min}$ (automated) | Near $0$ | Very High ($\$\$\$\$\$$) | Tier 0 real-time payments, identity verification |

---

## 2. Disaster Declaration Decision Tree

Before executing a disaster failover, the Incident Commander must evaluate:

```
[Outage Detected in Primary Region]
        │
        ├─► Is the primary cloud provider acknowledging a region-wide outage?
        │     ├─► YES ──► Is estimated restoration > 30 minutes?
        │     │             ├─► YES ──► DECLARE DISASTER & TRIGGER RUNBOOK
        │     │             └─► NO  ──► Hold for 15 mins, prepare failover scripts
        │     └─► NO  ──► Verify local infrastructure (DNS, certificates, deployments)
        │
        ├─► Is there irreversible data corruption or active ransomware?
        │     └─► YES ──► FREEZE PRIMARY REPLICATION & RESTORE POINT-IN-TIME SNAPSHOT
        │
        └─► Has RTO clock reached 50% without a clear path to resolution?
              └─► YES ──► DECLARE DISASTER & TRIGGER RUNBOOK
```

---

## 3. Step-by-Step Production Failover Procedure

### Step 1: Isolate Primary & Prevent Split-Brain
- Immediately revoke API gateway ingress in the failing region or flip CDN origin to maintenance page to block incoming writes.
- Terminate or pause background processing workers to prevent inconsistent state transitions.

```bash
# Example Cloudflare API origin switch to Maintenance / Standby
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/rulesets/${RULESET_ID}" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"action": "redirect", "action_parameters": {"from_value": {"status_code": 302, "target_url": {"value": "https://maintenance.domain.com"}}}}'
```

### Step 2: Promote Standby Database Replica
- Stop cross-region replication stream.
- Promote the read replica in the standby region (`ap-southeast-2` to `ap-southeast-1` or `ap-southeast-4` Melbourne) to standalone read-write primary.
- Record the exact Log Sequence Number (LSN) or transaction ID at promotion.

```bash
# AWS CLI Aurora / RDS Replica Promotion
aws rds promote-read-replica \
  --db-instance-identifier prod-db-standby-melbourne \
  --region ap-southeast-4

# Wait for status to become available
aws rds wait db-instance-available \
  --db-instance-identifier prod-db-standby-melbourne \
  --region ap-southeast-4
```

### Step 3: Scale Up Standby Compute & Services
- Apply Terraform/IaC configuration to spin up full capacity in the standby region:

```bash
cd terraform/environments/dr-standby
terraform apply -var="desired_cluster_capacity=10" -auto-approve
```

- Update backend secrets / database connection strings in secret manager to reference the newly promoted database endpoint.
- Restart application container pods or worker pools.

### Step 4: Execute Smoke Test & Synthetic Validation
Before routing client traffic to the standby cluster, the Technical Ops Lead must execute automated synthetic health checks:

- [ ] `GET /healthz` returns `200 OK` across all microservices.
- [ ] Database read test: successfully fetch a known benchmark entity record.
- [ ] Database write test: successfully perform an isolated test transaction on a synthetic test tenant.
- [ ] Third-party egress test: verify outbound connectivity to external registries (ASIC, PEP, email gateway).

### Step 5: Shift Edge DNS Traffic to Standby
- Update Route 53 or Cloudflare DNS routing records to point production domains to the standby load balancer.

```bash
# Update Cloudflare DNS A/CNAME record
curl -X PUT "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/dns_records/${DNS_RECORD_ID}" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"type":"CNAME","name":"api.domain.com","content":"dr-alb.ap-southeast-4.elb.amazonaws.com","ttl":60,"proxied":true}'
```

- Monitor edge traffic metrics: 5xx error rate must drop below $0.1\%$; latency must stabilize within expected boundaries.

---

## 4. Post-Incident Reconciliation & Graceful Fallback

Once the primary region is fully recovered, do NOT immediately fail back:

1. **Maintain Standby as Primary**: Run on the standby region for at least 24 hours of stable business operation.
2. **Reverse Replication Direction**: Configure the recovered original region as a read replica of the current active standby cluster.
3. **Data Catch-Up Verification**: Verify that the replication stream has caught up to zero replica lag.
4. **Planned Maintenance Window**: Schedule a 5-minute planned maintenance window during low-traffic off-hours (e.g. Sunday 02:00 AEST) to gracefully switch traffic back to the primary region.
5. **Post-Mortem Initiation**: Convene a blameless post-mortem within 48 hours to document timeline, telemetry, root cause, and remediation actions.
