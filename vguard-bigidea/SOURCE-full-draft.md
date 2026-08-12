# INVIDIA CORE: Power Protection That Disappears Into the Wall

### Track 1 — Reimagining the Stabilizer for the Next Decade

*Executive Summary — V-Guard Big Idea Tech Design Contest 2026*

---

## 1. The Idea

Every Indian home with a stabilizer has the same absurdity on its wall: **two boxes doing one job at the same place.**

There is the distribution board, mounted after the meter, holding the MCBs and RCCB. And there is the stabilizer — either a plug-in box behind the air conditioner, or a mainline unit bolted beside the DB. Two enclosures, two sets of terminals, two installations, two things the electrician wires, two things the customer looks at.

V-Guard already manufactures both. **Invidia+** is their next-generation smart distribution board — it displays live voltage, shows RCCB status, and raises alerts. **VMT 500/1000 Plus** are their mainline stabilizers, installed in the input line. The company sells the sensing box and the correcting box separately, to the same customer, for the same wall.

**INVIDIA CORE collapses them into one.** A distribution board that does not merely *report* voltage but *corrects* it — with MCB, RCCB, surge protection and solid-state voltage regulation on a single DIN rail inside a single enclosure. Power protection stops being an appliance the customer buys and becomes **infrastructure the building already has.**

---

## 2. The Insight That Makes It Work

The obvious objection to putting a stabilizer in a DB is heat and weight. A whole-home relay-tap autotransformer for an 8–10 kVA connection is several kilograms of copper and iron dissipating real power inside a sealed plastic box. That approach cannot work, and we are not proposing it.

**The distribution board is the only location in the entire home where selective, per-circuit conditioning is physically possible.** That single fact changes the engineering problem:

| Approach | What it must regulate | Consequence |
|---|---|---|
| Plug-in stabilizer | One appliance | Ugly, per-appliance cost, retail afterthought |
| Mainline stabilizer | **The entire house, 8–10 kVA** | Heavy, hot, expensive |
| **INVIDIA CORE** | **Only the 2–3 circuits that need it** | **~3 kVA. Small, cool, cheap** |

A DB already splits the supply into separate outgoing ways. So you regulate the air-conditioner circuit and the refrigerator circuit — the loads with real motors and real compressors — and leave the lighting, fan and socket circuits unregulated, because LED drivers and BLDC fans are universal-input and do not need it.

**You have just cut the regulation requirement by roughly two-thirds before designing anything.**

