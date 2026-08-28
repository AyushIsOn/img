"""Content of the NAKSHA detailed report.

Kept separate from the layout code so the wording can be edited without going
anywhere near the PDF plumbing. Every paragraph is a (style, text) pair.

Reference markers are written inline as [n] and must match REFERENCES below.
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
drawing, if there is one, says almost nothing about services, so the decisions \
get made on site by whoever is standing there. Runs are improvised, material is \
mis-ordered, and nothing is written down. Around 42% of building fires in India \
are attributed to electrical faults [1], and with no record of what was laid, \
any later renovation is guesswork.

NAKSHA is an app from V-Guard that closes that gap. The owner answers a short \
set of questions, scans each room with the phone's LiDAR sensor, and receives a \
complete electrical design: where every light, fan, socket and switchboard goes, \
how the points group into circuits, what cable and breaker each circuit needs, \
and how many metres of wire the house will consume. The same design is then \
projected onto the real walls in augmented reality, so it can be seen at full \
size before anything is chased or plastered.

The design itself is not produced by a language model. A rule engine does it, \
so every decision can be traced. The model's only job is the conversation.

For the owner this replaces total dependence on one electrician with a drawing, \
a quantity and a permanent record. For V-Guard it is a sales channel rather than \
a product: it can be given away free because the revenue is the wire, the water \
heater and the chimney it specifies. A working prototype exists. It designs a \
real surveyed room, and across three house types it shows that routing conduit \
as a shared tree instead of one run per point saves a mean of 45.8% of cable \
length, with a further 7.7% from siting the board properly.
"""

