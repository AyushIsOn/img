"""Content of the NAKSHA detailed report.

Two rules for anyone editing this file.

Do not quote the routing engine's material efficiency. Telling a wire
manufacturer the app reduces cable per house argues against the proposal. The
commercial case is which brand gets specified, not how much is consumed.

Do not add detail to the Berger story that was not in the source note. It is a
first person account and every embellishment is a thing to be caught on.
"""

TEAM = "TI3405_D38N"
MEMBERS = ["AYUSH GUPTA"]
TITLE = "NAKSHA"
SUBTITLE = ("An augmented reality service that plans a home's wiring, "
            "and sells the wire")
DATE = "28 August 2026"

# Paste the folder or file link once the demo recording is uploaded.
DRIVE_LINK = "https://drive.google.com/file/d/1eBcNDpe4yKDJRv7YKbVwHbuWcS2VZ9WY/view?usp=sharing"

SYNOPSIS = """\
A family building a house does not know where anything should go. Not the \
sockets, not the switchboards, not the water heater point. The architect's \
drawing, where there is one, says almost nothing about services. So the \
decisions get made on site by whoever is standing there. Runs are improvised, \
material is mis-ordered, and nothing is written down. Mumbai Fire Brigade, \
across 26,855 incidents over five years, attributes nearly three in four to \
electrical faults [1], and with no record of what was laid, later renovation is \
guesswork.

NAKSHA is an app from V-Guard. The owner answers about eight questions, walks \
each room with the phone's LiDAR sensor, and gets a complete electrical design: \
every light, fan, socket and switchboard placed, the points grouped into \
circuits, the cable and breaker sized for each, and the quantity of material the \
house needs. The design is then projected onto the real walls in augmented \
reality, at full size, before anything is chased.

The design is not produced by a language model. A rule engine produces it, so \
every decision is traceable. The model only runs the conversation.

For the owner this replaces dependence on one electrician with a drawing, a \
quantity and a permanent record. For V-Guard it is a sales channel rather than a \
product. It can be given away free, because the revenue is the wire, the water \
heater and the chimney it specifies. Services are chosen once, during \
construction, and never re-shopped.

A working prototype exists and designs a real surveyed room into three correctly \
sized circuits and a priced bill of quantities. A paid tier is also proposed, in \
which a trained partner projects the design onto the walls with a line laser so \
the electrician marks and chases against it.
"""