Then apply the second reduction. Instead of processing the full load through a transformer, use a **series voltage-injection topology**: the converter is wired in series with the circuit and synthesises only the *correction* voltage, not the whole waveform. To correct ±25% on a 3 kVA circuit, the converter itself handles roughly 750 VA. Academic work validates this class of direct AC-AC compensator with both step-up and step-down capability ([Applied Sciences, 2021](https://www.mdpi.com/2076-3417/11/24/11944/html)), and a recent field evaluation of intelligent solid-state voltage regulators in low-voltage distribution networks reports measurable improvement in voltage profile and about 2.3% reduction in power loss ([Nature, 2026](https://www.nature.com/articles/s41598-026-43198-0)).

**Net effect: from ~8 kVA of hot iron to under 1 kVA of solid-state switching.** That is the difference between "impossible in a DB" and "fits on a DIN rail."

And it delivers something a tap-changing stabilizer fundamentally cannot: **continuous correction with no voltage steps, no relay chatter, no dead-band, and no audible clicking** — plus the same silicon can perform surge clamping and power-factor correction.

---

## 3. Why Now

**The category is not dying — but it is commoditising.** The Indian voltage stabilizer market was valued at **USD 770.65 million in 2025, forecast to reach USD 1,202.60 million by 2034 at 5.07% CAGR** ([IMARC](https://www.imarcgroup.com/india-voltage-stabilizer-market)), driven largely by air-conditioner penetration still at only around 8% of households against 13.3 million AC units sold in 2025.

The problem is margin, not volume. V-Guard's FY25-26 revenue grew **7.0% to ₹5,966 crore while PAT fell 1.7% to ₹308 crore** ([V-Guard Q4 FY25-26](https://www.vguard.in/uploads/investor_relations/V-GUARD-INDUSTRIES-Q4-RESULTS-PRESENTATION-2026.pdf)). A relay-tap stabilizer is a commodity sold on price and warranty. A certified distribution board with integrated regulation is not.

**Two new problems also arrive at exactly this location.** Rooftop solar under PM Surya Ghar has crossed **50 lakh installations** — against 7.94 lakh in the previous decade — creating reverse power flow and feeder-end voltage rise that a one-directional appliance stabilizer was never designed for. And home EV charging is straining household electrical envelopes; an AEEE/Kazam study warns residential charging could become the **biggest hurdle to India's EV push**, citing inadequate sanctioned loads, poor earthing and ageing wiring. Both are *board-level* problems, not appliance-level ones.

---

## 4. Novelty and Innovation — Stated Honestly

We did not invent any of the constituent technologies, and the proposal is stronger for saying so plainly.

- **Solid-state stabilisers are commercial.** Sollatek's AVR is a microprocessor-controlled solid-state regulator handling −30% to +22% input and correcting at 1250 V/second ([Sollatek](https://www.sollatek.com/range/voltage-protection/autotmatic-voltage-regulator/)). The technology works and is proven in market.
- **DIN-rail stabilisers exist** — but as generic, relay-based industrial modules from commodity suppliers, not as integrated residential consumer units, and not from any mainstream Indian brand.
- **Series-injection AC-AC compensation is well-published** in the academic literature.
- **Smart DBs exist, including V-Guard's own Invidia+** — but they *measure and report*. None *correct*.

**Our novelty sits in four specific places:**

**① Architectural.** Nobody has combined protection (MCB/RCCB/SPD) and correction (voltage regulation) into a single certified residential consumer unit. The pieces are all mature; the integration is absent.

**② The per-circuit insight.** Selective regulation of only the circuits that need it is what makes DB integration thermally and economically feasible. This is only possible at the board — and it is the core engineering contribution.

**③ Channel.** This is the commercially decisive point and it is discussed in §6.

**④ Portfolio fit unique to V-Guard.** V-Guard is one of very few Indian companies manufacturing stabilizers, switchgear, distribution boards, *and* wires and cables. They own both halves of this product already. For almost any competitor this would be an acquisition; for V-Guard it is an integration.

---

## 5. Technology

**Topology.** A series-connected AC-AC voltage compensator per regulated way. A low-VA injection transformer or transformerless half-bridge synthesises a correction voltage that adds to or subtracts from the line, under closed-loop control against a 230V reference. Because the converter processes only the correction fraction, efficiency in the regulated path stays high and dissipation stays low.

**Thermal design — the honest core challenge.** Three mitigations: partial-power processing means far less heat to begin with; SiC or GaN switching devices reduce conduction and switching losses; and the module is designed as a **thermally isolated DIN-rail block with its own finned heatsink and a vented enclosure section**, physically separated from the MCB/RCCB rail so that regulator heat never derates the protective devices. Continuous internal temperature monitoring derates output before anything approaches limits.

**Failsafe bypass.** Non-negotiable. A normally-closed relay bypasses the regulator on fault, over-temperature or loss of control power, so the circuit reverts to a plain protected feed. **The board must never fail into an unpowered state**, and a regulator fault must never compromise the protective devices sharing the enclosure.

**Modularity, sizing and scalability.** There is deliberately **no central stabilizer inside the board.** The design is N independent per-way modules, which resolves the three questions this architecture always attracts:

- **How is capacity guaranteed if a homeowner loads up a circuit?** Each module is rated to **the MCB protecting its way, not to the expected load.** A 16A MCB means that circuit physically cannot exceed 16A — so no combination of appliances can overload the module. The protective device already in the enclosure *is* the capacity guarantee.
- **What if the regulated circuit also carries lights and other minor loads?** Series injection processes only the correction fraction of whatever current actually flows, so a few hundred watts of incidental load costs almost nothing. Regulating it is unnecessary, not harmful.
- **What happens when the customer buys another air conditioner?** The electrician clips on another module. **No board replacement and no rewiring of existing circuits.** This requires the board to ship with reserved DIN width and a pre-wired regulator bus — a design requirement, not an afterthought. Because capacity is per-way rather than pooled, there is no central rating to outgrow.

**Overload behaviour.** On overcurrent, over-temperature or inrush beyond headroom, the module reverts to unregulated pass-through and logs the event. The circuit keeps working. **The regulator must never be the component that trips the house.**

**Intelligence, kept modest and honest.** The board already sees per-circuit voltage and current. That enables genuinely useful, low-risk functions: per-circuit energy metering, sag/swell and surge event logging, detection of rising circuit impedance from a loosening connection, and load-shed sequencing so an EV charger plus geyser plus AC never breaches sanctioned load. We deliberately avoid over-claiming AI here — the value is in the power electronics; the electronics simply make the data available.

---

## 6. Consumer and Business Value

### The channel argument — the most important point in this document

A stabilizer is a **retail afterthought.** The customer buys an AC, then remembers they need a stabilizer, then walks into a shop and compares prices across brands. It is a low-margin, high-competition, brand-fragile transaction.

A distribution board is **specified by the electrician or builder during construction**, before the customer has any opinion, and it is never price-shopped by the homeowner. There is no comparison moment.

> **Integrating the stabilizer into the DB moves power protection out of the price-comparison retail aisle and into the electrician's specification decision at construction time.**

That is a structurally better business, and V-Guard already owns that channel through its switchgear and wires business. It also captures the customer *years earlier* — at wiring stage rather than at appliance-purchase stage — and makes the attachment durable, because nobody rips out a distribution board to save ₹1,500.

### Consumer value

- **One box instead of two.** No stabilizer on the wall, no visible wiring, nothing behind the fridge.
- **Whole-circuit protection**, so a new appliance on a protected circuit is covered automatically with no additional purchase.
- **No relay clicking and no voltage steps** — continuous correction, which tap-changers cannot deliver.
- **Cleaner homes.** For the growing premium and interior-designed segment, eliminating a wall-mounted appliance is a genuine selling point.
- **Future-ready** for solar reverse flow and EV load management, both of which are board-level problems.

### Business value

- **Margin repair** on a commoditising category, via a certified switchgear product rather than a retail commodity.
- **Higher realisation per home:** a modular board plus two regulator modules replaces a single low-margin stabilizer sale.
- **Incremental upsell** as customers add modules for new appliances.
- **Defensible against competitors** who make switchgear but not stabilizers, or stabilizers but not switchgear.

---

## 7. Prototype Plan (Phase 3)

1. **Single-way series-injection regulator** — a 3 kVA circuit regulator built around a ~750 VA converter, closed-loop to 230V ±5%, on a variac-driven bench simulating 170–280V input.
2. **Measured performance curves** — output regulation versus input voltage, efficiency versus load, and **step response compared side-by-side against a commercial relay-tap stabilizer**, to demonstrate continuous versus stepped correction.
3. **Thermal validation** — the decisive test. Thermocouple mapping inside a standard 8-way DB enclosure at full load, confirming MCB/RCCB ambient stays within rated limits.
4. **Failsafe bypass demonstration** — forced fault and over-temperature events showing clean reversion to protected pass-through.
5. **Mechanical mock-up** — CAD and 3D-printed DIN module showing the board fits a standard recess.

---

## 8. Risks and Honest Limitations

- **Thermal management is the make-or-break risk**, not an afterthought. If the module cannot hold enclosure ambient within MCB derating limits at full load, the concept fails. Our per-circuit and partial-power choices exist specifically to make this tractable, but it must be proven experimentally, which is why it is the primary prototype objective.
- **Certification is a genuine barrier.** DBs are certified under IS 13032 and related standards; stabilizers under IS 9815. A combined unit is effectively a new product category and will require engagement with BIS. This is a real timeline cost, not a footnote.
- **Cost.** Solid-state regulation at 3 kVA is more expensive per kVA than relay-tap iron at low volume. The economics depend on the per-circuit reduction and on scale; at launch this is a premium product, not a mass one.
- **Safety conservatism.** Adding an active, heat-generating power converter into the enclosure that houses the home's protective devices demands a higher safety bar than either product faces alone. The failsafe bypass is mandatory, not optional.
- **Diminishing voltage problem.** Grid quality is improving under RDSS, and modern appliances tolerate wider input ranges. The long-run case rests less on classical voltage correction and more on the board becoming the home's power-quality and load-management node — which is why the architecture is designed for solar and EV conditions, not just low mains voltage.
- **No sub-circuit selectivity — the sharpest practical limitation.** A distribution board cannot see inside a circuit. If an air conditioner shares an outgoing way with lights and sockets, the board cannot regulate the AC alone. The correct remedy is a **dedicated way for the AC**, which Indian wiring practice already calls for on heavy loads and which is why air conditioners normally get their own 16A/20A MCB in properly built homes. Where legacy wiring makes that impractical, a plug-in stabilizer remains the right answer for that one appliance, and the two products coexist without conflict. **This positions INVIDIA CORE primarily at new construction and rewiring rather than at messy retrofit** — which is consistent with, not contrary to, the channel strategy in §6, since circuit separation is decided at wiring stage anyway.
- **We are not first to any component.** Solid-state stabilisers, DIN-rail regulators, and smart DBs all exist. Our contribution is the integration, the per-circuit architecture, and the channel repositioning.