BODY = [

# ---------------------------------------------------------------- 1
("h1", "1. Story time"),

("p", "A few years ago my family used Berger's interior painting service. It "
      "was expensive. It was not available in most pincodes. We used it in one "
      "room of the house and nowhere else."),

("p", "My father still curses the price of that paint. Years later, he "
      "remembers the brand exactly."),

("p", "That is the whole insight. The service never scaled. It did not need "
      "to. What it did was put a premium brand physically inside our house for "
      "two days, and that memory outlasted every advertisement Berger ran in "
      "the same period. Asian Paints had already proved the mechanism with "
      "Beautiful Homes, and Berger followed it with Express Painting [2]. "
      "Neither company was trying to become a painting contractor. They were "
      "buying a position."),

("p", "V-Guard is in a similar place, with a harder problem. It sells wires, "
      "water heaters, chimneys, RO purifiers, pumps and gas stoves. It is "
      "trusted. It is not seen as the brand you consult before the walls close. "
      "On the Forbes India and TRA Research list of most respected consumer "
      "technology brands, V-Guard sits behind Havells, Bajaj Electricals, Syska "
      "and Cona [3]. That is a brand with permission it is not using."),

("p", "NAKSHA is the same move as Beautiful Homes, except it costs software "
      "money rather than field money, and it is aimed at the one moment when a "
      "home owner has to decide which brand goes into the wall."),

# ---------------------------------------------------------------- 2
("h1", "2. The problem"),

("p", "This is sharpest outside the metros, which is also where the growth is. "
      "Land prices in tier 2 and tier 3 cities are expected to rise 25% to 100% "
      "over the next two to four years as metro prices peak [4], and those are "
      "markets where houses are built by the owner rather than by a developer."),

("b", "There is often no architect. Where there is a drawing, it shows walls "
      "and rooms, not services."),

("b", "The electrician plans the installation, executes it, and is the only "
      "person who knows what was done."),

("b", "Nothing is recorded. Once the plaster is on, the information is gone."),

("b", "So the new owner has to think ten times before drilling a single hole "
      "in his own wall."),

("p", "The consequences are not only inconvenience. Roughly 42% of building "
      "fires in India are attributed to electrical faults [1], and a NITI Aayog "
      "survey found 28% of households dissatisfied with the quality of their "
      "electricity supply as recently as 2023 [5]. Sockets end up where the "
      "furniture is not. Air conditioners get added later onto circuits that "
      "were never sized for them."),

("p", "For V-Guard the same moment is a commercial one. Every one of those "
      "decisions settles which brand of wire, water heater, chimney and stove "
      "ends up in the house. V-Guard sells all of them and is present for none "
      "of it."),

# ---------------------------------------------------------------- 3
("h1", "3. What does the idea do?"),

("p", "The owner opens the app. It asks a short series of questions: name, "
      "sanctioned load from the electricity bill, how many bedrooms, how many "
      "people, how many air conditioners and in which rooms, which bathrooms "
      "need water heating, what the kitchen will have. Roughly eight questions, "
      "each one written from the answers already given."),

("p", "Then the owner walks each room holding the phone. The LiDAR sensor "
      "measures the walls, the doors, the windows and the furniture. Nothing is "
      "typed in."),

("p", "From the room and the answers the app produces four things:"),

("b", "A drawing. Every light, fan, socket, switchboard and appliance point "
      "positioned, with the conduit routed between them and the distribution "
      "board sited."),

("b", "A circuit schedule. Which points share a circuit, the breaker rating, "
      "the cable size, the connected load and the voltage drop on each."),

("b", "A quantity. Metres of cable by size, metres of conduit, counts of "
      "boxes and switchgear, and what it costs."),

("b", "An augmented reality view. The same design projected onto the actual "
      "walls and ceiling at full size, so it can be walked through before "
      "anything is cut."),

("p", "As each point is confirmed on site, it is ticked off. What remains at "
      "the end is an as-built record: a permanent map of where the cables "
      "actually went, which is the thing that does not exist today."),

# ---------------------------------------------------------------- 4
("h1", "4. How it works"),

("p", "There are three parts, and the division between them is deliberate."),

("h2", "4.1 The conversation"),

("p", "A language model asks the questions. It runs on a server, holds no "
      "engineering knowledge, and produces one thing: a profile of the "
      "household. Its output is a structured record of what the family intends "
      "to own, not a wiring decision."),

("p", "This boundary matters more than anything else in the design. A model "
      "that hallucinates a cable size is a fire. So the model is not allowed "
      "near the engineering, and if the model is unreachable a fixed set of "
      "questions runs instead and the app behaves identically."),

("h2", "4.2 The design engine"),

("p", "Everything that could hurt somebody happens here, in explicit rules."),

("p", "Lighting counts come from the lumen method against the measured floor "
      "area and an illuminance target for the room type. Socket counts follow "
      "spacing rules. Points are grouped into lighting, power and dedicated "
      "circuits. The distribution board is then placed by solving for the "
      "position that minimises total cable, and conduit is routed between the "
      "points as a rectilinear Steiner minimal tree, which is the same problem "
      "printed circuit board routers solve [6]."),

("p", "Sizing is done in a specific order: the breaker is chosen first from "
      "the design current, then a conductor whose ampacity covers that breaker. "
      "The reverse order is a protection violation, because a breaker rated "
      "above the cable it protects will not trip before the cable overheats. "
      "Voltage drop is then checked and the conductor increased if it fails. "
      "Maximum demand is calculated with diversity factors and compared against "
      "the sanctioned load, so a house with three air conditioners on a 5 kW "
      "sanction is told so while the walls are still open."),

("h2", "4.3 The augmented reality view"),

("p", "The design is authored on a floor plane in metres. To place it in the "
      "room, the app needs to know where the room is. The user points at two "
      "corners of the floor and taps each, which fixes position and rotation "
      "exactly, and the ceiling height comes from the scan. Registration is "
      "manual and visible on purpose. Automatic alignment drifts on a live "
      "building site, and an overlay that is confidently in the wrong place is "
      "worse than one the user positioned himself. The authoritative output is "
      "always the dimensioned drawing, never the phone screen."),

# ---------------------------------------------------------------- 5
("h1", "5. What does this mean for the user?"),

("b", "He is no longer completely dependent on one electrician or contractor. "
      "He has a drawing, and a second opinion is now possible."),

("b", "He has a 3D and augmented reality map of his own wiring, kept for the "
      "life of the building. Drilling a hole stops being a gamble."),

("b", "He knows how much wire and how much switchgear the house will consume, "
      "so he buys the right quantity and overcharging becomes visible."),

("b", "He sees a brand that turned up before the wall was closed rather than "
      "after it failed. That is what a premium brand looks like from inside a "
      "house."),

("p", "The electrician is not displaced by this, and the design does not "
      "assume he will be. He remains legally responsible for the installation. "
      "What he gets is the load calculation done, the sizes decided, the "
      "material list totalled, and a defensible answer when the owner asks why "
      "it costs what it costs."),

# ---------------------------------------------------------------- 6
("h1", "6. What does V-Guard get from all this?"),

("p", "Four things, in order of how much they are worth."),

("b", "V-Guard stops being only a trusted brand and becomes a technology "
      "first one. That repositioning is very hard to buy with advertising and "
      "reasonably cheap to buy with a working app."),

("b", "Every design is an order. The output is a material schedule in metres "
      "and units that can be mapped to V-Guard product codes. Specifying "
      "material is a stronger commercial position than advertising to whoever "
      "walks into a shop."),

("b", "The decision is captured years earlier. Services are chosen during "
      "construction, before the owner has formed any brand opinion, and they "
      "are never re-shopped. Nobody rewires a finished house."),

("b", "If the app reaches ordinary customers and local electricians, V-Guard "
      "gets first-hand market information: what is actually being installed, "
      "in which cities, at what load, in what quantity. Nobody in this "
      "category has that today."),

("p", "The margin case is the reason this is worth doing at all. In FY26 "
      "V-Guard's revenue grew about 7% to Rs 5,966 crore while profit after tax "
      "fell 1.7% to Rs 308 crore, with an EBITDA margin of 8.8% [7]. The "
      "electricals segment, which contains wires, is more than 40% of revenue "
      "[8]. Meanwhile Polycab holds roughly a quarter of a cables and wires "
      "market worth about Rs 1 lakh crore [9][10]. V-Guard cannot win that "
      "market on price against a competitor several times its size in the "
      "category. Buying share with discounts is what compresses the margin "
      "further. Being specified on a drawing before anyone reaches the counter "
      "is the alternative."),

("p", "There is also a tailwind. The organised share of the cables and wires "
      "industry rose from about 67% in FY22 to about 80% in FY26 [10]. NAKSHA "
      "accelerates exactly that shift, because a documented design forces "
      "certified branded material. You cannot write a conductor size on a "
      "drawing and then buy loose unbranded wire against it."),

("p", "And the channel already exists. V-Guard runs Rishta, a loyalty "
      "programme for electricians and plumbers with QR scanning and instant "
      "payouts [11]. Every major wire brand runs something similar. All of them "
      "are points and rewards schemes. None of them puts a tool in the "
      "electrician's hand that does any actual work. NAKSHA can be distributed "
      "inside a channel V-Guard owns.")
,
# ---------------------------------------------------------------- 7
("h1", "7. Does it actually work?"),

("p", "A prototype exists: an iOS application and a design engine. It has "
      "been run on a real room."),

("p", "The room is 15 feet by 12 feet with a 10 foot ceiling, surveyed and "
      "cross checked against a mesh scan which measured the footprint to within "
      "1.4%. It contains two lights, a ceiling fan, three switchboards, three "
      "sockets, an air conditioner and an existing MCB box. From those eleven "
      "points the engine produced three circuits: a 6 A lighting circuit on "
      "1.5 sq mm, a 16 A power circuit on 2.5 sq mm, and a dedicated 25 A "
      "circuit for the air conditioner on 4 sq mm. It routed 41 metres of "
      "conduit, reported a maximum demand of 1,959 W against a 4,500 W "
      "sanction, and priced the material at Rs 12,081. No code violations were "
      "raised."),

("p", "The 25 A circuit is worth a sentence, because it shows the ordering "
      "rule doing its job. A one ton air conditioner would normally be given a "
      "16 A breaker. The isolator physically fitted in that room is 25 A, so the "
      "engine took the larger device and raised the conductor to 4 sq mm, whose "
      "ampacity is exactly 25 A. A 2.5 sq mm cable under a 25 A breaker would "
      "have been a protection violation."),

("p", "The quantitative result is the routing study. Three house types were "
      "designed twice, once with a separate run to every point and once with "
      "conduit shared as a Steiner tree:"),

("t", "1 BHK, 48 sq m|201.3 m|114.8 m|37.5%|8.7%\n"
      "2 BHK, 84 sq m|504.0 m|253.6 m|44.9%|8.6%\n"
      "3 BHK, 130 sq m|822.8 m|349.3 m|54.9%|5.8%\n"
      "Mean|||45.8%|7.7%"),

("p", "The first saving is a mean of 45.8% of conduit length from sharing the "
      "topology, and the second is a further 7.7% from letting the engine site "
      "the distribution board rather than defaulting to the entry door. The "
      "second figure is the more honest of the two. Experienced electricians "
      "already loop lighting points in and out, which recovers part of the "
      "topology saving, so 45.8% should be read as an upper bound against the "
      "worst case. The board siting figure holds the topology constant and is a "
      "clean result."),

("p", "The cost of delivery is software cost. There is no field organisation, "
      "no equipment to maintain, and no trained staff to place in every "
      "pincode, which is precisely why this approach was chosen over anything "
      "involving hardware on site."),

# ---------------------------------------------------------------- 8
("h1", "8. What it does not do yet"),

("p", "Stating this plainly is more useful than claiming otherwise."),

("b", "The scan captures one room at a time and separate captures do not "
      "share a coordinate frame. Room shapes and areas are measured; the "
      "arrangement between rooms is approximated. The schedule and the "
      "quantities are unaffected because they depend on area and room type."),

("b", "Augmented reality accuracy on a live site is unproven. The promise is "
      "dimensioned guidance and reference marks, not millimetre placement."),

("b", "Only the electrical layer is built. Water, gas and duct routing use "
      "the same geometry and the same router, but they are not implemented."),

("b", "Liability needs legal structuring. The tool must be a decision aid a "
      "licensed contractor signs off, not the designer of record."),

("b", "Adoption, not technology, is the real risk. If the app does not "
      "visibly save an electrician time on load calculation and estimating from "
      "the first use, it will be ignored by the people who decide what gets "
      "bought."),

# ---------------------------------------------------------------- 9
("h1", "9. Why this is worth doing"),

("p", "The components exist and the proposal is stronger for saying so. "
      "Automated electrical takeoff is a mature category, with tools such as "
      "drawer.ai, Kreo and Trimble Accubid serving contractors who bid large "
      "projects [12]. Robotic site layout is solved, with Dusty Robotics having "
      "printed coordinated models onto hundreds of millions of square feet of "
      "slab [13]."),

("p", "All of it serves Western commercial contractors. The contribution here "
      "is positional. The user is the home owner rather than an estimator, so "
      "the design is created by walking around rather than uploaded as a "
      "finished drawing. Indian practice and Indian codes are the rule set. The "
      "as-built record is produced, which no takeoff tool does, because its "
      "users leave the site and never return. And the whole thing is monetised "
      "by a company that sells every product it touches."),

("p", "The construction sector is the single largest consumer of cable in "
      "India at about 32% of demand [14], and residential construction is "
      "growing at about 6.6% a year [15]. That is the pipeline. NAKSHA puts "
      "V-Guard at the front of it, in the hand of the person deciding, at the "
      "one moment the decision is still open."),
]

