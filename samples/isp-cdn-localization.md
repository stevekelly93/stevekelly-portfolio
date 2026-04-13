---
layout: page
title: "Content Delivery and the ISP Partnership: A Technical Overview for Network Engineers"
description: Partner-facing explainer covering traffic localization approaches, BGP steering mechanics, and how to evaluate which CDN deployment model fits your network.
doc_type: Partner Technical Overview
audience: ISP Network Engineering & Peering Teams
doc_date: Q1 2025
show_pdf: true
---

<div class="toc" markdown="1">
<p class="toc-title">Contents</p>

- [Why This Matters to Your Network](#why-this-matters-to-your-network)
- [What Traffic Localization Means](#what-traffic-localization-means)
- [The Two Deployment Models](#the-two-deployment-models)
- [How BGP Steers Traffic in Each Model](#how-bgp-steers-traffic-in-each-model)
- [Choosing the Right Approach](#choosing-the-right-approach)
- [Operational Considerations](#operational-considerations)
- [Getting Started](#getting-started)

</div>

## Why This Matters to Your Network

Video streaming has become a dominant share of downstream traffic on most broadband networks. For many ISPs, a significant portion of total network throughput during peak evening hours - often 40–60% - is attributable to a small number of streaming content providers.

When that traffic transits upstream links, it competes with all other traffic on your network. You pay transit costs for it, your upstream links become a bottleneck, and your subscribers experience the result: buffering, quality drops, and the support calls that follow.

Localizing that content - serving it from a point close to your subscribers rather than pulling it across transit links from distant origins - reduces load on upstream infrastructure, lowers transit cost, and improves subscriber experience.

CDN partnerships are the mechanism for doing this at scale. This document provides a practical technical overview of how CDN partnerships operate, how traffic is steered, and how to evaluate which approach fits your network.

---

## What Traffic Localization Means

In a conventional delivery model, your subscriber's video player requests a stream and that request travels outbound through your access network, across your upstream transit links, through one or more provider networks, and eventually reaches a content origin. The video data returns along the same path in reverse. Every byte crosses your transit connection.

In a localized delivery model, the content is available at a point inside or adjacent to your network. The subscriber's request still leaves your access infrastructure, but it terminates at a server that is either physically hosted within your facility or reachable over a direct network connection - without traversing transit. Video data returns directly from that local point.

<div class="mermaid">
graph TD
  subgraph WITHOUT ["Without Localization"]
    S1[Subscriber] --> A1[Access Network]
    A1 -->|"Transit"| U1[Upstream Provider]
    U1 --> O1[Content Origin]
  end
</div>

<div class="mermaid">
graph TD
  subgraph WITH ["With Localization"]
    S2[Subscriber] --> A2[Access Network]
    A2 --> L2[Local Cache / CDN Node]
    L2 -.->|"Cache miss only"| U2[Upstream]
  end
</div>

Content selection is typically handled by the provider's control plane, often via DNS, while BGP determines the network path used to reach the selected delivery node.

The practical effect: popular content is pre-positioned and served locally, resulting in high effective cache-hit rates. Only uncached or less-popular content crosses transit links. Your upstream traffic volume drops, your subscribers see better performance, and that capacity is available for everything else.

---

## The Two Deployment Models

CDN partnerships typically offer two approaches. They are not mutually exclusive - some networks use both.

### Embedded Appliances (On-Net Hosting)

The content provider supplies caching hardware and places it directly in your network facility. You provide rack space, power, and network connectivity. The provider manages and operates the equipment.

Traffic flow: subscriber requests route to the local appliance; content is served directly from your facility with no transit involvement.

**Characteristics:**
- Highest possible localization - content originates within your own infrastructure
- Does not require external peering relationships; BGP involvement is limited to integration with the appliance for traffic steering rather than full upstream routing policy management
- Provider handles capacity management and hardware lifecycle
- Requires physical space and power in your facility
- Best fit for ISPs with significant traffic volume to a specific provider

### Peering (Network-Level Interconnection)

Your network establishes a BGP peering session with the content provider, either at an internet exchange point (IXP) or through a direct private network interconnect (PNI). The provider advertises its CDN prefix ranges to you; your network learns those routes and reaches CDN nodes over the direct peering link rather than through transit.

Traffic flow: subscriber requests to content provider IPs route via the peering link; BGP policy controls which paths are used.

**Characteristics:**
- Traffic stays off transit links without requiring hardware in your facility
- Scales to multiple content providers through a single IXP presence
- Requires BGP peering configuration and ongoing routing policy maintenance
- IXP membership or cross-connect costs apply
- Best fit for ISPs already present at IXPs or serving multiple major content providers

---

## How BGP Steers Traffic in Each Model

Understanding the routing mechanics helps you evaluate where failures occur and how to troubleshoot them.

### Embedded Appliances

The content provider's appliance announces a localized DNS or anycast address. Subscriber requests resolve to that local address; your routing infrastructure delivers them to the appliance within your facility. BGP interaction is limited and typically used for controlled traffic steering rather than full peering policy management. The appliance integrates into your network as a local service endpoint, with routing handled in coordination with the provider.

What matters here is that your internal routing correctly delivers subscriber traffic to the appliance address, and that the appliance has adequate bandwidth on its uplinks to your core network. The BGP relationship, if any, is between the provider's appliance and their origin infrastructure for cache fills - not something you configure.

### Peering

With a peering-based model, BGP is the control plane for traffic steering.

The content provider's edge routers advertise CDN prefixes over the peering session. Your routers learn those routes with the peering path as the next-hop. Your BGP policy determines whether those routes are preferred over transit routes to the same destinations.

Standard practice is to apply a higher local preference to routes learned from peering neighbors, ensuring CDN-bound traffic uses the direct path rather than falling back to transit.

<div class="mermaid">
graph LR
  subgraph "Your Network"
    BR[Border Router]
    CORE[Core]
    SUB[Subscriber]
  end

  subgraph "Content Provider"
    PE[Peering Edge]
    CDN[CDN Nodes]
  end

  TRANSIT[Transit Provider]

  SUB --> CORE
  CORE --> BR
  BR -->|"BGP peering - preferred\nLocal Pref 200"| PE
  BR -->|"Transit - backup\nLocal Pref 100"| TRANSIT
  PE --> CDN
</div>

**Route policy considerations:**

- **Local preference:** Set a higher local preference on routes learned from the CDN peering neighbor so they are preferred over the same prefixes via transit
- **Prefix filtering:** Accept only the content provider's announced CDN prefixes; do not accept a default route or broader prefixes that could make the peering session a default path
- **Traffic ratios:** Most CDN peering is asymmetric by nature - inbound traffic (content delivery) is much larger than outbound; confirm the peering agreement accounts for this
- **Failover:** Retain transit routes for CDN prefixes as a backup path; if the peering session fails, traffic should fall back to transit rather than blackholing

---

## Choosing the Right Approach

Neither model is universally better. The right choice depends on your traffic profile, infrastructure, and operational preferences.

| Factor | Embedded Appliance | Peering |
|--------|-------------------|---------|
| **Traffic volume to a single provider** | High benefit above threshold; provider will often absorb hardware cost | Effective regardless of provider mix |
| **Facility space and power** | Required | Not required |
| **BGP and peering operations** | Minimal | Required |
| **IXP presence** | Not required | Needed for most peering |
| **Operational model** | Provider manages hardware | You manage routing policy |
| **Time to deploy** | Weeks to months (hardware logistics) | Days to weeks (IXP port, peering config) |
| **Multi-provider coverage** | One deployment per provider | One IXP presence covers many providers |

**A practical heuristic:** If you have one content provider contributing a large fraction of your total traffic and you have facility space, the embedded model is typically the fastest path to impact. If you're present at an IXP or want to reduce transit costs across multiple providers simultaneously, peering provides more leverage.

Many networks use a hybrid: embedded appliances for the highest-volume provider relationships, peering for the broader long tail of content traffic.

---

## Operational Considerations

### Monitoring What You Localized

Localization only delivers value if traffic is actually flowing through the local path. Confirm this by monitoring:

- Traffic volume on peering links or appliance uplinks
- BGP prefix counts and session state for peering relationships
- Transit traffic volume over time - a successful localization deployment should show a measurable decrease

If your transit traffic to a specific destination block did not decrease after a peering session came up, the routing policy may not be preferring the peering path. Check local preference configuration and confirm you are receiving the expected prefixes.

### Cache Fill Traffic

Embedded appliances pull content from provider origin infrastructure to populate their local cache. This fill traffic will appear on the appliance's uplinks and may traverse transit or peering paths depending on how the provider's origin infrastructure is reached and how your routing policy treats those sources. Understand what networks the fill traffic originates from and whether you want to route it differently from subscriber traffic.

### Failover and Redundancy

For embedded appliances: if the appliance is unreachable, subscriber requests fall back to the provider's origin infrastructure via your normal transit path. Verify this behavior during commissioning - a failure that results in blackholing rather than fallback is a significant subscriber impact event.

For peering: ensure transit backup routes exist for all prefixes learned from the peering neighbor. Test peer-down scenarios before treating the peering session as production-critical infrastructure.

---

## Getting Started

The path to a CDN localization partnership typically follows this sequence:

1. **Traffic analysis:** Identify which content providers contribute the largest share of your transit traffic. Most providers have a partner portal or NOC contact for discussing deployment options.

2. **Model selection:** Based on your traffic profile and infrastructure, determine whether embedded, peering, or a combination is the right fit.

3. **Technical prerequisites:** For peering, confirm IXP presence or arrange a PNI. For embedded appliances, identify facility space, power, and network connectivity for the hardware.

4. **BGP policy preparation:** Review and document your local preference, prefix filter, and failover policies before configuring the peering session.

5. **Validation:** After deployment, confirm traffic is flowing as expected. Compare transit volumes before and after. Verify failover behavior.

6. **Ongoing operations:** Monitor session state, traffic volumes, and prefix changes. CDN providers periodically update their prefix ranges - maintain your prefix filters accordingly.

---

*This document provides a general technical overview of CDN partnership models. Specific deployment requirements, hardware specifications, and operational procedures vary by provider. Contact your CDN partner's network operations team for provider-specific guidance.*
