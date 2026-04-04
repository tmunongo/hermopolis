#!/usr/bin/env python3
"""
HTML to Svelte Module Conversion Script for Hermopolis Platform

Usage:
  python3 scripts/convert_module.py <path/to/Module.html> <output/path/ModuleXX.svelte>
"""

import re
import os
import sys


def convert_module(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    css_match = re.search(r"<style>(.*?)</style>", text, re.DOTALL)
    css = css_match.group(1).strip() if css_match else ""
    css = re.sub(r":root\s*\{[^}]+\}", "", css, flags=re.DOTALL)
    css = re.sub(r"\*,\s*\*\:\:before,\s*\*\:\:after\s*\{[^}]+\}", "", css)
    css = re.sub(r"html\s*\{[^}]+\}", "", css)
    css = re.sub(r"(?<![a-zA-Z0-9_\-])body\s*\{", ".page-wrapper {", css)
    css = re.sub(r"::-webkit-scrollbar[^{]*\{[^}]+\}", "", css)
    # Ensure keyboard users can see focus on interactive buttons
    if ".btn" in css and not re.search(r"\.btn\s*:(?:focus|focus-visible)\b", css):
        css += (
            "\n\n.btn:focus,\n"
            ".btn:focus-visible {\n"
            "\toutline: 3px solid currentColor;\n"
            "\toutline-offset: 3px;\n"
            "}\n"
        )

    selectors_to_wrap = [
        ".frame-strip",
        ".frame-cell",
        ".film-frame",
        ".film-frame.active",
        ".film-frame canvas",
        ".film-frame-num",
        ".hero-deco-col",
        ".hero-dot",
        ".preset-btn",
        ".preset-btn.active",
        ".preset-btn:hover",
        "h3",
        "code",
        "input[type='range']",
        "input[type='range']::-webkit-slider-thumb",
        ".btn",
        ".btn:hover",
        ".btn.active",
        ".btn.coral.active",
        ".btn.mint.active",
        ".btn.off",
        ".btn.off:hover",
        ".btn-row",
        ".spacing-chart-wrap",
        ".spacing-row",
        ".spacing-row-label",
        ".spacing-track",
        ".spacing-dot",
        ".weight-grid",
        ".weight-panel",
        ".weight-label",
        ".weight-label span",
        ".curve-mini",
        ".q-img",
        ".option.correct",
        ".option.wrong",
        ".option.disabled",
        ".feedback.ok",
        ".feedback.bad",
        ".quiz-score.visible",
        ".graph-legend",
        ".p-card",
        ".p-card:hover",
        ".p-card.active",
        ".p-card.active::after",
        ".p-card-num",
        ".p-card-name",
        ".p-card-tag",
        ".p-card.active .p-card-num",
        ".p-card.active .p-card-name",
        ".ctrl-row",
        ".ctrl-label",
        ".ctrl-val",
        ".key-insight",
        ".key-insight-label",
        ".buffer-row",
        ".buffer-cell",
        ".buffer-cell span",
        ".buffer-cell:hover",
        ".buffer-cell.X",
        ".buffer-cell.Y",
        ".buffer-cell.R",
        ".buffer-cell.G",
        ".buffer-cell.B",
        ".state-val",
        ".state-val.none",
        ".state-val.bound",
        ".log-line",
        ".log-line.bind",
        ".log-line.draw",
        ".log-line.gpu",
        ".log-line.info",
        ".question",
        ".lang-tag",
        ".cc-item",
        ".cc-item.bad",
        ".cc-item.good",
        ".debug-option",
        ".debug-option:hover",
        ".debug-option.correct",
        ".debug-option.wrong",
        ".debug-option.disabled",
        ".demo-badge.animated",
        ".btn.rose:hover",
        ".btn.rose.active",
        ".btn.violet.active",
        ".btn.amber.active",
        ".issue-list li",
        ".issue-list li.problem",
        ".issue-list li.strength",
        ".ts-output.rose-mode .ts-heading",
        ".ts-output.mix-mode .ts-heading",
        ".tp-option",
        ".tp-option:hover",
        ".tp-option.correct",
        ".tp-option.wrong",
        ".tp-option.disabled",
        ".tp-feedback",
        ".tp-feedback.ok",
        ".tp-feedback.bad",
        ".op",
        ".callout.pink",
        ".callout.pink .callout-label",
        ".callout.sky",
        ".callout.sky .callout-label",
        ".btn.sage:hover",
        ".btn.sage.active",
        ".btn.violet:hover",
        ".btn.sky:hover",
        ".btn.sky.active",
        ".three-col",
        ".p-tag",
        ".brand-scenario",
        ".brand-scenario-label",
        ".brand-prompt",
        ".shape-options",
        ".shape-choice",
        ".shape-choice:hover",
        ".shape-choice.selected",
        ".shape-choice.correct-reveal",
        ".shape-choice.wrong-reveal",
        ".brand-feedback",
        ".brand-feedback.ok",
        ".brand-feedback.bad",
        ".icon-rule-card",
        ".icon-rule-card-label",
        ".icon-rule-canvas",
        ".icon-rule-verdict",
        ".icon-rule-verdict.pass",
        ".icon-rule-verdict.fail",
        ".assess-option-canvas",
        ".assess-option-canvas:hover",
        ".assess-option-canvas.correct-reveal",
        ".assess-option-canvas.wrong-reveal",
        ".assess-canvas-label",
        ".assess-feedback.ok",
        ".assess-feedback.bad",
        ".btn.gold.active",
        ".gpu-stage.active",
        ".gpu-stage.active .gpu-stage-num",
        ".gpu-stage.active .gpu-stage-name",
        ".gpu-stage.active .gpu-stage-desc",
        ".q-text",
        ".q-num",
        ".options",
        ".option",
        ".option:hover",
        ".feedback",
        ".bind-step",
        ".bind-step:last-child",
        ".bind-num",
        ".bind-content",
        ".bind-title",
        ".bind-desc",
        ".log-line:last-child",
        # Anim Module 05 Selectors
        ".hero-bar",
        ".btn.coral:hover",
        ".btn.mint:hover",
        ".btn.danger",
        ".btn.danger:hover",
        "input[type='range'].coral::-webkit-slider-thumb",
        ".tl-btn.playing",
        ".tl-layer-name-row",
        ".tl-layer-name-row:hover",
        ".tl-layer-name-row.selected",
        ".tl-layer-swatch",
        ".tl-layer-label",
        ".tl-layer-name-row.selected .tl-layer-label",
        ".tl-layer-eye",
        ".tl-layer-eye:hover",
        ".tl-ruler-tick",
        ".tl-ruler-num",
        ".tl-ruler-line",
        ".tl-ruler-line.major",
        ".tl-track-row",
        ".tl-track-bg",
        ".tl-keyframe",
        ".tl-keyframe:hover",
        ".tl-tween-bar",
        ".tl-tween-bar.hold",
        ".ls-layer",
        ".ls-layer:hover",
        ".ls-layer.selected",
        ".ls-layer.dragging",
        ".ls-swatch",
        ".ls-name",
        ".ls-layer.selected .ls-name",
        ".ls-type",
        ".ls-eye",
        ".ls-eye:hover",
        ".ls-layer.visible .ls-eye",
        ".ls-lock",
        ".ls-lock:hover",
        ".ls-preview",
        ".onion-shell",
        ".onion-panel",
        ".onion-panel-label",
        # Mod 01-03 Selectors
        "pre",
        ".kw",
        ".fn",
        ".str",
        ".cm",
        ".num",
        ".callout.red",
        ".callout.red .callout-label",
        ".btn.amber:hover",
        ".btn.red:hover",
        ".btn.red.active",
        ".btn.blue:hover",
        ".btn.blue.active",
        ".prev-link",
        ".prev-link:hover",
        ".cog-bar",
        ".slider-row",
        ".slider-row label",
        ".slider-val",
        ".pace-clip",
        ".pace-separator",
        ".pace-info strong",
        ".chunk-row",
        ".chunk-block",
        ".chunk-divider",
        ".chunk-divider.strong",
        ".chunk-label",
        ".rhythm-beat",
        ".rhythm-beat:hover",
        ".rhythm-beat.cut",
        ".rhythm-beat.hold",
        ".rhythm-beat.peak",
        ".hier-row",
        ".hier-row:last-child",
        ".hier-rank",
        ".hier-label",
        ".hier-bar-wrap",
        ".hier-bar-fill",
        ".hier-props",
        ".dtree",
        ".dnode",
        ".dnode:hover",
        ".dnode.active",
        ".dnode.result-animate",
        ".dnode.result-static",
        ".dnode.result-either",
        ".dnode-q",
        ".dnode-opts",
        ".dnode-opt",
        ".dnode-opt:hover",
        ".dnode-opt.chosen",
        ".dtree-connector",
        ".dtree-result",
        ".dtree-result.animate",
        ".dtree-result.static",
        ".dtree-result.either",
        ".dtree-verdict",
        ".dnode-reason",
        ".contrast-swatch",
        ".sg-dont::before",
        ".sg-dont",
        ".sg-do",
        ".sg-do::before",
        ".sg-color-chip",
        ".sg-color-chip-swatch",
        ".sg-color-chip-info",
        ".sg-color-chip-name",
        ".sg-color-chip-role",
        ".sg-color-chip-val",
        ".sg-type-row",
        ".sg-type-row:last-child",
        ".sg-type-spec",
        ".sg-type-tag",
        ".sg-icon-cell",
        ".sg-icon-cell canvas",
        ".sg-icon-cell-label",
        ".sg-voice-pair",
        ".sg-voice-do",
        ".sg-voice-dont",
        ".sg-voice-label",
        ".sg-voice-text",
        ".export-card",
        ".export-card-header",
        ".export-card-fmt",
        ".export-card-type",
        ".export-card-body",
        ".export-card-uses",
        ".export-use-item",
        ".export-use-dot",
        ".export-card-warn",
        ".audit-q-item",
        ".audit-q-header",
        ".audit-q-header.answered-yes",
        ".audit-q-header.answered-no",
        ".audit-q-body",
        ".audit-q-cat",
        ".audit-q-btns",
        ".audit-q-btn",
        ".audit-q-btn.yes",
        ".audit-q-btn.no",
        ".audit-result.visible",
        ".audit-area-item",
        ".two-col",
        ".callout.warn",
        ".callout.warn .callout-label",
        ".ep-info strong",
        ".rot-score-label",
        ".rot-score-label span",
        ".callout.violet",
        ".callout.violet .callout-label",
        ".h-swatch",
        ".h-swatch:hover",
        ".h-swatch-label",
        ".cc-badge",
        ".cc-badge.pass",
        ".cc-badge.fail",
        ".palette-opt.correct",
        ".palette-opt.wrong",
        ".palette-opt.disabled",
        ".palette-feedback.ok",
        ".palette-feedback.bad",
        ".brand-layer",
        ".brand-layer .layer-title",
        ".brand-layer .layer-subtitle",
        ".brand-layer .layer-arrow",
        ".brand-layer.open .layer-arrow",
        ".layer-content",
        ".layer-content.open",
        ".layer-content ul",
        ".layer-content li",
        ".layer-content li::before",
        ".layer-content .layer-example",
        ".concept-score-row",
        ".concept-score-label",
        ".concept-score-bar-bg",
        ".concept-score-bar",
        ".concept-score-val",
        ".sgp-logo-area",
        ".sgp-logo-mark",
        ".sgp-brand-name",
        ".sgp-tagline",
        ".sgp-palette-row",
        ".sgp-swatch",
        ".sgp-type-row",
        ".sgp-heading",
        ".sgp-body-text",
        ".sgp-thumb",
        ".sgp-thumb-canvas",
        ".sgp-label",
        ".cc-touchpoint",
        ".cc-tp-label",
        ".cc-tp-canvas",
        ".cc-verdict-item",
        ".cc-verdict-icon",
        ".critique-specimen",
        ".critique-specimen-canvas",
        ".critique-specimen-label",
        ".critique-q",
        ".critique-opts",
        ".critique-opt",
        ".critique-opt:hover",
        ".critique-opt.correct",
        ".critique-opt.wrong",
        ".critique-opt.disabled",
        ".critique-feedback",
        ".critique-feedback.ok",
        ".critique-feedback.bad",
        ".tf-anatomy",
        ".tf-tag.sage",
        ".tf-ann-line",
        ".audit-opt.correct",
        ".audit-opt.wrong",
        ".audit-opt.disabled",
        ".audit-feedback.ok",
        ".audit-feedback.bad",
        ".compare-item.selected",
        ".assess-q",
        ".assess-q-header",
        ".assess-q-body",
        ".assess-canvas-wrap",
        ".assess-canvas-wrap canvas",
        ".assess-q-text",
        ".assess-opts",
        ".assess-opt",
        ".assess-opt:hover",
        ".assess-opt.correct",
        ".assess-opt.wrong",
        ".assess-opt.disabled",
        ".assess-feedback",
        ".checklist-module",
        ".checklist-module-header",
        ".checklist-module-title",
        ".checklist-module-progress",
        ".checklist-module-bar",
        ".checklist-module-bar-fill",
        ".checklist-items",
        ".checklist-item",
        ".checklist-item:last-child",
        ".checklist-item:hover",
        ".checklist-item.done .ci-box",
        ".checklist-item.done .ci-check",
        ".checklist-item.done .ci-text",
        ".ci-box",
        ".ci-check",
        ".ci-text",
        ".ci-tag",
        ".sg-logo-variant",
        ".sg-logo-variant-label",
        ".analogy-card",
        ".analogy-card:hover",
        ".analogy-card.selected",
        ".analogy-card canvas",
        ".analogy-card-label",
        ".seq-stage",
        ".seq-stage:last-child",
        ".seq-stage:hover",
        ".seq-stage.active",
        ".seq-stage:hover + .seq-stage",
        ".seq-stage.active + .seq-stage",
        ".seq-stage-num",
        ".seq-stage-label",
        ".reduction-step-btn",
        ".reduction-step-btn:hover",
        ".reduction-step-btn.active",
        ".reduction-step-btn .step-num",
        ".sb-panel",
        ".sb-panel.selected",
        ".sb-panel canvas",
        ".sb-panel-footer",
        ".sb-panel-num",
        ".sb-strip-item",
        ".sb-strip-item canvas",
        ".sb-strip-label",
        ".assess-question",
        ".assess-q-hdr",
        ".assess-canvas-row",
        ".assess-canvas-row canvas",
        ".assess-fb",
        ".assess-fb.ok",
        ".assess-fb.bad",
        # VS Module09 — Colour System Builder & Typography Pairing Lab
        ".csb-swatch-row",
        ".csb-swatch",
        ".csb-swatch.selected",
        ".csb-swatch-label",
        ".csb-role-row",
        ".csb-role-cell",
        ".csb-role-cell.active",
        ".color-picker-wrap",
        ".color-picker-label",
        ".color-picker-swatch",
        ".color-picker-swatch:hover",
        ".color-picker-hex",
        ".color-picker-hex:focus",
        ".color-harmony-tag",
        ".type-role-card",
        ".type-role-card:hover",
        ".type-role-card.selected",
        ".type-role-name",
        ".type-role-card.selected .type-role-name",
        ".type-preview",
        ".font-option",
        ".font-option:hover",
        ".font-option.selected",
        ".font-option-preview",
        ".font-option-meta",
        ".font-option-name",
        ".cc-frame-pair",
        ".cc-frame",
        ".cc-frame:hover",
        ".cc-frame canvas",
        ".cc-frame-label",
        # VS Module10 — Production Pipeline & Capstone
        ".pipeline-stage",
        ".pipeline-stage:hover",
        ".pipeline-stage.active",
        ".pipeline-stage.done",
        ".ps-header",
        ".ps-num",
        ".ps-title",
        ".ps-badge",
        ".ps-body",
        ".ps-tasks",
        ".ps-task",
        ".ps-task:last-child",
        ".ps-task-check",
        ".ps-task-check.checked",
        ".ps-task-text",
        ".ps-task-text.done",
        ".ps-module-ref",
        ".pipeline-stage.active .ps-num",
        ".pipeline-stage.done .ps-num",
        ".pipeline-stage.active .ps-title",
        ".pipeline-stage.active .ps-body",
        ".checklist-group",
        ".checklist-group-label",
        ".check-box",
        ".capstone-badge",
        ".course-complete",
        ".cc-title",
        ".cc-sub",
        # Game Dev Module11/12 — sliders, info, polish, 3D, complete banner
        ".slider-row input[type='range']",
        ".slider-row input[type='range']::-webkit-slider-thumb",
        ".slider-val",
        ".info-panel",
        ".info-row",
        ".info-key",
        ".info-val",
        ".polish-item",
        ".polish-item:last-child",
        ".polish-check",
        ".polish-check.done",
        ".polish-label",
        ".polish-label.done",
        ".mat4",
        ".m4c",
        ".m4c.hi",
        ".mat-label",
        ".pipeline3d",
        ".p3d-stage",
        ".p3d-stage:last-child",
        ".p3d-stage:hover",
        ".p3d-stage.active",
        ".p3d-name",
        ".p3d-sub",
        ".p3d-detail",
        ".depth-strip",
        ".depth-cell",
        ".complete-banner",
        ".complete-title",
        ".complete-sub",
        ".module-grid",
        ".mod-chip",
        ".mod-chip.done",
        ".demo-badge.i",
        ".demo-badge.a",
        ".demo-badge.g",
        ".btn.g:hover",
        ".btn.g.active",
        ".btn.o:hover",
        ".btn.o.active",
        ".callout.gold",
        ".callout.gold .callout-label",
        ".callout.green",
        ".callout.green .callout-label",
        ".callout.blue",
        ".callout.blue .callout-label",
        ".callout.orange",
        ".callout.orange .callout-label",
        ".callout.cyan",
        ".callout.cyan .callout-label",
        ".callout.amber",
        ".callout.amber .callout-label",
        ".callout.mint",
        ".callout.mint .callout-label",
    ]
    for sel in selectors_to_wrap:
        escaped_sel = re.escape(sel)
        # Target strict selector boundaries to prevent corrupting compound class names (e.g. `code` matching inside `.tl-timecode`)
        css = re.sub(
            rf"(?<!:global\()(?<![a-zA-Z0-9_\-]){escaped_sel}(?P<suffix>[\s{{,>+~])",
            rf":global({sel})\g<suffix>",
            css,
        )

    if "animation" in output_path:
        token_replacements = [
            ("--bg", "--anim-bg"),
            ("--surface", "--anim-surface"),
            ("--raised", "--anim-raised"),
            ("--border2", "--anim-border2"),
            ("--border", "--anim-border"),
            ("--gold", "--anim-gold"),
            ("--coral", "--anim-coral"),
            ("--mint", "--anim-mint"),
            ("--lavender", "--anim-lavender"),
            ("--text", "--anim-text"),
            ("--muted", "--anim-muted"),
            ("--dim", "--anim-dim"),
        ]
        for old_token, new_token in token_replacements:
            css = css.replace(old_token, new_token)

    body_match = re.search(r"<body>(.*?)</body>", text, re.DOTALL)
    body_content = body_match.group(1).strip() if body_match else text

    script_match = re.search(r"<script>(.*?)</script>", body_content, re.DOTALL)
    script_js = script_match.group(1).strip() if script_match else ""
    # Patch specific logic bugs found in modules (like profile list duplication in Module 2)
    script_js = script_js.replace(
        "const list = document.getElementById('profileList');",
        "const list = document.getElementById('profileList');\n\t\tlist.innerHTML = '';",
    )
    script_js = script_js.replace("let desc = '';", "let desc;")
    script_js = script_js.replace("anticipateOffset = 0;", "anticipateOffset;")
    html_content = re.sub(
        r"<script>.*?</script>", "", body_content, flags=re.DOTALL
    ).strip()

    # Escape GLSL/Python braces AND bare < inside <pre>/<code> blocks so Svelte doesn't crash
    def escape_pre_code(match):
        block = match.group(0)
        block = block.replace("{", "&#123;").replace("}", "&#125;")
        # Escape bare < that Svelte would parse as a component/element tag
        # Use negative lookahead to NOT escape valid HTML tags that might be inside Pygments output
        block = re.sub(
            r"<(?!/?(?:span|code|pre|div|br|strong|em|b|i|u|a|table|tr|td|th|tbody|thead|p|h[1-6]|ul|ol|li)\b)",
            "&lt;",
            block,
        )
        return block

    html_content = re.sub(
        r"(<pre>.*?</pre>|<code>.*?</code>)",
        escape_pre_code,
        html_content,
        flags=re.DOTALL,
    )

    # ── Auto-patch accessibility (ARIA, Buttons, Labels) ──
    # Auto-add aria-attributes to canvases
    def fix_canvas_aria(match):
        attrs = match.group(1) or ""
        if "aria-label" not in attrs:
            # Try to grab the id for the label
            id_match = re.search(r'id=["\']([^"\']+)["\']', attrs)
            label = (
                id_match.group(1).replace("-", " ").title() + " Demonstration"
                if id_match
                else "Canvas Demonstration"
            )
            return (
                f'<canvas{attrs} aria-label="{label}" role="application" tabindex="0">'
            )
        return match.group(0)

    html_content = re.sub(r"<canvas([^>]*)>", fix_canvas_aria, html_content)

    # Convert .option divs into semantic buttons for keyboard accessibility
    # Do this in a single pass so we don't accidentally rewrite parent </div> closings.
    html_content = re.sub(
        r'<div class="option"([^>]*)>(.*?)</div\s*>',
        r'<button type="button" class="option"\1>\2</button>',
        html_content,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Mark quiz option correctness explicitly for robust highlighting
    def add_data_correct(match):
        tag = match.group(0)
        if "data-correct=" in tag:
            return tag
        attrs = match.group(1) or ""
        is_true = bool(re.search(r",\s*true\s*\)", attrs))
        return tag.replace(
            'class="option"',
            f'class="option" data-correct="{"true" if is_true else "false"}"',
            1,
        )

    html_content = re.sub(
        r'<button([^>]*\bclass="option"[^>]*)>',
        add_data_correct,
        html_content,
        flags=re.IGNORECASE,
    )

    # Convert loose labels next to inputs into associated labels for a11y
    html_content = re.sub(
        r'<label>([^<]+)</label>(?=\s*<input[^>]+id=["\']([^"\']+)["\'])',
        r'<label for="\2">\1</label>',
        html_content,
    )

    # Convert #reading-progress to valid progressbar
    html_content = html_content.replace(
        '<div class="progress-bar-fill" id="reading-progress">',
        '<div class="progress-bar-fill" id="reading-progress" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">',
    )

    # Replace bare placeholder anchors with a valid relative path so Svelte doesn't flag invalid hrefs
    html_content = html_content.replace('href="#"', 'href="."')
    html_content = html_content.replace('href="javascript:void(0)"', 'href="."')

    # Visual Storytelling Module01: default mode is faceless-info, so btn-fs should not start mint
    if (
        "visual-storytelling" in output_path
        and os.path.basename(output_path) == "Module01.svelte"
    ):
        html_content = re.sub(
            r'(<button[^>]*\bid=["\']btn-fs["\'][^>]*\bclass=["\'])([^"\']*)(["\'])',
            lambda m: (
                m.group(1)
                + " ".join([c for c in m.group(2).split() if c != "mint"])
                + m.group(3)
            ),
            html_content,
            flags=re.IGNORECASE,
        )

    # Fix label for= association: match <label> followed by a sibling input with id
    def fix_label_for(match):
        """Replace bare <label> with <label for="..."> using the id of the next sibling input."""
        full = match.group(0)
        # Find the input id in the surrounding context
        input_id_match = re.search(r'<input[^>]+id="([^"]+)"', full)
        if input_id_match:
            label_for = input_id_match.group(1)
            # Replace the first <label...> (up to >) with the for attribute added.
            # Using sub with count=1
            return re.sub(
                r"<label([^>]*)>", rf'<label\g<1> for="{label_for}">', full, count=1
            )
        # No input with id found in context, just return as is
        return full

    # Match slider-row patterns: <label ...>...</label> ... <input ... id="..." ...>
    html_content = re.sub(
        r'<label[^>]*>([^<]*)</label>\s*(?=>?\s*<input[^>]+id="[^"]+")',
        fix_label_for,
        html_content,
    )

    # Fallback: any remaining <label> without for=
    def ensure_dummy_for(match):
        attrs = match.group(1) or ""
        if "for=" in attrs:
            return match.group(0)
        return f'<label{attrs} for="dummy">'

    html_content = re.sub(
        r"<label([^>]*)>(?![^<]*</label>)",
        ensure_dummy_for,
        html_content,
    )

    # Prevent bare { } from crashing Svelte parser (e.g. state tables, template literals)
    # Replace any {…} expression that Svelte would try to evaluate as a template
    html_content = re.sub(
        r"\{([^{}]*)\}", lambda m: "&#123;" + m.group(1) + "&#125;", html_content
    )

    # Generic click handler logic
    def replace_onclick(match):
        prefix = match.group(1)
        code = match.group(2)
        suffix = match.group(3)
        code = re.sub(r"\bthis\b", "e.currentTarget", code)
        code = re.sub(r"window\.", "", code)  # remove preexisting window.

        tag = prefix.strip("< ").split()[0].lower()
        full_tag = prefix + suffix
        simple_call = re.match(
            r"^\s*([A-Za-z_$][\w$]*)\s*\(([^)]*)\)\s*;?\s*$",
            code,
        )
        if simple_call:
            fn = simple_call.group(1)
            args = simple_call.group(2).strip()
            call_expr = f"actions.{fn}({args})" if args else f"actions.{fn}()"
        else:
            fn = None
            args = None
            call_expr = None

        if tag in ["button", "a"]:
            if call_expr:
                return f"{prefix}onclick={{(e) => {call_expr}}}{suffix}"
            return f"{prefix}onclick={{(e) => {{ {code} }}}}{suffix}"
        else:
            extras = ""
            if "role=" not in full_tag:
                extras += ' role="button"'
            if "tabindex=" not in full_tag:
                extras += ' tabindex="0"'
            if "onkeydown=" not in full_tag:
                if call_expr:
                    extras += f' onkeydown={{(e) => {{ if (e.key === "Enter" || e.key === " ") {{ e.preventDefault(); {call_expr}; }} }}}}'
                else:
                    extras += f' onkeydown={{(e) => {{ if (e.key === "Enter" || e.key === " ") {{ e.preventDefault(); {code}; }} }}}}'
            if call_expr:
                return f"{prefix}onclick={{(e) => {call_expr}}}{extras}{suffix}"
            return f"{prefix}onclick={{(e) => {{ {code} }}}}{extras}{suffix}"

    html_content = re.sub(r'\s+onkeydown="[^"]*"', "", html_content)
    html_content = re.sub(
        r'(<[^>]+)\bonclick="([^"]+)"([^>]*>)', replace_onclick, html_content
    )

    html_content = re.sub(
        r'\boninput="([^"]+)"',
        lambda m: (
            f"oninput={{() => {{ actions.{m.group(1).replace('window.', '')} }}}}"
        ),
        html_content,
    )
    html_content = re.sub(
        r'\bonchange="([^"]+)"',
        lambda m: (
            f"onchange={{() => {{ actions.{m.group(1).replace('window.', '')} }}}}"
        ),
        html_content,
    )

    # ── Script JS Transformations ──

    # 1. Deduplicate function declarations across combined script blocks
    # Track seen function names, remove subsequent duplicate declarations
    seen_functions = set()

    def dedup_function(match):
        name = match.group(1)
        if name in seen_functions:
            return f"var _dup_{name} = function("
        seen_functions.add(name)
        return match.group(0)

    # First, collect all function names for binding
    function_names = list(
        dict.fromkeys(re.findall(r"function\s+([a-zA-Z0-9_]+)\s*\(", script_js))
    )

    # Then deduplicate declarations
    script_js = re.sub(r"function\s+([a-zA-Z0-9_]+)\s*\(", dedup_function, script_js)

    # 2. Build actions bindings for template onclick handlers
    actions_bindings = "\n\t\t".join(
        [
            f"if (typeof {fn} === 'function') actions.{fn} = {fn};"
            for fn in function_names
        ]
    )

    # 3. Prevent division-by-zero in scroll handlers
    script_js = script_js.replace(
        "el.scrollHeight - el.clientHeight",
        "Math.max(1, el.scrollHeight - el.clientHeight)",
    )
    script_js = script_js.replace(
        "el.style.width = (window.scrollY / docH) * 100 + '%';",
        "if (!docH || docH <= 0) { el.style.width = '0%'; el.setAttribute('aria-valuenow', '0'); return; }\n"
        "\t\t\t\tconst progress = Math.max(0, Math.min(1, window.scrollY / docH));\n"
        "\t\t\t\tconst pct = Math.round(progress * 100);\n"
        "\t\t\t\tel.style.width = pct + '%';\n"
        "\t\t\t\tel.setAttribute('aria-valuenow', String(pct));",
    )
    # Keep aria-valuenow in sync for the common direct style.width assignment pattern
    script_js = re.sub(
        r"document\.getElementById\(['\"]reading-progress['\"]\)\.style\.width\s*=\s*(?P<expr>[^;]+);",
        (
            "const _rp = document.getElementById('reading-progress');\n"
            "\t\t\tif (_rp) {\n"
            "\t\t\t\t_rp.style.width = \\g<expr>;\n"
            "\t\t\t\t_rp.setAttribute('aria-valuenow', String(Math.round(parseFloat(_rp.style.width) || 0)));\n"
            "\t\t\t}"
        ),
        script_js,
    )

    # 4. Detect and bind memory leaks
    raf_vars = set(re.findall(r"(\w+)\s*=\s*requestAnimationFrame\(", script_js))
    interval_vars = set(re.findall(r"(\w+)\s*=\s*setInterval\(", script_js))
    timeout_vars = set(re.findall(r"(\w+)\s*=\s*setTimeout\(", script_js))

    for name in [
        "fpsRafId",
        "tsRafId",
        "curveRafId",
        "arcRafId",
        "weightRafId",
        "scRafId",
        "flRAF",
        "walkRaf",
        "hlRaf",
        "clutterRaf",
        "baRaf",
        "flowRaf",
        "fkAnimRaf",
        "flipTimer",
    ]:
        if name in script_js:
            if "Raf" in name or "RAF" in name:
                raf_vars.add(name)
            else:
                interval_vars.add(name)

    cleanup_logic = []
    for var in sorted(raf_vars):
        cleanup_logic.append(
            f"if (typeof {var} !== 'undefined' && {var}) cancelAnimationFrame({var});"
        )
    for var in sorted(interval_vars):
        cleanup_logic.append(
            f"if (typeof {var} !== 'undefined' && {var}) clearInterval({var});"
        )
    for var in sorted(timeout_vars):
        cleanup_logic.append(
            f"if (typeof {var} !== 'undefined' && {var}) clearTimeout({var});"
        )

    # Track document and window events properly without regex parens
    if "addEventListener" in script_js:
        script_js = script_js.replace("window.addEventListener", "_addWinListener")
        script_js = script_js.replace("document.addEventListener", "_addDocListener")
        listener_shim = (
            "\t\tconst _listeners = [];\n"
            "\t\tconst _addWinListener = (type, listener, options) => {\n"
            "\t\t\twindow.addEventListener(type, listener, options);\n"
            "\t\t\t_listeners.push({ target: window, args: [type, listener, options] });\n"
            "\t\t};\n"
            "\t\tconst _addDocListener = (type, listener, options) => {\n"
            "\t\t\tdocument.addEventListener(type, listener, options);\n"
            "\t\t\t_listeners.push({ target: document, args: [type, listener, options] });\n"
            "\t\t};\n"
        )
        script_js = listener_shim + script_js
        cleanup_logic.append(
            "_listeners.forEach(l => l.target.removeEventListener(...l.args));"
        )

    cleanup_str = "\n\t\t\t".join(cleanup_logic)

    # Replace `const x = this` inside event listener callbacks with e.currentTarget
    script_js = re.sub(
        r"(addEventListener\s*\([^,]+,\s*function\s*\([^)]*\)\s*\{[^}]*?)\bconst\s+(\w+)\s*=\s*this\s*;",
        r"\1const \2 = e.currentTarget;",
        script_js,
        flags=re.DOTALL,
    )

    eslint_disables = [
        "@typescript-eslint/no-unused-vars",
        "@typescript-eslint/no-unused-expressions",
        "@typescript-eslint/no-explicit-any",
        "@typescript-eslint/no-this-alias",
        "no-undef",
    ]
    if re.search(r"\bnew Set\b", script_js):
        eslint_disables.append("svelte/prefer-svelte-reactivity")
    eslint_disables.append("no-useless-assignment")
    eslint_disables.append("no-useless-escape")
    eslint_disable_str = ", ".join(eslint_disables)

    svelte_content = (
        "<script>\n"
        f"\t/* eslint-disable {eslint_disable_str} */\n"
        "\timport { onMount } from 'svelte';\n\n"
        "\tlet actions = new Proxy(\n"
        "\t\t{},\n"
        "\t\t{\n"
        "\t\t\tget: (target, prop) => {\n"
        "\t\t\t\tif (prop === 'then') return undefined;\n"
        "\t\t\t\tif (typeof prop !== 'string') return (..._args) => {};\n"
        "\t\t\t\tif (prop in target) return target[prop];\n"
        "\t\t\t\treturn (..._args) => {};\n"
        "\t\t\t}\n"
        "\t\t}\n"
        "\t);\n\n"
        "\tonMount(() => {\n" + script_js + "\n\n"
        "\t\t" + actions_bindings + "\n\n"
        "\t\treturn () => {\n"
        "\t\t\t" + cleanup_str + "\n"
        "\t\t};\n"
        "\t});\n"
        "</script>\n\n" + html_content + "\n\n"
        "<style>\n" + css + "\n"
        "</style>\n"
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svelte_content)

    print(f"Successfully converted {input_path} to {output_path}.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_module.py <input_path> <output_path>")
    else:
        convert_module(sys.argv[1], sys.argv[2])
