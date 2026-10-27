# Sehat Saathi deployment readiness

## Current verdict

This repository is a local research prototype. It is **not approved for clinical, public-sector, or nationwide deployment** in India or the United States. The interface and workflow improvements do not establish clinical validity, security, legal compliance, or service reliability.

`SEHAT_ENV=production` deliberately prevents the web app from starting. Remove that gate only after the deployment owner has completed and documented the controls below, and replaced local prototype storage and identity with an approved platform.

## Current boundaries

- The curated facility directory is a small Neemrana / Rajasthan / NCR demo cluster. Other Indian locations use best-effort public OpenStreetMap geocoding and facility data; unknown towns never inherit Neemrana's coordinates. OpenStreetMap listings are community-mapped, not verified or guaranteed complete.
- Emergency numbers, public resources, medicine references, and languages are India-focused. There is no US public-service configuration or verified nationwide directory.
- Live nearby searches send the selected city or GPS coordinates to OpenStreetMap services. A controlled deployment needs an approved provider, privacy/retention review, attribution, coverage/freshness monitoring, and rate-limit/error handling.
- Patient-related records use local files/services. The app has no web identity, authorization, tenant separation, consent lifecycle, or tamper-evident audit trail.
- AI prescription reading and chat are assistive prototype features. They are not validated for clinical decisions and must not be trusted as medication instructions.
- Localhost binding is a development convenience, not an access-control design. Do not expose this server to a network.
- Use synthetic data only. Do not enter actual patient information in this prototype.

## Required before any controlled pilot

1. **Named clinical owner:** define intended use, clinical workflow, exclusions, escalation paths, and accountable review for each feature. Validate prescription reading, translated content, alert language, and caregiver workflows with representative users and clinicians.
2. **Independent security and privacy review:** threat model, secure identity and role policy, consent and revocation, tenant isolation, encryption and key management, retention/deletion rules, incident response, vulnerability management, and independent penetration testing.
3. **Jurisdiction-specific governance:** obtain qualified legal, privacy, accessibility, procurement, and medical-device advice for each deployment. Decide data residency, cross-border handling, record ownership, and operator responsibilities separately for each country and agency.
4. **Authoritative regional configuration:** use approved facility and emergency datasets with named owners, freshness and correction processes, geographic coverage, localization, and fallbacks. Never infer a user's jurisdiction from a hardcoded city.
5. **Resilient operations:** approved durable storage, tested backup/restore, disaster recovery, uptime objectives, monitoring, alerting, capacity tests, dependency management, and a staffed support and incident process.
6. **Accessibility and language validation:** test keyboard and screen-reader operation, contrast, zoom, plain language, assisted use, low-bandwidth behavior, and every supported language with users in each target population.
7. **Staged evaluation:** risk assessment, documented acceptance criteria, safety case, non-production simulation, limited supervised pilot, independent evaluation, and explicit authorization before expanding scope.

## Design direction

The browser experience uses a restrained civic-service visual language: legible type, clear task hierarchy, direct emergency access, visible uncertainty, and explicit prototype/data-scope notices. It is a design prototype for review, not evidence that the service is ready for government use.
