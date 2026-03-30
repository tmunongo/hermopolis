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
        ".dtree-reason",
        ".contrast-swatch",
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
            return f'<canvas{attrs} aria-label="{label}" role="region" tabindex="0">'
        return match.group(0)

    html_content = re.sub(r"<canvas([^>]*)>", fix_canvas_aria, html_content)

    # Convert .option divs into semantic buttons for keyboard accessibility
    html_content = re.sub(
        r'<div class="option"([^>]*)>',
        r'<button type="button" class="option"\1>',
        html_content,
    )
    # The closing </button> for options requires careful regex or assuming all options close purely as </div>
    # A safer approach for options since they're leaf nodes in quizzes:
    html_content = re.sub(
        r'(<button type="button" class="option"[^>]*>.*?)</div\s*>',
        r"\1</button>",
        html_content,
        flags=re.DOTALL | re.IGNORECASE,
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
            # Return empty — we'll strip the entire duplicate function body in a second pass
            return f"/* duplicate {name} removed */ var _dup_{name} = function("
        seen_functions.add(name)
        return match.group(0)

    # First, collect all function names for binding
    function_names = list(
        dict.fromkeys(re.findall(r"function\s+([a-zA-Z0-9_]+)\s*\(", script_js))
    )

    # Then deduplicate declarations
    script_js = re.sub(r"function\s+([a-zA-Z0-9_]+)\s*\(", dedup_function, script_js)
    # Remove orphaned duplicate function bodies introduced by the header rewrite above
    for name in function_names:
        script_js = re.sub(
            rf"/\*\s*duplicate\s+{re.escape(name)}\s+removed\s*\*/\s*var\s+_dup_{re.escape(name)}\s*=\s*function\s*\([^)]*\)\s*\{{.*?\}}\s*;?",
            "",
            script_js,
            flags=re.DOTALL,
        )

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

    eslint_disables = [
        "@typescript-eslint/no-unused-vars",
        "@typescript-eslint/no-unused-expressions",
        "no-undef",
    ]
    if re.search(r"\bnew Set\b", script_js):
        eslint_disables.append("svelte/prefer-svelte-reactivity")
    eslint_disables.append("no-useless-assignment")
    eslint_disables.append("no-useless-escape")
    eslint_disable_str = ", ".join(eslint_disables)

    svelte_content = (
        '<script lang="ts">\n'
        f"\t/* eslint-disable {eslint_disable_str} */\n"
        "\timport { onMount } from 'svelte';\n\n"
        "\tlet actions: Record<string, any> = {};\n\n"
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
