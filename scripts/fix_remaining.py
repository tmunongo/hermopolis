import glob
import re

CLASSES = [
    ".slider-row",
    ".broll-card",
    ".broll-thumb",
    ".broll-thumb-label",
    ".broll-desc",
    ".broll-rating-strip",
    ".broll-rate-btn",
    ".vfunc-row",
    ".vfunc-icon",
    ".vfunc-body",
    ".vfunc-name",
    ".vfunc-desc",
    ".vfunc-badge",
    ".vfunc-example",
    ".diag-stage",
    ".diag-stage-num",
    ".diag-stage-badge",
    ".diag-dot",
    ".diag-detail",
    ".metaphor-concept-pill",
    ".metaphor-panel",
    ".metaphor-panel-label",
    ".metaphor-visual",
    ".metaphor-text",
    ".metaphor-verdict",
    ".framing-cell",
    ".framing-cell-label",
    ".framing-detail",
    ".iso-element",
    ".lline-cell",
    ".lline-label",
    ".llines-detail",
    ".func-detail",
    ".overuse-element",
    ".overuse-score",
    ".overuse-chip",
    ".overuse-meter-row",
    ".overuse-meter-label",
    ".overuse-meter-bar",
    ".overuse-meter-fill",
    ".timing-grid",
    ".timing-cell",
    ".timing-row-label",
    ".motion-cost-item",
    ".mci-icon",
    ".mci-label",
    ".mci-toggle",
    ".mci-cost",
    ".sync-strip",
    ".sync-strip-label",
    ".sync-strip-events",
    ".sync-event",
    ".sync-playhead",
    ".channel-track",
    ".channel-track-label",
    ".channel-track-body",
    ".channel-clip",
    ".channel-playhead",
    ".vp-word",
    ".vp-cursor",
    ".cue-chip",
    ".cue-legend-item",
    ".cue-legend-dot",
    ".pause-sentence",
    ".pause-word-row",
    ".pw",
]

files = glob.glob("src/lib/modules/*/*.svelte")

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Fix a11y canvas roles
    content = content.replace('role="region"', 'role="img"')
    content = content.replace("role='region'", "role='img'")
    content = content.replace('role="application"', 'role="img"')
    content = content.replace("role='application'", "role='img'")

    # 2. Fix inner selectors
    content = re.sub(r":global\(([^)]+)\)\s+([^{]+)\s*\{", r":global(\1 \2) {", content)

    # 3. Fix un-globbed classes
    lines = content.split("\n")
    new_lines = []
    in_style = False

    for line in lines:
        if "<style>" in line:
            in_style = True
        elif "</style>" in line:
            in_style = False

        if in_style:
            for cls in CLASSES:
                escaped = cls.replace(".", "\\.")
                pattern = r"^(\s*)(" + escaped + r"(?:[:\. ][^\{]+)?)(\s*\{)"
                match = re.match(pattern, line)
                if match:
                    line = f"{match.group(1)}:global({match.group(2)}){match.group(3)}"
                    break
        new_lines.append(line)

    new_content = "\n".join(new_lines)

    if new_content != content:
        with open(file, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Patched {file}")