BODY = [

# ---------------------------------------------------------------- 1
("h1", "1. The problem"),

("p", "Sharpest outside the metros, which is where the growth is. Land prices "
      "in tier 2 and tier 3 cities are expected to rise 25% to 100% over two to "
      "four years as metro prices peak [4], and those are markets where the "
      "owner builds the house, not a developer."),

("b", "Often no architect. Where a drawing exists it shows walls and rooms, "
      "not services."),

("b", "The electrician plans it, executes it, and is the only person who knows "
      "what was done."),

("b", "Nothing is recorded. Once the plaster is on, the information is gone."),

("b", "The owner thinks ten times before drilling one hole in his own wall."),

("b", "Sockets end up where the furniture is not. Air conditioners get added "
      "later onto circuits never sized for them."),

("p", "Every one of those decisions settles which brand of wire, water heater "
      "and chimney goes into the house. V-Guard sells all of them and is present "
      "for none of it."),

# ---------------------------------------------------------------- 2
("h1", "2. What NAKSHA does"),

("b", "Asks about eight questions: sanctioned load, bedrooms, occupants, how "
      "many air conditioners and where, which bathrooms need water heating, what "
      "the kitchen will have. Each question is written from the answers already "
      "given."),

("b", "The owner walks each room holding the phone. LiDAR measures walls, "
      "doors, windows and furniture. Nothing is typed."),

("b", "Produces a drawing: every light, fan, socket, switchboard and appliance "
      "point placed, conduit routed, distribution board sited."),

("b", "Produces a circuit schedule: which points share a circuit, breaker "
      "rating, cable size, connected load, voltage drop."),

("b", "Produces a bill of quantities: metres of cable by size, metres of "
      "conduit, counts of boxes and switchgear, priced."),

("b", "Projects the same design onto the actual walls in augmented reality, at "
      "full size, before anything is cut."),

("b", "Each point is ticked off as installed. What remains is an as-built "
      "record, a permanent map of where the cables actually went. That does not "
      "exist today."),

# ---------------------------------------------------------------- 3
("h1", "3. How it works"),

("img", "exhibits/flow-diagram.png|How the three stages fit together. The "
        "language model handles the conversation and hands over a profile. "
        "Everything that could hurt somebody happens in the rule engine, where "
        "each decision is traceable to a rule.|15.5"),

("h2", "3.1 The conversation"),

("b", "A language model asks the questions and produces one output: a profile "
      "of the household. What the family intends to own, not a wiring decision."),

("b", "This boundary matters more than anything else here. A model that "
      "hallucinates a cable size is a fire."),

("b", "If the model is unreachable, a fixed question set runs instead and the "
      "app behaves identically."),

("h2", "3.2 The design engine"),

("b", "Lighting counts from the lumen method against measured floor area and an "
      "illuminance target per room type. Socket counts from spacing rules."),

("b", "Points grouped into lighting, power and dedicated circuits."),

("b", "Distribution board placed by solving for the position that minimises "
      "total cable."),

("b", "Conduit routed as a rectilinear Steiner minimal tree, the same problem "
      "circuit board routers solve [5]."),

("b", "Sizing in a fixed order: breaker chosen from the design current, then a "
      "conductor whose ampacity covers that breaker. The reverse order is a "
      "protection violation, because a breaker rated above the cable it protects "
      "will not trip before the cable overheats."),

("b", "Voltage drop checked and the conductor increased if it fails. Maximum "
      "demand calculated with diversity and compared against the sanctioned "
      "load, so three air conditioners on a 5 kW sanction is flagged while the "
      "walls are still open."),

("h2", "3.3 The augmented reality view"),

("b", "The user taps two floor corners, which fixes position and rotation "
      "exactly. Ceiling height comes from the scan."),

("b", "Registration is manual and visible on purpose. Automatic alignment "
      "drifts on a live site, and an overlay confidently in the wrong place is "
      "worse than one the user positioned himself."),

("b", "The authoritative output is always the dimensioned drawing, never the "
      "screen."),

# ---------------------------------------------------------------- 4
("h1", "4. NAKSHA as a service"),

("p", "The app is the free layer. Above it sits a paid one."),

("b", "A trained V-Guard partner arrives with a 3D line laser. It mounts on a "
      "tripod or clamps to the wall, sits in the middle of the room, and "
      "projects the design onto the walls and ceiling as real lines."),

("b", "The electrician marks and chases against the projection instead of "
      "measuring from paper. Socket heights, switchboard positions and conduit "
      "runs are set out in minutes."),

("b", "Commodity hardware, a few thousand rupees, already used by tile and "
      "false ceiling contractors."),

("img", "exhibits/laser-projector.jpg|A 360 degree line laser with tripod and "
        "wall mount. The marking instrument, not the design tool.|8.5"),

("p", "This is not speculative. The equivalent exists at industrial scale in "
      "the United States. Dusty Robotics sends a small robot across a concrete "
      "slab printing the building model directly onto the floor, and has printed "
      "onto hundreds of millions of square feet [6]."),

("img", "exhibits/dusty-robotics.jpg|Dusty Robotics printing a building model "
        "onto a slab. It works on floors, which is where American layout is "
        "needed.|6.5"),

("b", "The distinction matters. Dusty prints on the floor because that is where "
      "American layout happens. Indian services run in walls and ceilings, so a "
      "floor printer solves the wrong surface."),

("b", "A line laser projecting upward and outward is the correct instrument for "
      "the same job here."),

("b", "This tier does not have to scale. A handful of trained partners in metro "
      "cities is enough. Its purpose is positioning, not revenue."),

# ---------------------------------------------------------------- 5
("h1", "5. What this means for the user"),

("b", "Not completely dependent on one electrician. He has a drawing, so a "
      "second opinion becomes possible."),

("b", "A 3D and augmented reality map of his own wiring, kept for the life of "
      "the building. Drilling a hole stops being a gamble."),

("b", "He knows what quantity of wire and switchgear the house needs, so he "
      "buys the right amount and overcharging becomes visible."),

("b", "He sees a brand that arrived before the wall closed rather than after "
      "something failed."),

("b", "The electrician is not displaced. He stays legally responsible. What he "
      "gets is the load calculation done, the sizes decided, the material list "
      "totalled, and a defensible answer when the owner asks why it costs what "
      "it costs."),

("box", "Story time\n"
        "A few years ago my family used Berger's Express Painting service. It "
        "was expensive. It was not available in most pincodes. We used it in one "
        "room and nowhere else. To this day my father still curses Berger "
        "paint.\n"
        "He also still remembers the brand, exactly, years later. The service "
        "never scaled and never needed to. What it did was put a premium brand "
        "physically inside our house for two days. Asian Paints proved the "
        "mechanism first with Beautiful Homes and Berger followed [2]. Neither "
        "was trying to become a painting contractor. They were buying a "
        "position."),

("img", "exhibits/berger-express-painting.jpg|Berger's Express Painting "
        "service. A branded crew with branded equipment, inside the customer's "
        "house.|11"),

# ---------------------------------------------------------------- 6
("h1", "6. What V-Guard gets from this"),

("b", "V-Guard stops being only a trusted brand and becomes a technology first "
      "one. On the Forbes India and TRA Research list of most respected consumer "
      "technology brands, V-Guard currently sits behind Havells, Bajaj "
      "Electricals, Syska and Cona [3]. That repositioning is hard to buy with "
      "advertising and cheap to buy with a working app."),

("b", "Every design becomes an order. The output is a material schedule in "
      "metres and units, mappable to V-Guard product codes. Being specified "
      "beats advertising to whoever walks into a shop."),

("b", "The decision is captured years earlier, during construction, before the "
      "owner has any brand opinion. Nobody rewires a finished house."),

("b", "First hand market data: what is being installed, in which cities, at "
      "what load, in what quantity. Nobody in this category has that."),

("p", "The margin case is why it is worth doing. In FY26 V-Guard's revenue grew "
      "about 7% to Rs 5,966 crore while profit after tax fell 1.7% to Rs 308 "
      "crore, on an EBITDA margin of 8.8% [7]. Growth is not the problem; margin "
      "is. Meanwhile the organised share of the cables and wires industry rose "
      "from roughly 67% in FY22 to about 80% in FY26 [8]. A documented design "
      "accelerates that shift, because you cannot write a conductor size on a "
      "drawing and then buy loose unbranded wire against it."),

("p", "The channel also already exists. V-Guard runs Rishta, a loyalty "
      "programme for electricians and plumbers with QR scanning and instant "
      "payouts [9]. Every major wire brand runs something similar and all of "
      "them are points and rewards schemes. None puts a tool in the "
      "electrician's hand that does actual work."),

# ---------------------------------------------------------------- 7
("h1", "7. Does it actually work?"),

("p", "A prototype exists: an iOS application and a design engine. It has been "
      "run on a real room, 15 feet by 12 feet with a 10 foot ceiling, surveyed "
      "and cross checked against a mesh scan that measured the footprint to "
      "within 1.4%."),

("b", "Eleven measured fittings: two lights, a ceiling fan, three "
      "switchboards, three sockets, an air conditioner, an existing MCB box."),

("b", "Three circuits produced: 6 A lighting on 1.5 sq mm, 16 A power on "
      "2.5 sq mm, dedicated 25 A for the air conditioner on 4 sq mm."),

("b", "Maximum demand 1,959 W against a 4,500 W sanction. Material priced. No "
      "code violations raised."),

("p", "The 25 A circuit is the part worth reading. A one ton air conditioner "
      "would normally get a 16 A breaker. The isolator actually fitted in that "
      "room is 25 A, so the engine took the larger device and raised the "
      "conductor to 4 sq mm, whose ampacity is exactly 25 A. A 2.5 sq mm cable "
      "under a 25 A breaker would have been a protection violation. That is the "
      "difference between a drawing and a decoration."),

("p", "Delivery cost is software cost. No field organisation, no equipment to "
      "maintain, nobody to place in every pincode. That is why the app is the "
      "base layer and the laser service sits above it as an option."),

# ---------------------------------------------------------------- 8
("h1", "8. What it does not do yet"),

("b", "The scan captures one room at a time and separate captures share no "
      "coordinate frame. Room shapes and areas are measured; the arrangement "
      "between rooms is approximated. Schedule and quantities are unaffected, "
      "because they depend on area and room type."),

("b", "Augmented reality accuracy on a live site is unproven. The promise is "
      "dimensioned guidance, not millimetre placement."),

("b", "Only the electrical layer is built. Water, gas and duct routing use the "
      "same geometry and the same router, but are not implemented."),

("b", "Liability needs legal structuring. The tool must be a decision aid a "
      "licensed contractor signs off, not the designer of record."),

("b", "Adoption, not technology, is the real risk. If it does not visibly save "
      "an electrician time from the first use, it will be ignored by the people "
      "who decide what gets bought."),

("p", "Construction is the largest single consumer of cable in India at about "
      "32% of demand [10]. That is the pipeline. NAKSHA puts V-Guard at the "
      "front of it, in the hand of the person deciding, at the one moment the "
      "decision is still open."),
]

