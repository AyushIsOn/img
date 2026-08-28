# Exhibit images

Three placeholders are committed here so the layout is already correct. Each is
at the aspect ratio of the intended picture, so swapping it does not reflow the
document.

| File | Should show |
|---|---|
| `berger-express-painting.jpg` | Berger Express Painting crew working in a room |
| `laser-projector.jpg` | 360 degree line laser with tripod and wall mount |
| `dusty-robotics.jpg` | Dusty Robotics FieldPrinter printing a layout on a slab |

## Replacing them

In Word, right click the picture and choose **Change Picture**. Size and caption
stay as they are. This is the quickest route and needs no rebuild.

Or overwrite the files here and rebuild both formats:

```bash
python3 build_docx.py     # editable submission
python3 build_report.py   # pdf
```
