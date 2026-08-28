"""Content of the NAKSHA detailed report.

Separate from the layout so wording can change without touching PDF plumbing.
Each entry is a (style, text) pair. Reference markers are written inline as [n]
and must match REFERENCES.

Note on framing: the routing engine's material efficiency is deliberately not
quoted as a headline. Telling a wire manufacturer the app reduces cable per house
argues against the proposal. The commercial case is capturing which brand gets
specified, not changing how much is consumed.
"""

TEAM = "D38N"
MEMBERS = ["Ayush Gupta"]
TITLE = "NAKSHA"
SUBTITLE = ("An augmented reality service that plans a home's wiring, "
            "and sells the wire")
TRACK = "Track 4: Digital Solutions for Consumer Engagement"

SYNOPSIS = """\
A family building a house does not know where anything should go. Not the \
sockets, not the switchboards, not the water heater point. The architect's \
drawing, where there is one, says almost nothing about services. So the \
decisions get made on site by whoever is standing there. Runs are improvised, \
material is mis-ordered, and nothing is written down. Around 42% of building \
fires in India are attributed to electrical faults [1], and with no record of \
what was laid, later renovation is guesswork.

NAKSHA is an app from V-Guard that closes that gap. The owner answers about \
eight questions, walks each room with the phone's LiDAR sensor, and gets a \
complete electrical design: every light, fan, socket and switchboard placed, the \
points grouped into circuits, the cable and breaker sized for each, and the \
quantity of wire the house will need. The same design is then projected onto the \
real walls in augmented reality, at full size, before anything is chased.

The design is not produced by a language model. A rule engine produces it, so \
every decision is traceable. The model only runs the conversation.

For the owner this replaces dependence on one electrician with a drawing, a \
quantity and a permanent record. For V-Guard it is a sales channel, not a \
product. It can be given away free because the revenue is the wire, the water \
heater and the chimney it specifies. Services are chosen once, during \
construction, and never re-shopped.

A working prototype exists. It designs a real surveyed room into three correctly \
sized circuits and a priced bill of quantities. A premium tier is also proposed, \
in which a trained partner projects the design onto the walls with a line laser \
so the electrician marks and chases directly against it.
"""

