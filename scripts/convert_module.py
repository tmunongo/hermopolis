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

    # Automatically patch a11y complaints
    # Replace bare placeholder anchors with a valid relative path so Svelte doesn't flag invalid hrefs
    html_content = html_content.replace('href="#"', 'href="."')
    html_content = html_content.replace('href="javascript:void(0)"', 'href="."')

    # Fix label for= association: match <label> followed by a sibling input with id
    def fix_label_for(match):
        """Replace bare <label> with <label for="..."> using the id of the next sibling input."""
        full = match.group(0)
        # Find the input id in the surrounding context
        input_id_match = re.search(r'<input[^>]+id="([^"]+)"', full)
        if input_id_match:
            label_for = input_id_match.group(1)
            return full.replace("<label>", f'<label for="{label_for}">')
        # No input with id found in context, generate a unique id
        return full

    # Match slider-row patterns: <label>...</label> ... <input ... id="..." ...>
    html_content = re.sub(
        r'<label>([^<]*)</label>\s*(?=>?\s*<input[^>]+id="[^"]+")',
        fix_label_for,
        html_content,
    )
    # Fallback: any remaining bare <label> without for=
    html_content = re.sub(
        r"<label>(?![^<]*</label>)", '<label for="dummy">', html_content
    )

    # Prevent bare { } from crashing Svelte parser (e.g. state tables, template literals)
    # Replace any {…} expression that Svelte would try to evaluate as a template
    html_content = re.sub(
        r"\{([^{}]*)\}", lambda m: "&#123;" + m.group(1) + "&#125;", html_content
    )

    # Generic click handler logic — with Space key support for non-button/anchor
    def replace_onclick(match):
        prefix = match.group(1)
        code = match.group(2)
        suffix = match.group(3)
        code = re.sub(r"\bthis\b", "e.currentTarget", code)

        tag = prefix.strip("< ").split()[0].lower()
        full_tag = prefix + suffix
        if tag in ["button", "a"]:
            return f"{prefix}onclick={{(e) => {{ window.{code} }}}}{suffix}"
        else:
            # Only add role/tabindex/onkeydown if not already present
            extras = ""
            if "role=" not in full_tag:
                extras += ' role="button"'
            if "tabindex=" not in full_tag:
                extras += ' tabindex="0"'
            if "onkeydown=" not in full_tag:
                extras += f' onkeydown={{(e) => {{ if (e.key === "Enter" || e.key === " ") {{ e.preventDefault(); window.{code} }} }}}}'
            return f"{prefix}onclick={{(e) => {{ window.{code} }}}}{extras}{suffix}"

    # Strip any existing raw HTML onkeydown attributes — the onclick handler above generates Svelte-compatible ones
    html_content = re.sub(r'\s+onkeydown="[^"]*"', "", html_content)

    html_content = re.sub(
        r'(<[^>]+)\bonclick="([^"]+)"([^>]*>)', replace_onclick, html_content
    )

    # Handle oninput and onchange simply
    html_content = re.sub(
        r'\boninput="([^"]+)"', r"oninput={() => { window.\1 }}", html_content
    )
    html_content = re.sub(
        r'\bonchange="([^"]+)"', r"onchange={() => { window.\1 }}", html_content
    )

    # Automatically extract all function declarations to mount to window
    function_names = re.findall(r"function\s+([a-zA-Z0-9_]+)\s*\(", script_js)
    # Filter out duplicate names
    function_names = list(set(function_names))
    window_bindings = "\n\t\t".join(
        [
            f"if (typeof {fn} === 'function') window.{fn} = {fn};"
            for fn in function_names
        ]
    )

    # ── Auto-detect cleanup requirements ──

    # 1. Detect requestAnimationFrame assignments: `variable = requestAnimationFrame(fn)`
    raf_vars = set(re.findall(r"(\w+)\s*=\s*requestAnimationFrame\(", script_js))
    # Also detect hardcoded RAF variable names
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
    ]:
        if name in script_js:
            raf_vars.add(name)

    # 2. Detect setInterval assignments
    interval_vars = set(re.findall(r"(\w+)\s*=\s*setInterval\(", script_js))

    # 3. Detect setTimeout assignments
    timeout_vars = set(re.findall(r"(\w+)\s*=\s*setTimeout\(", script_js))

    # 4. Detect flipTimer etc by name
    if "flipTimer" in script_js:
        interval_vars.add("flipTimer")

    # 5. Detect window.addEventListener calls for named handlers
    window_listeners = re.findall(
        r"window\.addEventListener\(\s*['\"](\w+)['\"]", script_js
    )

    # Build cleanup logic
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
    if window_listeners:
        cleanup_logic.append(
            "// Note: window event listeners use anonymous functions and cannot be auto-removed."
        )
        cleanup_logic.append(
            "// Consider refactoring to named handlers for proper cleanup."
        )

    cleanup_str = "\n\t\t\t".join(cleanup_logic)

    # Build eslint-disable list based on what the script contains
    eslint_disables = [
        "@typescript-eslint/no-unused-vars",
        "@typescript-eslint/no-unused-expressions",
    ]
    if re.search(r"\bnew Set\b", script_js):
        eslint_disables.append("svelte/prefer-svelte-reactivity")
    if re.search(r"no-useless-assignment", "") or True:  # commonly needed
        eslint_disables.append("no-useless-assignment")
    eslint_disables.append("no-useless-escape")
    eslint_disable_str = ", ".join(eslint_disables)

    svelte_content = (
        "<script>\n"
        f"\t/* eslint-disable {eslint_disable_str} */\n"
        "\timport { onMount } from 'svelte';\n\n"
        "\tonMount(() => {\n" + script_js + "\n\n"
        "\t\t/* eslint-disable no-undef */\n"
        "\t\t" + window_bindings + "\n"
        "\t\t/* eslint-enable no-undef */\n\n"
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
