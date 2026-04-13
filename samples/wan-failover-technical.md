---
layout: page
title: "WAN Failover Fix: IPSLA + EEM Stopgap Implementation"
description: Technical resolution summary documenting the immediate IPSLA and EEM fix deployed following the WAN blackhole outage, and the known limitations that drove further architectural work.
doc_type: Technical Resolution Summary - Stopgap Implementation
audience: Network Engineering & IT Operations
doc_date: Q2 2023
series_page: 2
series_total: 3
show_pdf: true
---

*Part 2 of 3 - See also: [Incident Post-Mortem](wan-failover-postmortem) · [Target Architecture](wan-failover-architecture)*

---

<div class="toc" markdown="1">
<p class="toc-title">Contents</p>

- [Background](#background)
- [The Problem With the Prior Configuration](#the-problem-with-the-prior-configuration)
- [The Solution: IPSLA + EEM](#the-solution-ipsla--eem)
- [How Failover Now Behaves](#how-failover-now-behaves)
- [Failover and Recovery Flow](#failover-and-recovery-flow)
- [Validation](#validation)
- [Known Limitations of This Approach](#known-limitations-of-this-approach)
- [Key Takeaway](#key-takeaway)

</div>

## Background

Following a P1 outage caused by a WAN traffic blackhole that did not trigger automatic failover, an immediate fix was deployed to close the detection gap and restore automated failover capability. This document describes that stopgap solution: what was implemented, how it behaves, and the limitations that were identified through operational experience.

A subsequent architectural review evaluated the long-term design. That work is documented in [WAN Failover Architecture: From Stopgap to Target State](wan-failover-architecture).

---

## The Problem With the Prior Configuration

The customer's primary WAN path used a dedicated Layer 2 circuit with BGP peering to the managed data center. An IPsec tunnel over a secondary internet circuit served as the backup path.

Failover was configured to trigger when the primary circuit's physical interface went down. This is a common but incomplete approach. Dedicated WAN circuits can enter a state where:

- Both the customer-side and provider-side physical interfaces remain up
- The upstream provider network silently discards traffic
- BGP sessions stay established (keepalives pass; data traffic does not)

In this state, the failover condition is never met, traffic is blackholed, and the backup path does not activate.

A third ISP circuit was evaluated as an option to improve diversity, but due to physical infrastructure constraints at the customer facility, a third provider would share upstream paths with the existing internet circuit, providing no meaningful redundancy.

---

## The Solution: IPSLA + EEM

The redesigned failover was implemented on the customer router pair using two IOS features working together.

**IP SLA** continuously sends end-to-end probes across the primary WAN path. Unlike BGP keepalives, these probes traverse the provider network, so they fail when traffic is being blackholed even if the physical interface is up.

**EEM (Embedded Event Manager)** monitors the IP SLA probe results on the customer routers. When the probe reports reachability failure, EEM executes a script that:
1. Administratively shuts down the BGP peer session on the primary WAN interface
2. Triggers route convergence over the IPsec backup tunnel
3. Logs the event for operations visibility

### Intentional Manual Recovery

Failback to the primary circuit is intentionally manual. Once EEM shuts the BGP peer, it remains down until an engineer explicitly removes the shutdown. This was a deliberate design decision: the carrier had experienced repeated intermittent forwarding failures on the same circuit, and the team needed direct confirmation from the carrier that the underlying issue was resolved before returning production traffic to the primary path. Automatic recovery would have risked restoring to a circuit that had not been fully stabilized.

The stakes made this requirement non-negotiable. The customer's call center ran over this WAN path, and active VoIP calls cannot survive even a sub-second interruption. A path that flips back to an unstable primary drops every in-progress call at that moment, with direct impact on revenue and client relationships. Holding traffic on the confirmed-stable IPsec backup until carrier verification was complete was the only acceptable approach.

---

## How Failover Now Behaves

**Before the change:**

| Condition | Detection | Result |
|-----------|-----------|--------|
| Physical interface down | Interface state | Automatic failover |
| Traffic blackhole, interfaces up | Not detected | No failover - manual intervention required |

**After the change:**

| Condition | Detection | Result |
|-----------|-----------|--------|
| Physical interface down | Interface state | Automatic failover (unchanged) |
| BGP session drops | BGP hold timer | Automatic failover (unchanged) |
| Traffic blackhole, interfaces up | **IP SLA end-to-end probe** | **Automatic failover via EEM; manual restore required** |
| Provider packet loss above threshold | **IP SLA threshold monitoring** | **Automatic failover via EEM; manual restore required** |

### Architecture: Before vs. After

<div class="mermaid">
graph LR
  subgraph BEFORE ["Before - Interface-based failover"]
    A1[Customer Routers] -->|"BGP / Layer 2 WAN"| B1[Managed Data Center]
    A1 -.->|"IPsec backup"| B1
    X1["⚠ Carrier blackhole\nBGP stays UP\nInterfaces stay UP\nNo failover triggered"] -.->|affects| A1
  end
</div>

<div class="mermaid">
graph LR
  subgraph AFTER ["After - IPSLA + EEM on customer routers"]
    A2["Customer Router Pair\n(IP SLA + EEM)"] -->|"BGP / Layer 2 WAN"| B2[Managed Data Center]
    A2 -.->|"IPsec backup"| B2
    EEM["Probe fails\nEEM shuts BGP peer\nIPsec activates\nManual restore required"] --> A2
  end
</div>

---

## Failover and Recovery Flow

```
Normal operation:
  IP SLA probe → PASSING
  BGP peer → UP
  Traffic → Layer 2 WAN (primary)

Blackhole detected:
  IP SLA probe → FAILING
  EEM triggers → BGP peer shutdown (on customer router)
  Routing converges → IPsec backup tunnel
  Traffic → IPsec tunnel (backup)
  BGP peer remains shut - manual restore required

Recovery (manual):
  Carrier confirms underlying issue resolved
  Network engineer removes BGP peer shutdown
  Routing converges → Layer 2 WAN (primary)
  Traffic → Layer 2 WAN (primary)
```

---

## Validation

Following implementation, failover was tested end-to-end in a scheduled maintenance window:

- IP SLA probes confirmed passing on the primary path under normal conditions
- Simulated blackhole condition triggered EEM within the configured probe interval
- Voice and data traffic confirmed passing over backup path within BGP convergence time
- BGP peer confirmed remaining shut after probe recovery, requiring manual intervention to restore
- Manual restoration of BGP peer confirmed clean convergence back to the primary path

---

## Known Limitations of This Approach

While the IP SLA + EEM solution resolves the immediate detection gap, operational experience identified several limitations:

- **Script dependency:** EEM logic requires careful maintenance; the shutdown and restore behavior is sensitive to probe timing and threshold configuration
- **Peer-only detection:** IP SLA probing the BGP peer IP alone does not catch failures deeper in the carrier network; probe targets must be chosen carefully
- **Manual restore overhead:** failback requires a deliberate engineer action after carrier confirmation. This is intentional for stability in this environment, but it increases time-to-recovery and requires on-call awareness of the procedure
- **Not protocol-native:** the solution works around BGP rather than working with it, making it harder to scale and audit

These limitations informed the target-state architecture documented in [WAN Failover Architecture: From Stopgap to Target State](wan-failover-architecture), which replaces EEM-driven neighbor shutdown with BFD-backed BGP and policy-based failover.

---

## Key Takeaway

Physical interface state is a necessary but insufficient failover trigger for dedicated WAN circuits. End-to-end reachability monitoring (implemented here via IP SLA) closes the detection gap, while intentional manual restore ensures traffic does not return to an unverified primary path. This solution was deployed as an effective stopgap; the architectural evolution toward BFD and policy-driven failover addresses the remaining operational complexity.

---

*Organization and provider details have been generalized to protect confidentiality.*