BODY = [

# ---------------------------------------------------------------- 1
("h1", "1. Story time"),

("p", "A few years ago my family used Berger's Express Painting service. It was "
      "expensive. It was not available in most pincodes. We used it in one room "
      "and nowhere else."),

("p", "My father still complains about the price. Years later, he remembers the "
      "brand exactly."),

("img", "exhibits/berger-express-painting.jpg|Berger's Express Painting "
        "service. A branded crew, branded equipment, inside the customer's "
        "house. The service never had to reach every pincode to do its work.|"
        "11"),

("p", "That is the insight. The service never scaled and never needed to. What "
      "it did was put a premium brand physically inside our house for two days, "
      "and that memory has outlasted every advertisement Berger ran since. "
      "Asian Paints proved the mechanism first with Beautiful Homes; Berger "
      "followed [2]. Neither was trying to become a painting contractor. They "
      "were buying a position."),

("p", "V-Guard is in the same place with a harder problem. It sells wires, "
      "water heaters, chimneys, RO purifiers, pumps and stoves. It is trusted. "
      "It is not the brand you consult before the walls close. On the Forbes "
      "India and TRA Research list of most respected consumer technology brands, "
      "V-Guard sits behind Havells, Bajaj Electricals, Syska and Cona [3]. That "
      "is permission the brand is not using."),

# ---------------------------------------------------------------- 2
("h1", "2. The problem"),

("p", "It is sharpest outside the metros, which is where the growth is. Land "
      "prices in tier 2 and tier 3 cities are expected to rise 25% to 100% over "
      "two to four years as metro prices peak [4], and those are markets where "
      "the owner builds the house rather than a developer."),

("b", "There is often no architect. Where a drawing exists it shows walls and "
      "rooms, not services."),

("b", "The electrician plans the installation, executes it, and is the only "
      "person who knows what was done."),

("b", "Nothing is recorded. Once the plaster is on, the information is gone."),

("b", "So the owner thinks ten times before drilling one hole in his own wall."),

("p", "Sockets end up where the furniture is not. Air conditioners get added "
      "later onto circuits never sized for them. And every one of those "
      "decisions settles which brand of wire, water heater and chimney goes into "
      "the house. V-Guard sells all of them and is present for none of it."),

# ---------------------------------------------------------------- 3
("h1", "3. What does the idea do?"),

("p", "The owner opens the app. It asks about eight questions: name, sanctioned "
      "load from the bill, bedrooms, occupants, how many air conditioners and "
      "where, which bathrooms need water heating, what the kitchen will have. "
      "Each question is written from the answers already given."),

("p", "Then the owner walks each room holding the phone. The LiDAR sensor "
      "measures walls, doors, windows and furniture. Nothing is typed."),

("p", "From the room and the answers the app produces:"),

("b", "A drawing, with every light, fan, socket, switchboard and appliance "
      "point placed, the conduit routed and the distribution board sited."),

("b", "A circuit schedule: which points share a circuit, the breaker rating, "
      "the cable size, the connected load and the voltage drop."),

("b", "A quantity: metres of cable by size, metres of conduit, counts of boxes "
      "and switchgear, and what it costs."),

("b", "An augmented reality view of the same design on the actual walls, at "
      "full size, before anything is cut."),

("p", "Each point is ticked off as it is installed. What remains is an as-built "
      "record: a permanent map of where the cables actually went. That is the "
      "thing which does not exist today."),

# ---------------------------------------------------------------- 4
("h1", "4. How it works"),

("p", "Three parts, and the separation between them is the whole design."),

("h2", "4.1 The conversation"),

("p", "A language model asks the questions. It runs on a server and produces "
      "one output: a profile of the household. What the family intends to own, "
      "not a wiring decision."),

("p", "This boundary matters more than anything else here. A model that "
      "hallucinates a cable size is a fire. So it is kept away from the "
      "engineering entirely, and if it is unreachable a fixed question set runs "
      "instead and the app behaves identically."),

("h2", "4.2 The design engine"),

("p", "Everything that could hurt somebody happens here, in explicit rules."),

("p", "Lighting counts come from the lumen method against the measured floor "
      "area and an illuminance target for the room type. Socket counts follow "
      "spacing rules. Points are grouped into lighting, power and dedicated "
      "circuits. The board is placed by solving for the position that minimises "
      "total cable, and conduit is routed as a rectilinear Steiner minimal tree, "
      "the same problem circuit board routers solve [5]."),

("p", "Sizing runs in a specific order: the breaker is chosen from the design "
      "current, then a conductor whose ampacity covers that breaker. The reverse "
      "order is a protection violation, because a breaker rated above the cable "
      "it protects will not trip before the cable overheats. Voltage drop is "
      "then checked and the conductor increased if it fails. Maximum demand is "
      "calculated with diversity and compared against the sanctioned load, so a "
      "house with three air conditioners on a 5 kW sanction is told while the "
      "walls are still open."),

("h2", "4.3 The augmented reality view"),

("p", "The design is authored on a floor plane in metres. To place it in the "
      "room the app needs to know where the room is, so the user taps two floor "
      "corners, which fixes position and rotation exactly. The ceiling height "
      "comes from the scan. Registration is manual and visible on purpose: "
      "automatic alignment drifts on a live site, and an overlay confidently in "
      "the wrong place is worse than one the user positioned himself. The "
      "authoritative output is always the dimensioned drawing, never the "
      "screen."),

# ---------------------------------------------------------------- 5
("h1", "5. NAKSHA as a service"),

("p", "The app is the free layer. Above it sits a paid one, and this is where "
      "the Berger comparison becomes literal."),

("p", "A trained V-Guard partner arrives with a 3D line laser. It mounts on a "
      "tripod or clamps to the wall, sits in the middle of the room, and "
      "projects the design onto the walls and ceiling as actual lines. The "
      "electrician marks and chases directly against the projection instead of "
      "measuring from a paper drawing. Socket heights, switchboard positions and "
      "conduit runs are set out in minutes, in the position the owner chose in "
      "augmented reality."),

("img", "exhibits/laser-projector.jpg|A 360 degree line laser with tripod and "
        "wall mount. Commodity hardware, a few thousand rupees, already used by "
        "tile and false ceiling contractors. It is the marking instrument, not "
        "the design tool.|8.5"),

("p", "This is not speculative. The equivalent exists at industrial scale in "
      "the United States. Dusty Robotics sends a small robot across a concrete "
      "slab printing the building model directly onto the floor, and has printed "
      "onto hundreds of millions of square feet [6]."),

("img", "exhibits/dusty-robotics.jpg|Dusty Robotics printing a building model "
        "onto a slab. It works on floors, which is where American layout is "
        "needed. Indian services run in walls and ceilings, so the same idea "
        "has to be projected rather than printed.|6.5"),

("p", "The distinction matters. Dusty prints on the floor because that is where "
      "American layout happens. In Indian construction the wiring is concealed "
      "in walls and ceilings, so a floor printer solves the wrong surface. A "
      "line laser projecting upward and outward is the correct instrument for "
      "the same job here."),

("p", "And as with Berger, this tier does not have to scale. A handful of "
      "trained partners in metro cities is enough. Its purpose is to make "
      "V-Guard the brand that turned up with equipment before the wall was "
      "closed. The app delivers the reach; the service delivers the "
      "positioning."),

# ---------------------------------------------------------------- 6
("h1", "6. What does this mean for the user?"),

("b", "He is not completely dependent on one electrician. He has a drawing, so "
      "a second opinion becomes possible."),

("b", "He has a 3D and augmented reality map of his own wiring, kept for the "
      "life of the building. Drilling a hole stops being a gamble."),

("b", "He knows what quantity of wire and switchgear the house needs, so he "
      "buys the right amount and overcharging becomes visible."),

("b", "He sees a brand that arrived before the wall closed rather than after "
      "something failed."),

("p", "The electrician is not displaced and the design does not assume he will "
      "be. He stays legally responsible for the installation. What he gets is "
      "the load calculation done, the sizes decided, the material list totalled, "
      "and a defensible answer when the owner asks why it costs what it costs."),

# ---------------------------------------------------------------- 7
("h1", "7. What does V-Guard get from all this?"),

("p", "Four things, in order of what they are worth."),

("b", "V-Guard stops being only a trusted brand and becomes a technology first "
      "one. That repositioning is hard to buy with advertising and cheap to buy "
      "with a working app."),

("b", "Every design becomes an order. The output is a material schedule in "
      "metres and units, mappable to V-Guard product codes. Being specified is a "
      "stronger position than advertising to whoever walks into a shop."),

("b", "The decision is captured years earlier, during construction, before the "
      "owner has any brand opinion. Nobody rewires a finished house."),

("b", "If the app reaches ordinary customers and local electricians, V-Guard "
      "gets first-hand market data: what is being installed, in which cities, at "
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
      "payouts [9]. Every major wire brand runs something similar, and all of "
      "them are points and rewards schemes. None puts a tool in the "
      "electrician's hand that does actual work."),

# ---------------------------------------------------------------- 8
("h1", "8. Does it actually work?"),

("p", "A prototype exists: an iOS application and a design engine. It has been "
      "run on a real room."),

("p", "The room is 15 feet by 12 feet with a 10 foot ceiling, surveyed and "
      "cross checked against a mesh scan that measured the footprint to within "
      "1.4%. It contains two lights, a ceiling fan, three switchboards, three "
      "sockets, an air conditioner and an existing MCB box. From those eleven "
      "points the engine produced three circuits: 6 A lighting on 1.5 sq mm, "
      "16 A power on 2.5 sq mm, and a dedicated 25 A circuit for the air "
      "conditioner on 4 sq mm. It routed the conduit, reported maximum demand of "
      "1,959 W against a 4,500 W sanction, priced the material, and raised no "
      "code violations."),

("p", "The 25 A circuit is the part worth reading. A one ton air conditioner "
      "would normally be given a 16 A breaker. The isolator actually fitted in "
      "that room is 25 A, so the engine took the larger device and raised the "
      "conductor to 4 sq mm, whose ampacity is exactly 25 A. A 2.5 sq mm cable "
      "under a 25 A breaker would have been a protection violation. That is the "
      "difference between a drawing and a decoration."),

("p", "Delivery cost is software cost. No field organisation, no equipment to "
      "maintain, nobody to place in every pincode. That is precisely why the app "
      "is the base layer and the laser service sits above it as an option."),

# ---------------------------------------------------------------- 9
("h1", "9. What it does not do yet"),

("b", "The scan captures one room at a time and separate captures share no "
      "coordinate frame. Room shapes and areas are measured; the arrangement "
      "between rooms is approximated. The schedule and quantities are unaffected "
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

# ---------------------------------------------------------------- 10
("h1", "10. Why this is worth doing"),

("p", "The components exist and the proposal is stronger for saying so. "
      "Automated electrical takeoff is mature, serving contractors who bid large "
      "projects. Robotic layout is solved, as Dusty Robotics shows. All of it "
      "serves Western commercial construction."),

("p", "The contribution here is positional. The user is the home owner, not an "
      "estimator, so the design is created by walking around rather than "
      "uploaded as a finished drawing. Indian practice and Indian codes are the "
      "rule set. The as-built record is produced, which no takeoff tool does, "
      "because its users leave site and never return. And it is monetised by a "
      "company that sells every product it touches."),

("p", "Construction is the largest single consumer of cable in India at about "
      "32% of demand [10], and residential construction is growing at roughly "
      "6.6% a year. That is the pipeline. NAKSHA puts V-Guard at the front of "
      "it, in the hand of the person deciding, at the one moment the decision is "
      "still open."),
]

REFERENCES = [
    "National Crime Records Bureau, Accidental Deaths and Suicides in India, "
    "on causes of fire accidents.",

    "Asian Paints, Beautiful Homes Service; Berger Paints, Express Painting.",

    "Forbes India and TRA Research, Most Respected Consumer Tech Brands.",

    "The Economic Times Brand Equity, on tier 2 and tier 3 land prices.",

    "M. Hanan, On Steiner's problem with rectilinear distance, SIAM Journal on "
    "Applied Mathematics, 1966.",

    "Dusty Robotics, FieldPrinter deployment figures.",

    "V-Guard Industries Limited, results for the year ended 31 March 2026.",

    "Motilal Oswal Financial Services, Cables and Wires sector update, 2026.",

    "V-Guard Industries Limited, Rishta programme for electricians and "
    "plumbers.",

    "CRU Group, on construction as a share of Indian cable demand.",
]
