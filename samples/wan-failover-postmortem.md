---
layout: page
title: "Incident Post-Mortem: WAN Failover Failure - Primary WAN Outage"
description: Customer-facing post-mortem following a P1 outage caused by a WAN traffic blackhole that did not trigger automatic failover.
doc_type: Post-Incident Review
audience: Customer IT Leadership & Business Stakeholders
doc_date: Q2 2023
series_page: 1
series_total: 3
show_pdf: true
---

*Part 1 of 3 - See also: [WAN Failover Fix](wan-failover-technical) · [Target Architecture](wan-failover-architecture)*

---

<div class="toc" markdown="1">
<p class="toc-title">Contents</p>

- [Summary](#summary)
- [Impact](#impact)
- [Timeline](#timeline)
- [Root Cause](#root-cause)
- [Resolution](#resolution)
- [What We Are Doing to Prevent Recurrence](#what-we-are-doing-to-prevent-recurrence)
- [Lessons Learned](#lessons-learned)

</div>

## Summary

On-call monitoring triggered an alert indicating loss of connectivity between the customer's primary office facility and the managed data center. Investigation confirmed that the primary WAN (Wide Area Network) circuit had stopped passing traffic while continuing to show as physically active on both ends. Because the existing failover configuration relied on physical interface status rather than end-to-end traffic health, the backup IPsec tunnel (an encrypted secondary network connection used as a failover path) did not activate automatically. An on-call engineer manually intervened to force failover within 20 minutes of alert. Full service was restored at that point.

All data systems and voice services were unavailable for the duration of the outage, including Cisco IP phones and call center operations.

---

## Impact

| Category | Detail |
|----------|--------|
| **Duration** | Approximately 20 minutes from alert to full restoration |
| **Services affected** | All data systems; Cisco IP telephony including call center operations |
| **Users affected** | Several hundred users across multiple floors; call center staff most severely impacted |
| **Data loss** | None confirmed |
| **Financial impact** | Under assessment; call center productivity loss during outage window; active phone calls dropped at moment of failure with no automatic recovery |

---

## Timeline

| Time | Event |
|------|-------|
| T+0 | Monitoring alert fires; on-call engineer engaged |
| T+5 | Engineer confirms primary WAN circuit showing physically up; traffic not passing; backup tunnel not active |
| T+10 | Root cause identified: failover condition not met due to interface-up state; manual intervention initiated |
| T+20 | BGP (Border Gateway Protocol - the routing protocol managing traffic between the customer network and data center) peer on primary WAN circuit manually shut down; traffic routes via IPsec backup tunnel; services restored |
| T+45 | All systems confirmed stable; incident escalated for post-mortem review |

---

## Root Cause

The primary WAN circuit, a dedicated Layer 2 connection between the customer facility and the managed data center, experienced a traffic blackhole condition. Traffic was being silently dropped by the carrier while both the customer-side and data center-side physical interfaces remained in an up state. This is a known behavior with dedicated WAN circuits: the physical layer can show healthy while the provider's network discards packets downstream.

The failover configuration in place at the time of the incident monitored physical interface status as its trigger condition. Because the interface never went down, the IPsec backup tunnel did not activate, and traffic was blackholed rather than rerouted.

This configuration was inherited from the previous managed services provider. At the time of the incident, a full discovery and configuration audit of this customer's environment had not yet been completed following the transition of managed services. The failover gap was not identified prior to this event.

---

## Resolution

The on-call engineer manually issued a shutdown of the BGP peer session on the primary WAN circuit. With the BGP session down, routing converged over the IPsec backup tunnel and full connectivity was restored, including voice services.

A configuration review was immediately initiated to prevent recurrence. See the companion document, *WAN Failover Redesign: IPSLA-Driven BGP Failover*, for the permanent fix implemented following this incident.

---

## What We Are Doing to Prevent Recurrence

**Immediate actions (completed):**
- Full configuration audit of WAN failover logic for this customer and all affected accounts
- IP SLA (Service Level Agreement - a tool that continuously tests whether a network path is actually passing traffic, not just whether the physical connection appears active) monitoring implemented to detect blackhole conditions independent of interface state
- EEM (Embedded Event Manager - a Cisco automation tool that executes a response script when a monitored condition is met) configured to trigger BGP peer shutdown and failover without requiring manual intervention
- Failover tested and validated end-to-end in a maintenance window following implementation

**Process changes:**
- Discovery and configuration audit checklist formalized for all new client onboarding and MSP (Managed Service Provider) transitions
- WAN failover validation added as a required step before any new managed services engagement is marked fully operational

---

## Lessons Learned

Interface-up does not mean traffic is passing. Relying on physical interface state alone as a failover trigger is insufficient for circuits where the provider network can silently discard traffic. End-to-end reachability monitoring is required to detect and respond to these conditions.

The voice traffic dependency made stability the overriding concern throughout the recovery design. Active phone calls cannot survive even a sub-second interruption - a path that flaps back to an unstable primary drops every in-progress call at that moment, with direct impact on call center revenue and customer relationships. This shaped both the immediate fix and the longer-term architecture: the priority was not just fast failover, but controlled, verified recovery that would not expose voice traffic to a circuit that had not been confirmed stable.

The incomplete discovery at the time of transition created a visibility gap that contributed to this incident. Formalizing the transition audit process ensures this class of inherited misconfiguration is identified before it becomes an outage.

---

*Organization and provider details have been generalized to protect confidentiality.*