REFERENCES = [
    "Ministry of Home Affairs, National Crime Records Bureau, Accidental "
    "Deaths and Suicides in India, chapter on causes of fire accidents.",

    "Asian Paints, Beautiful Homes Service, and Berger Paints, Express "
    "Painting, company service descriptions.",

    "Forbes India and TRA Research, Most Respected Consumer Tech Brands, as "
    "reported in Forbes India, Havells: Making a Brand of a Commodity.",

    "The Economic Times Brand Equity, Beyond metros, a big realty boom is "
    "brewing, on tier 2 and tier 3 land prices.",

    "NITI Aayog consumer survey on household electricity supply quality, "
    "2023, as reported in Finshots, How V-Guard Stabilised India.",

    "M. Hanan, On Steiner's problem with rectilinear distance, SIAM Journal "
    "on Applied Mathematics, 1966; and C. Chu and Y. Wong, FLUTE: Fast "
    "lookup table based rectilinear Steiner minimal tree algorithm, IEEE "
    "Transactions on Computer Aided Design, 2008.",

    "V-Guard Industries Limited, audited results for the quarter and year "
    "ended 31 March 2026, investor presentation.",

    "Reuters, India's V-Guard posts quarterly profit climb on healthy "
    "electricals demand, January 2026.",

    "Bank of America initiation of coverage on Polycab and KEI, as reported "
    "in The Economic Times.",

    "Motilal Oswal Financial Services, Cables and Wires sector update, "
    "June 2026, on industry size and the organised share.",

    "V-Guard Industries Limited, Rishta loyalty programme for electricians "
    "and plumbers, application listings.",

    "drawer.ai, Kreo and Trimble Accubid, product documentation for "
    "automated electrical takeoff.",

    "Dusty Robotics, FieldPrinter deployment figures, company reports.",

    "CRU Group, State policies and clean energy boost India's cable market, "
    "on construction as a share of cable demand.",

    "Mordor Intelligence, India Residential Construction Market, size and "
    "forecast.",
]

TABLE_HEADER = ["House type", "Radial", "Steiner", "Topology saving",
                "Board siting"]
