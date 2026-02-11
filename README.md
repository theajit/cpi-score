# 🚦 CPI Score API — Status & Trust

## 🔍 Live Status Dashboard

Real-time visibility into API uptime, performance, and incident history.

---

## 🧩 Monitored API

Public REST API for Corruption Perceptions Index 2025 scores.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API info |
| GET | `/countries` | All countries (`?region=&min_score=&max_score=`) |
| GET | `/countries/{code}` | Lookup by ISO2/ISO3 |
| GET | `/regions` | Region summaries |
| GET | `/regions/{region}` | Countries in region |
| GET | `/rankings` | Ranked list (`?order=desc&limit=10`) |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |

---

## 📊 Metrics Tracked

* **Uptime %** (per component)
* **Latency** (P50 / P95)
* **Error Rate** (5xx)
* **Regional health checks** (multi-region validation)
* **Incident history** (timeline + resolution notes)

---

## 🚨 Incident Transparency

When something breaks, the status page will show:

* Severity level + impacted components
* Timeline updates (identified → mitigating → monitoring → resolved)
* Resolution summary (what happened + what changed)

Severity model:

| Status                  | Meaning                          |
| ----------------------- | -------------------------------- |
| 🟢 Operational          | All services normal              |
| 🟡 Degraded Performance | Slow responses, still functional |
| 🟠 Partial Outage       | Some endpoints unavailable       |
| 🔴 Major Outage         | Widespread API unavailability    |
| 🔵 Maintenance          | Planned downtime / upgrades      |

---

## 🔔 Subscribe to Updates

You can subscribe via:

* Email alerts
* RSS feed
* Webhooks (automation-friendly)

---

# ✅ Trust & Data Transparency

## 📌 Data Provenance (Source of Truth)

This API is a **distribution layer** for CPI data published by:

* **Publisher:** Transparency International
* **Dataset:** Corruption Perceptions Index (CPI) 2025
* **Official Source:** [https://www.transparency.org/en/cpi](https://www.transparency.org/en/cpi)

**Attribution requirement:**

> Data source: Transparency International – Corruption Perceptions Index (CPI)

---

## 🧾 Data Transformation Policy

The CPI Score API:

* ✅ Preserves official CPI scores (no recalculation)
* ✅ Normalizes to REST-friendly structures
* ✅ Adds ISO2/ISO3 indexing for reliable lookups
* ✅ Supports region-level rollups for convenience

The API does **not**:

* ❌ Change CPI methodology
* ❌ Predict corruption risk
* ❌ Apply proprietary scoring or weighting

---

## 🌍 Coverage Declaration

We expose coverage explicitly to avoid “trust gaps”:

* `coverage.served` → number of countries served by this API dataset
* `coverage.source_claim` → number published by Transparency International

If the numbers differ, common causes include:

* ISO mapping gaps for some territories
* Region/taxonomy normalization differences
* CPI territory classification vs ISO representation

**Recommendation:** Surface this in `GET /` and/or `GET /health` as metadata.

---

## 🔄 Update Frequency

* CPI scores are updated **annually** following TI publication.
* Patch updates may occur for:

  * ISO code corrections
  * Region mapping improvements
  * Formatting consistency

---

## ⚠️ Accuracy & Use Disclaimer

* TI retains methodological authority.
* This API is best suited for:

  * research, dashboards, analytics, education
* Not recommended as the *sole* input for:

  * legal, regulatory, or financial decisions without independent verification

---

# 🛡 Service Reliability (SLA-Lite)

This is an open-source service with best-effort reliability commitments.

### Availability Target

* **≥ 99% monthly uptime** target
* Continuous checks available via `/health`

### Version Stability

* Semantic versioning:

  * **MAJOR** = breaking changes
  * **MINOR** = new features/fields
  * **PATCH** = fixes, non-breaking

### Deprecation Policy

* Deprecated endpoints remain active for **≥ 90 days**
* Announced via:

  * GitHub releases
  * status page announcements
  * documentation notes

---

## 🔐 Security & Privacy

* No authentication required for public endpoints (currently)
* No personal or sensitive data stored
* Minimal operational logging for reliability monitoring

---

## 🧭 Reporting Issues

If you see discrepancies (data or uptime), report them here:

👉 [https://github.com/theajit/cpi-score/issues](https://github.com/theajit/cpi-score/issues)

---

## ⭐ Quick Links

* 🌐 Website → [https://corruptionindex.in](https://corruptionindex.in)
* 📦 GitHub → [https://github.com/theajit/cpi-score](https://github.com/theajit/cpi-score)
* 📚 Docs → [https://api.corruptionindex.in/docs](https://api.corruptionindex.in/docs)


