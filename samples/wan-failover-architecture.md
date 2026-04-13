---
layout: page
title: "WAN Failover Architecture: From Stopgap to Target State"
description: Design document covering the evolution of WAN failover detection from interface-based triggers through BFD-backed BGP and policy-driven failover for Cisco IOS-XE to NSX Tier-0 connectivity.
doc_type: Architecture Design & Evolution
audience: Network Engineering & IT Operations
doc_date: Q3 2023
series_page: 3
series_total: 3
show_pdf: true
---

*Part 3 of 3 - See also: [Incident Post-Mortem](wan-failover-postmortem) · [IPSLA + EEM Fix](wan-failover-technical)*

---

<div class="toc" markdown="1">
<p class="toc-title">Contents</p>

- [Purpose](#purpose)
- [The Problem with Interface-Based Failover](#the-problem-with-interface-based-failover)
- [Evolution of Failover Strategy](#evolution-of-failover-strategy)
- [Configuration Intent](#configuration-intent)
- [Failover and Failback Flow](#failover-and-failback-flow)
- [Risks and Considerations](#risks-and-considerations)
- [Implementation Sequence](#implementation-sequence)
- [Summary](#summary)
- [Key Takeaways](#key-takeaways)

</div>

## Purpose

This document describes the target-state failover architecture for Cisco IOS-XE to NSX Tier-0 connectivity, and the engineering rationale for evolving beyond the initial IP SLA + EEM stopgap.

The goal is failover behavior that is:

- **Fast and deterministic:** converges without waiting for BGP hold timers
- **Accurate:** detects real path usability, not just interface state
- **Stable:** recovers cleanly without flapping - active VoIP calls cannot survive even a sub-second path interruption, so a failover that oscillates or returns to an unstable primary drops calls and directly impacts call center revenue and client relationships
- **Operationally maintainable:** removes script-based dependencies where possible

---

## The Problem with Interface-Based Failover

The original failure that triggered this design work exposed a fundamental gap: a carrier experienced internal forwarding failures while both physical interfaces remained up. BGP adjacency stayed established. Traffic was blackholed. No failover occurred.

The root cause was a failover model that relied entirely on Layer 1/2 signals, which told us nothing about whether the data plane was actually functional.

<div class="mermaid">
graph LR
  A[On-Premises\nCisco IOS-XE] -->|"Direct L2 - interfaces UP/UP\nBGP session UP\nTraffic blackholed"| B[NSX Tier-0]
  A -.->|"Tunnel backup\nNever activates"| B
  C["⚠ Carrier internal failure\nInvisible to control plane"] -. affects .-> A
</div>

The fix documented in [Part 2](wan-failover-technical) addressed immediate detection using IP SLA probes and an EEM script to force BGP peer shutdown on failure. That solution works, but it introduces operational complexity, script dependency, and potential instability during failback. This document describes where the architecture should go next.

---

## Evolution of Failover Strategy

The progression from initial design to target state follows five stages. Each stage improves on the one before it.

<div class="mermaid">
flowchart LR
  S0["Stage 0\nInterface / BGP timers\nMisses blackholes"]
  S1["Stage 1\nIP SLA + EEM\nDetects blackholes\nBut fragile"]
  S2["Stage 2\nBFD + BGP\nFast peer detection\nMisses deeper failures"]
  S3["Stage 3\nBFD + End-to-end probes\nTwo-layer validation"]
  S4["Stage 4\nPolicy-driven failover\nNo neighbor shutdown\nProduction-grade"]
  S5["Stage 5\nMulti-signal health\nFull resilience"]

  S0 --> S1 --> S2 --> S3 --> S4 --> S5
  style S1 fill:#fff3cd,stroke:#f0ad4e
  style S4 fill:#d4edda,stroke:#28a745
</div>

### Stage 0 - Interface-Based Failover (Baseline)

Failover triggers only when the physical interface goes down or BGP hold timers expire. Cannot detect carrier internal failures or data-plane blackholes while the control plane remains healthy.

**Weakness:** Silent outages. The network looks healthy while traffic is dropping.

---

### Stage 1 - IP SLA + EEM (Current State)

IP SLA probes a remote endpoint. On failure, an EEM script administratively shuts the BGP neighbor, forcing convergence to the backup tunnel.

**Improvement:** Detects real traffic failure even when BGP stays up.

**Limitations:**
- Dependent on script logic and state tracking
- Failback requires careful coordination to avoid flapping
- Not protocol-native, making it harder to scale and maintain

---

### Stage 2 - BFD-Backed BGP

Bidirectional Forwarding Detection (BFD) is enabled on the BGP session over the direct path. BFD operates at sub-second intervals and can detect forwarding-path failures to the BGP peer far faster than BGP hold timers alone.

When BFD detects a failure, BGP tears down the session natively with no EEM script required. Routing converges to the backup path automatically.

**Improvement:** Fast, protocol-native convergence. Eliminates EEM dependency for peer-reachability failures.

**Limitation:** BFD only validates reachability to the BGP peer. It does not detect failures deeper in the carrier network or partial blackholing beyond the peer.

---

### Stage 3 - BFD + End-to-End Health Probes

Layer 1 detection (BFD) is combined with end-to-end reachability probing. IP SLA probes target meaningful endpoints such as an NSX Tier-0 loopback, a data center internal VIP, or a critical service IP, rather than just the BGP peer address.

Probe results are tied to routing decisions via tracking objects and route-map policy, avoiding the need for neighbor shutdown.

**Two-layer validation:**

| Layer | Mechanism | Detects |
|-------|-----------|---------|
| BFD | Bidirectional Forwarding Detection | Forwarding failure to BGP peer |
| IP SLA | End-to-end reachability probes | Carrier internal failures, deeper blackholing, service reachability |

---

### Stage 4 - Policy-Driven Failover (Target State)

Both paths remain active at all times. The direct path is preferred via routing policy (Local Preference). When health signals indicate the primary path is degraded, routing policy shifts traffic to the backup without tearing down the BGP neighbor.

<div class="mermaid">
graph TD
  subgraph "Target State - Active/Backup with Policy Failover"
    IOS[Cisco IOS-XE] -->|"BGP - Local Pref 200 (preferred)"| DC[Layer 2 WAN]
    IOS -->|"BGP - Local Pref 100 (backup)"| TUN[IPsec Tunnel]
    DC -->|"BFD + SLA probe"| NSX[NSX Tier-0]
    TUN --> NSX

    PROBE["IP SLA\nEnd-to-end probe"] -->|"Failure detected"| TRACK[Track Object]
    BFD_SIG["BFD signal"] --> TRACK
    TRACK -->|"Adjusts Local Preference\nvia route-map"| IOS
  end
</div>

**Key difference from Stage 1:** Traffic shifts because routing policy changes, not because the BGP neighbor is shut down. The control plane remains stable throughout.

**Failback behavior:**
- Automatic when BFD session restores **and** health probes succeed
- Hysteresis and delay timers prevent flapping on intermittent failures

---

## Configuration Intent

### Cisco IOS-XE - Primary Path (Direct)

```
router bgp 65001
 neighbor 10.10.10.2 remote-as 65002
 neighbor 10.10.10.2 fall-over bfd
 !
 address-family ipv4
  neighbor 10.10.10.2 activate
  neighbor 10.10.10.2 route-map PRIMARY-IN in
 exit-address-family

route-map PRIMARY-IN permit 10
 set local-preference 200
```

### Cisco IOS-XE - Backup Path (Tunnel)

```
router bgp 65001
 neighbor 172.16.10.2 remote-as 65002
 !
 address-family ipv4
  neighbor 172.16.10.2 activate
  neighbor 172.16.10.2 route-map BACKUP-IN in
 exit-address-family

route-map BACKUP-IN permit 10
 set local-preference 100
```

### NSX Tier-0

- Configure BGP neighbors for both the direct Cisco edge peer and tunnel-side peer
- Enable BFD on BGP sessions
- Ensure route advertisements and prefix filtering are consistent with IOS-XE policy

---

## Failover and Failback Flow

<div class="mermaid">
sequenceDiagram
  participant Primary as Direct Path
  participant BFD as BFD / IP SLA
  participant BGP as BGP Policy
  participant Backup as Tunnel Path

  Note over Primary,Backup: Normal operation - direct path preferred
  Primary->>BFD: Health probes passing
  BFD->>BGP: Local Pref 200 active
  BGP->>Primary: Traffic flows via direct path

  Note over Primary,Backup: Failure detected
  Primary->>BFD: Probe failure / BFD down
  BFD->>BGP: Adjust Local Pref → 100 or withdraw route
  BGP->>Backup: Traffic shifts to tunnel

  Note over Primary,Backup: Recovery
  Primary->>BFD: Probes passing (sustained)
  BFD->>BGP: Restore Local Pref 200 (after delay)
  BGP->>Primary: Traffic returns to direct path
</div>

---

## Risks and Considerations

**BFD scope:** BFD validates reachability to the BGP peer only. End-to-end probes are required to catch deeper carrier failures; BFD alone is not sufficient.

**Probe target selection:** IP SLA probes must target meaningful endpoints. Probing only the BGP peer IP defeats the purpose. Probe targets should include at minimum an NSX loopback and a data center service IP.

**Failback stability:** Without hysteresis controls, recovering links can cause route flapping. Delay timers on track objects and SLA threshold tuning prevent premature failback.

**NSX BFD compatibility:** Validate BFD support and timer compatibility between IOS-XE and NSX Tier-0 before enabling in production.

---

## Implementation Sequence

1. Enable BFD on Cisco ↔ NSX direct-path BGP session; validate detection behavior
2. Introduce route-map policy (Local Preference) for path preference
3. Configure IP SLA probes targeting meaningful DC endpoints; tie to track objects
4. Test failover end-to-end using controlled link simulation
5. Tune BFD timers, SLA thresholds, and failback delay for stability
6. Keep existing EEM script as safety net initially; phase out once policy-based failover is validated

---

## Summary

| Stage | Mechanism | Detects | Status |
|-------|-----------|---------|--------|
| 0 | Interface / BGP timers | Link down | Replaced |
| 1 | IP SLA + EEM | End-to-end failure | Current - transitioning |
| 2 | BFD + BGP | Path to peer | Implementing |
| 3 | BFD + SLA probes | Path + service health | Target |
| 4 | Policy-driven failover | Clean failover/failback | Target |

---

## Key Takeaways

- **BFD** ensures the routing path to the peer is alive
- **Health probes** ensure the network is actually usable end-to-end
- **Routing policy** determines which path is preferred, without tearing down the control plane
- The evolution from interface-based triggers to policy-driven failover represents a shift from reactive to deterministic network behavior

---

*Organization, IP addressing, and AS numbers in this document are illustrative. This document is part of a three-part series on WAN failover design.*
