# Exhibit images

`build_report.py` embeds these if present and skips them with a warning if not,
so the report always builds.

Save the three images here with exactly these names, then rebuild:

| File | What it shows |
|---|---|
| `berger-express-painting.jpg` | Berger Express Painting crew at work in a room |
| `laser-projector.jpg` | 360 degree line laser with tripod and wall mount |
| `dusty-robotics.jpg` | Dusty Robotics printing a layout onto a slab |

```bash
cd vguard-bigidea && python3 build_report.py
```

Any common raster format works, jpg or png. Widths are set per exhibit in
`report_content.py`; aspect ratio is preserved automatically.
