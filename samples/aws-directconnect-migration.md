---
layout: page
title: "AWS Connectivity Migration: IPsec Tunnels to Direct Connect"
description: Migration overview communicating a global consolidation of AWS-to-on-premises connectivity from individual IPsec tunnels to AWS Direct Connect with BGP.
doc_type: Migration Overview & Application Owner Communication
audience: Application Owners & Cross-functional Stakeholders
doc_date: Q4 2024
doc_status: Phased rollout in progress
show_pdf: true
---

<div class="toc" markdown="1">
<p class="toc-title">Contents</p>

- [Why We're Making This Change](#why-were-making-this-change)
- [What This Means for Application Owners](#what-this-means-for-application-owners)
- [How the Migration Works](#how-the-migration-works)
- [Architecture: Before vs. After](#architecture-before-vs-after)
- [BGP Routing: What's Changing Under the Hood](#bgp-routing-whats-changing-under-the-hood)
- [Migration Schedule and Coordination](#migration-schedule-and-coordination)
- [Questions](#questions)

</div>

## Why We're Making This Change

Our current AWS connectivity relies on a collection of IPsec tunnels (encrypted point-to-point network connections), each provisioned individually to carry traffic for specific application networks between AWS VPCs (Virtual Private Clouds - isolated private network environments within AWS where applications run) and on-premises data centers. Over time, this approach has created a management burden: each tunnel requires its own configuration, monitoring, and troubleshooting path. When issues arise, isolating the affected tunnel and tracing traffic flows across dozens of point-to-point connections adds significant time to resolution.

Migrating to AWS Direct Connect consolidates all AWS-to-on-premises connectivity onto a single, dedicated connection per region. BGP (Border Gateway Protocol - the routing protocol that controls how network addresses are advertised and shared between systems) handles this dynamically, so all networks are reachable over one connection without per-network tunnel provisioning. The result is a simpler, more reliable, and more transparent architecture.

---

## What This Means for Application Owners

If your application has components in AWS that communicate with on-premises systems, or has on-premises components that access data or services in AWS, this migration affects your connectivity path.

**What improves:**
- **Reliability:** Direct Connect provides a dedicated connection with consistent performance, replacing internet-dependent tunnels subject to variable path quality
- **Troubleshooting:** traffic flows are visible and traceable across a single connection; network issues affecting your application can be identified and resolved significantly faster
- **Scalability:** adding new networks or expanding existing ones no longer requires provisioning additional tunnels; routes are advertised through BGP automatically

**What stays the same:**
- Application behavior, endpoints, and DNS (Domain Name System - the service that translates application hostnames into network addresses) are unchanged
- IP addressing for your application environments is unchanged
- Your application does not require reconfiguration

---

## How the Migration Works

Each application network is migrated individually during a scheduled maintenance window. This phased approach ensures that issues affecting one network do not impact others, and allows the network team to validate connectivity before proceeding to the next group.

### Phase 1: Pilot Networks
A small subset of lower-risk application networks is migrated first. Connectivity is validated end-to-end before any production-critical networks are moved. BGP route advertisements are confirmed, and traffic flows are verified before the maintenance window closes.

### Phase 2: Staged Rollout by Application Group
Remaining networks are migrated in scheduled groups, coordinated with application owners. Both the existing IPsec tunnel and the Direct Connect path remain available during each window. If an issue is encountered, traffic can be reverted to the tunnel while the network team investigates.

### Phase 3: Tunnel Decommission
Once all networks have been successfully migrated and validated on Direct Connect, the legacy IPsec tunnels are decommissioned. BGP route-maps and prefix-lists are updated to reflect the final routing policy, and the configuration is documented for ongoing operations.

---

## Architecture: Before vs. After

<div class="mermaid">
graph TD
  subgraph BEFORE ["Before - Individual IPsec Tunnels"]
    R1[On-Premises Router] -->|"IPsec Tunnel - App A networks"| V1[AWS VPC A]
    R1 -->|"IPsec Tunnel - App B networks"| V2[AWS VPC B]
    R1 -->|"IPsec Tunnel - App C networks"| V3[AWS VPC C]
    R1 -->|"IPsec Tunnel - App N networks"| V4[AWS VPC ...]
  end
</div>

<div class="mermaid">
graph TD
  subgraph AFTER ["After - AWS Direct Connect with BGP"]
    R2[On-Premises Router] -->|"Single Direct Connect\nBGP advertises all prefixes"| DX[AWS Direct Connect]
    DX --> VA[AWS VPC A]
    DX --> VB[AWS VPC B]
    DX --> VC[AWS VPC C]
    DX --> VN[AWS VPC ...]
  end
</div>

## BGP Routing: What's Changing Under the Hood

For application owners who want the technical detail:

Previously, each IPsec tunnel carried routes for specific networks configured statically on the tunnel endpoint. Direct Connect uses BGP to advertise all permitted prefixes (network address ranges) dynamically. Route policy rules on the Direct Connect BGP neighbors define which address ranges are advertised in each direction: on-premises networks to AWS, and VPC networks back to on-premises routers.

This means routing decisions are dynamic and converge automatically when changes occur, rather than requiring manual tunnel reconfiguration for each network change.

---

## Migration Schedule and Coordination

Application owners will be contacted individually before their network group is scheduled for migration. You will receive:

- Advance notice of your scheduled maintenance window
- A point of contact on the network team for questions
- Confirmation once your network has been successfully migrated and validated

No action is required from application owners during the migration window unless you are asked to assist with application-layer validation.

---

## Questions

Contact the network engineering team through the standard project communication channel or submit a request through the IT service portal. A migration status tracker is maintained and updated following each completed phase.

---

*Organization and infrastructure details have been generalized to protect confidentiality.*
