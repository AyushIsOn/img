# INVIDIA CORE — Video Script

Slide numbers match `INVIDIA-CORE-Slides.pdf`. Everything in `>` is what you say. `//` = pause / next beat.

**Measured length is at the bottom of this file.** If your brief demands a different duration, see *Trimming* at the end.

---

### 1 · Title — 0:00

> Every Indian home with a stabilizer has two boxes doing one job, in the same place.
> // One of them shouldn't exist.

### 2 · Two boxes — 0:09

> This is the distribution board. MCBs and RCCB, right after your meter.
> // And this is the stabilizer, sitting behind your air conditioner.
> // V-Guard makes both. Their Invidia Plus board even shows your incoming voltage on a screen.
> // So it tells you the voltage is bad. It just can't fix it.

### 3 · The proposal — 0:29

> Our proposal is simple. Put the fixing inside the board.
> // MCB, RCCB, surge protection, voltage correction. One enclosure, one rail.

### 4 · Why nobody has — 0:37

> There's a good reason nobody has. A whole-house stabilizer needs about eight thousand watts of transformer. Several kilos of iron, and it runs hot.
> // Put that next to your MCBs and they overheat and start tripping.
> // So this only works if the correction gets much smaller. Two ways, and they stack.

### 5 · Shrink one — 0:56

> First — the board already splits your supply into separate circuits. That's the row of MCBs.
> // So don't fix everything. Fix the air conditioner and the fridge, because those have compressors.
> // Leave the lights and fans. LED bulbs and BLDC fans run anywhere from a hundred volts to two-eighty. They genuinely don't care.
> // One AC circuit is three thousand watts, not eight thousand.

### 6 · Shrink two — 1:20

> Second — and this is the key one.
> // A normal stabilizer takes one-eighty in and builds two-thirty out. All the power goes through the transformer.
> // Instead: leave the one-eighty alone, and add fifty volts on top of it, in series.
> // Think of water pressure. You could build a pumping station that re-pressurises all the water. Or you could put a small booster in the pipe that adds only what's missing.
> // Same pressure at the tap. Much smaller machine.
> // Fifty volts instead of two-thirty — so about a fifth of the power.

### 7 · The cascade — 1:51

> Put them together. Eight thousand watts the old way. Three thousand for one circuit. Seven hundred once you only supply the shortfall.
> // Ten times smaller. And seven hundred watts fits on a DIN rail.

### 8 · The board — 2:04

> Mains, through the RCCB, onto the busbar. Three circuits get a module — lights and sockets don't.
> // Each module is sized to its own MCB, so nothing you plug in can overload it.
> // If one fails or overheats, a relay bypasses it. You lose the correction, never the power.
> // Another air conditioner later? Clip on another module.

### 9 · The business — 2:25

> And it changes how this sells.
> // Today you buy an AC, remember the stabilizer, and compare five brands in a shop.
> // With this, the electrician fits it while the house is being wired. You were never in that decision — and nobody removes a distribution board to save fifteen hundred rupees.

### 10 · Honest risk — 2:44

> One thing we won't overclaim. The arithmetic says the heat works. Proving it is test one — thermocouples inside a real enclosure, fully loaded.
> // If that test fails, the idea fails.

---

## Recording notes

- **Screen-record the slides PDF full-screen** and talk over it. No camera needed unless the rules require faces.
- Record **one take per slide.** Far easier to redo 20 seconds than 3 minutes.
- Phone voice memo in a small carpeted room beats a laptop mic in a big room.
- Say **"M-C-B"** and **"R-C-C-B"** as letters.
- Read numbers as written — "one-eighty", "two-thirty". Sounds natural, saves time.
- Export **1080p MP4, H.264.** Slides are exact 16:9.
- **Don't rush slide 6.** It's the one idea the judges must actually understand.

## Trimming

- **Need 2:00?** Use only slides 1, 3, 5, 6, 7, 9. That keeps the whole spine: problem → idea → shrink one → shrink two → it fits → why it sells.
- **Need 5:00?** Slow down, and add: the solar and EV angle after slide 9, and the sub-circuit limitation after slide 10.
- Speaking pace assumed is 150 words per minute. If you naturally read faster, you'll land shorter — that's fine, never pad.


## Measured length

**463 spoken words.**

| Pace | Runtime |
|---|---|
| 140 wpm (slow, clear) | 3:18 |
| 150 wpm (normal) | **3:05** |
| 160 wpm (brisk) | 2:53 |

Per-slide budget (at 150 wpm):

| Slide | Words | Seconds |
|---|---|---|
| 1 Title | 21 | 8 |
| 2 Two boxes | 50 | 20 |
| 3 The proposal | 20 | 8 |
| 4 Why nobody has | 51 | 20 |
| 5 Shrink one | 62 | 25 |
| 6 Shrink two | 89 | 36 |
| 7 The cascade | 34 | 14 |
| 8 The board | 56 | 22 |
| 9 The business | 50 | 20 |
| 10 Honest risk | 30 | 12 |
