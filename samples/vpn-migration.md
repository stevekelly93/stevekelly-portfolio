---
layout: page
title: "VPN Authentication Migration: SecureAuth to Okta + Google Titan"
description: Project overview communicating a phased VPN authentication migration to IT leadership and cross-functional stakeholders.
doc_type: Project Overview
audience: IT Leadership & Cross-functional Stakeholders
doc_date: Q1 2025
show_pdf: true
---

<div class="toc" markdown="1">
<p class="toc-title">Contents</p>

- [Why We're Making This Change](#why-were-making-this-change)
- [What Changes and What Stays the Same](#what-changes-and-what-stays-the-same)
- [Migration Timeline and Phases](#migration-timeline-and-phases)
- [Risks and How We're Addressing Them](#risks-and-how-were-addressing-them)
- [What We Need From Stakeholders](#what-we-need-from-stakeholders)
- [Questions and Resources](#questions-and-resources)

</div>

## Why We're Making This Change

Our current VPN (Virtual Private Network - the secure, encrypted connection that allows users to access company systems remotely) authentication relies on certificate-based verification through SecureAuth. This approach creates operational friction: certificate lifecycle management requires ongoing IT intervention, provisioning certificates to new or replacement devices delays user access, and the model provides limited visibility into authentication events at the individual user level.

Migrating to Okta with Google Titan hardware tokens delivers phishing-resistant multi-factor authentication (MFA - requiring both a password and a physical key to verify identity) that meets modern security standards while simplifying the experience for both end users and IT.

---

## What Changes and What Stays the Same

**What changes:** Users will authenticate using their Okta credentials combined with a Google Titan security key, a hardware token that plugs into a USB port and authenticates with a single tap. This replaces the certificate-based flow that currently runs silently in the background.

**What stays the same:** The VPN client, connection endpoint, and overall experience remain unchanged. Users connect to the same VPN they use today; only the authentication step is different.

> **Note:** End users will receive their Google Titan, enrollment instructions, and a support contact before their cutover date. No action is required until that communication arrives.

---

## Migration Timeline and Phases

### Phase 1: Pilot & Validation
Deploy to 20 IT staff and power users. Validate Okta integration, Google Titan enrollment flow, and helpdesk runbooks.
**Duration:** 2 weeks

### Phase 2: Staged Rollout
Expand by department or location. Both authentication methods remain active in parallel, so no user loses access during transition.
**Duration:** 2 weeks per cohort

### Phase 3: Full Cutover
Decommission SecureAuth once all users have enrolled and authenticated successfully on the new platform.

---

## Risks and How We're Addressing Them

**Primary risk:** Users unable to complete enrollment before their cutover date.

**Mitigations:**
- Parallel operation during Phase 2 ensures no access disruption
- Dedicated enrollment support channel available throughout migration
- Helpdesk briefed and equipped with troubleshooting documentation before Phase 1 begins

**Lost or damaged Google Titans:** Users may request temporary access through a break-glass process. A ticket submitted to the Identity team moves the user to a group that permits MFA without a hardware token while a replacement key is provisioned. This policy will be documented and communicated to all users prior to cutover.

---

## What We Need From Stakeholders

| Role | Responsibility |
|------|----------------|
| **IT Security / Identity** | Own Okta configuration, Google Titan provisioning, and break-glass access approvals |
| **Department Leads** | Confirm employee rosters; flag users with accessibility needs or non-standard device configurations before rollout |
| **End Users** | Complete enrollment when notified; contact the helpdesk for questions or key issues |

End-user communications will be issued one week before each cohort's cutover date.

---

## Questions and Resources

- **Questions:** Contact the IT Security team or submit a request through the helpdesk portal
- **Project status:** Available on the IT project status page throughout the migration

---

*Organization names and identifying details have been generalized to protect confidentiality.*
