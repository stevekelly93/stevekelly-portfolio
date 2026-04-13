---
layout: page
title: Portfolio
hide_nav: true
---

<a id="top"></a>

<div class="toc" markdown="1">
<p class="toc-title">Contents</p>

- [About](#about)
- [Writing Samples](#writing-samples)
  - [VPN Authentication Migration: SecureAuth to Okta + Google Titan](#vpn-authentication-migration-secureauth-to-okta--google-titan)
  - [Incident Post-Mortem: WAN Failover Failure](#incident-post-mortem-wan-failover-failure)
  - [WAN Failover Fix: IPSLA + EEM Stopgap Implementation](#wan-failover-fix-ipsla--eem-stopgap-implementation)
  - [WAN Failover Architecture: From Stopgap to Target State](#wan-failover-architecture-from-stopgap-to-target-state)
  - [AWS Connectivity Migration: IPsec Tunnels to Direct Connect](#aws-connectivity-migration-ipsec-tunnels-to-direct-connect)
  - [Content Delivery and the ISP Partnership](#content-delivery-and-the-isp-partnership-a-technical-overview-for-network-engineers)
- [Background](#background)

</div>

## About

I'm a network engineer who found that the highest-impact part of my work wasn't just building infrastructure, but making it legible to business stakeholders navigating an outage, to application owners acting on a migration, and to external partners integrating with us.

Through extensive experience designing and operating large-scale enterprise and data center networks, I developed a parallel focus on communication as a core part of delivery. I've clarified complex network behavior, aligned engineering and business teams on technical tradeoffs, and translated those decisions into actionable guidance across engineering, business, and partner audiences.

The samples here span those audiences, from internal engineering documentation to executive summaries to partner-facing technical explanations, and reflect how I approach writing as a way to drive understanding, alignment, and action.

This portfolio contains a selection of technical writing samples drawn from real projects, along with a small number of representative pieces that reflect how I would communicate network architectures and integration concepts in a partner-facing context. Organization names and identifying details have been generalized to protect confidentiality.

---

## Writing Samples

### [VPN Authentication Migration: SecureAuth to Okta + Google Titan](samples/vpn-migration)
**Audience:** IT Leadership & Cross-functional Stakeholders

A project overview document communicating a phased VPN authentication migration to non-network technical stakeholders. Covers business rationale, what changes for end users, migration phases, risk mitigations, and stakeholder responsibilities.

<div class="back-to-top"><a href="#top" title="Back to top">&#8593; top</a></div>

---

### [Incident Post-Mortem: WAN Failover Failure](samples/wan-failover-postmortem)
**Audience:** Customer IT Leadership & Business Stakeholders

A customer-facing post-mortem following a P1 outage caused by a WAN traffic blackhole that did not trigger automatic failover. Documents impact, root cause, timeline, and prevention measures in clear language for a non-engineering audience.

*Part 1 of 3 - See also: [WAN Failover Fix](samples/wan-failover-technical) · [Target Architecture](samples/wan-failover-architecture)*

<div class="back-to-top"><a href="#top" title="Back to top">&#8593; top</a></div>

---

### [WAN Failover Fix: IPSLA + EEM Stopgap Implementation](samples/wan-failover-technical)
**Audience:** Network Engineering & IT Operations

A technical resolution summary documenting the stopgap fix implemented following the incident. Explains the gap in the prior configuration, the IPSLA + EEM solution, and how failover now behaves, including a before/after comparison and validation results.

*Part 2 of 3 - See also: [Post-Mortem](samples/wan-failover-postmortem) · [Target Architecture](samples/wan-failover-architecture)*

<div class="back-to-top"><a href="#top" title="Back to top">&#8593; top</a></div>

---

### [WAN Failover Architecture: From Stopgap to Target State](samples/wan-failover-architecture)
**Audience:** Network Engineering & IT Operations

A design document tracing the full evolution of WAN failover strategy, from interface-based triggers through IP SLA + EEM, BFD-backed BGP, and policy-driven failover. Covers configuration intent for Cisco IOS-XE and NSX Tier-0, with architecture diagrams and a sequenced implementation plan.

*Part 3 of 3 - See also: [Post-Mortem](samples/wan-failover-postmortem) · [Initial Fix](samples/wan-failover-technical)*

<div class="back-to-top"><a href="#top" title="Back to top">&#8593; top</a></div>

---

### [AWS Connectivity Migration: IPsec Tunnels to Direct Connect](samples/aws-directconnect-migration)
**Audience:** Application Owners & Cross-functional Stakeholders

A migration overview communicating a global consolidation of AWS-to-on-premises connectivity from individual IPsec tunnels to AWS Direct Connect with BGP. Written for application owners who need to understand the impact on their systems without requiring deep networking knowledge.

<div class="back-to-top"><a href="#top" title="Back to top">&#8593; top</a></div>

---

### [Content Delivery and the ISP Partnership: A Technical Overview for Network Engineers](samples/isp-cdn-localization)
**Audience:** ISP Network Engineering & Peering Teams

A partner-facing technical explainer covering how CDN traffic localization works, the two deployment models (embedded appliances and peering), how BGP steers traffic in each, and how to evaluate which approach fits a given network. Written for ISP network engineers who understand routing but are evaluating a CDN partnership for the first time.

<div class="back-to-top"><a href="#top" title="Back to top">&#8593; top</a></div>

---

## Background

**Technical domains:** BGP, OSPF, EIGRP, MPLS, EVPN/VXLAN, SD-WAN, data center networking, cloud interconnection, firewall governance, ISP peering concepts

**Documentation platforms:** Confluence, SharePoint, internal wiki systems

**Certifications:** CCNP Enterprise, CCDP, CCNA, Microsoft Azure Administrator, ITIL Foundation

**LinkedIn:** [linkedin.com/in/stevekellysd](https://www.linkedin.com/in/stevekellysd)