REFERENCES = [
    "Addressing India's electrical fire risks, The Hindu, 2026. Delhi Fire "
    "Service attributes over 80% of fires in the capital to electrical faults; "
    "Mumbai Fire Brigade, analysing 26,855 incidents over five years, "
    "attributes nearly three in four to the same cause.",

    "Asian Paints, Beautiful Homes Service; Berger Paints, Express Painting.",

    "Forbes India and TRA Research, Most Respected Consumer Tech Brands, as "
    "reported in Forbes India, Havells: Making a Brand of a Commodity.",

    "Beyond metros, a big realty boom is brewing, The Economic Times Brand "
    "Equity, on tier 2 and tier 3 land prices.",

    "M. Hanan, On Steiner's problem with rectilinear distance, SIAM Journal on "
    "Applied Mathematics, vol. 14, no. 2, 1966, pp. 255 to 265.",

    "Dusty Robotics, FieldPrinter, company deployment figures.",

    "V-Guard Industries Limited, audited results for the quarter and year "
    "ended 31 March 2026, investor presentation.",

    "Motilal Oswal Financial Services, Cables and Wires sector update, June "
    "2026, on industry size and the organised share.",

    "V-Guard Industries Limited, Rishta loyalty programme for electricians and "
    "plumbers, application listings.",

    "CRU Group, State policies and clean energy boost India's cable market, on "
    "construction as a share of Indian cable demand.",
]
