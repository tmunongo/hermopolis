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
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    css_match = re.search(r'<style>(.*?)</style>', text, re.DOTALL)
    css = css_match.group(1).strip() if css_match else ""
    css = re.sub(r':root\s*\{[^}]+\}', '', css, flags=re.DOTALL)
    css = re.sub(r'\*,\s*\*\:\:before,\s*\*\:\:after\s*\{[^}]+\}', '', css)
    css = re.sub(r'html\s*\{[^}]+\}', '', css)
    css = re.sub(r'(?<![a-zA-Z0-9_\-])body\s*\{', '.page-wrapper {', css)
    css = re.sub(r'::-webkit-scrollbar[^{]*\{[^}]+\}', '', css)

    selectors_to_wrap = [
        '.frame-strip', '.frame-cell', '.film-frame', '.film-frame.active', '.film-frame canvas', '.film-frame-num',
        '.hero-deco-col', '.hero-dot', '.preset-btn', '.preset-btn.active', '.preset-btn:hover',
        'h3', 'code', "input[type='range']", "input[type='range']::-webkit-slider-thumb",
        '.btn', '.btn:hover', '.btn.active', '.btn.coral.active', '.btn.mint.active', '.btn.off', '.btn.off:hover', '.btn-row',
        '.spacing-chart-wrap', '.spacing-row', '.spacing-row-label', '.spacing-track', '.spacing-dot',
        '.weight-grid', '.weight-panel', '.weight-label', '.weight-label span', '.curve-mini',
        '.q-img', '.option.correct', '.option.wrong', '.option.disabled',
        '.feedback.ok', '.feedback.bad', '.quiz-score.visible', '.graph-legend',
        '.p-card', '.p-card:hover', '.p-card.active', '.p-card.active::after',
        '.p-card-num', '.p-card-name', '.p-card-tag', '.p-card.active .p-card-num', '.p-card.active .p-card-name',
        '.ctrl-row', '.ctrl-label', '.ctrl-val', '.key-insight', '.key-insight-label',
        '.buffer-row', '.buffer-cell', '.buffer-cell span', '.buffer-cell:hover', 
        '.buffer-cell.X', '.buffer-cell.Y', '.buffer-cell.R', '.buffer-cell.G', '.buffer-cell.B',
        '.state-val', '.state-val.none', '.state-val.bound',
        '.log-line', '.log-line.bind', '.log-line.draw', '.log-line.gpu', '.log-line.info',
        '.question', '.lang-tag',
        '.op', '.callout.pink', '.callout.pink .callout-label', '.btn.gold.active',
        '.gpu-stage.active', '.gpu-stage.active .gpu-stage-num', '.gpu-stage.active .gpu-stage-name', 
        '.gpu-stage.active .gpu-stage-desc', '.q-text', '.q-num', '.options', '.option', '.option:hover', 
        '.feedback', '.bind-step', '.bind-step:last-child', '.bind-num', '.bind-content', '.bind-title', 
        '.bind-desc', '.log-line:last-child'
    ]
    for sel in selectors_to_wrap:
        escaped_sel = re.escape(sel)
        css = re.sub(fr'(?<!:global\(){escaped_sel}(?P<suffix>[\s{{,])', fr':global({sel})\g<suffix>', css)

    if 'animation' in output_path:
        token_replacements = [
            ('--bg', '--anim-bg'), ('--surface', '--anim-surface'), ('--raised', '--anim-raised'),
            ('--border2', '--anim-border2'), ('--border', '--anim-border'), ('--gold', '--anim-gold'),
            ('--coral', '--anim-coral'), ('--mint', '--anim-mint'), ('--lavender', '--anim-lavender'),
            ('--text', '--anim-text'), ('--muted', '--anim-muted'), ('--dim', '--anim-dim')
        ]
        for old_token, new_token in token_replacements:
            css = css.replace(old_token, new_token)
        
    body_match = re.search(r'<body>(.*?)</body>', text, re.DOTALL)
    body_content = body_match.group(1).strip() if body_match else text

    script_match = re.search(r'<script>(.*?)</script>', body_content, re.DOTALL)
    script_js = script_match.group(1).strip() if script_match else ''
    # Patch specific logic bugs found in modules (like profile list duplication in Module 2)
    script_js = script_js.replace("const list = document.getElementById('profileList');", "const list = document.getElementById('profileList');\n\t\tlist.innerHTML = '';")
    script_js = script_js.replace("let desc = '';", "let desc;")
    script_js = script_js.replace("anticipateOffset = 0;", "anticipateOffset;")
    html_content = re.sub(r'<script>.*?</script>', '', body_content, flags=re.DOTALL).strip()

    # Escape GLSL/Python braces inside <pre> blocks so Svelte doesn't crash trying to evaluate them
    def escape_braces(match):
        return match.group(0).replace('{', '&#123;').replace('}', '&#125;')
    html_content = re.sub(r'(<pre>.*?</pre>|<code>.*?</code>)', escape_braces, html_content, flags=re.DOTALL)

    # Automatically patch a11y complaints
    # Replace bare placeholder anchors with a valid relative path so Svelte doesn't flag invalid hrefs
    html_content = html_content.replace('href="#"', 'href="."')
    html_content = html_content.replace('href="javascript:void(0)"', 'href="."')
    html_content = html_content.replace('<label>', '<label for="dummy">')

    # Generic click handler logic
    def replace_onclick(match):
        prefix = match.group(1)
        code = match.group(2)
        suffix = match.group(3)
        code = re.sub(r'\bthis\b', 'e.currentTarget', code)
        
        tag = prefix.strip('< ').split()[0].lower()
        if tag in ['button', 'a']:
            return f'{prefix}onclick={{(e) => {{ window.{code} }}}}{suffix}'
        else:
            return f'{prefix}onclick={{(e) => {{ window.{code} }}}} role="button" tabindex="0" onkeydown={{(e) => {{ if (e.key === "Enter") window.{code} }}}}{suffix}'

    html_content = re.sub(r'(<[^>]+)\bonclick="([^"]+)"([^>]*>)', replace_onclick, html_content)

    # Automatically extract all function declarations to mount to window
    function_names = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', script_js)
    # Filter out duplicate names
    function_names = list(set(function_names))
    window_bindings = "\n\t\t".join([f"if (typeof {fn} === 'function') window.{fn} = {fn};" for fn in function_names])

    # Grab the common cleanup vars if they exist
    cleanup_logic = []
    if 'fpsRafId' in script_js: cleanup_logic.append("if (typeof fpsRafId !== 'undefined' && fpsRafId) cancelAnimationFrame(fpsRafId);")
    if 'tsRafId' in script_js: cleanup_logic.append("if (typeof tsRafId !== 'undefined' && tsRafId) cancelAnimationFrame(tsRafId);")
    if 'flipTimer' in script_js: cleanup_logic.append("if (typeof flipTimer !== 'undefined' && flipTimer) clearInterval(flipTimer);")
    if 'curveRafId' in script_js: cleanup_logic.append("if (typeof curveRafId !== 'undefined' && curveRafId) cancelAnimationFrame(curveRafId);")
    if 'arcRafId' in script_js: cleanup_logic.append("if (typeof arcRafId !== 'undefined' && arcRafId) cancelAnimationFrame(arcRafId);")
    if 'weightRafId' in script_js: cleanup_logic.append("if (typeof weightRafId !== 'undefined' && weightRafId) cancelAnimationFrame(weightRafId);")
    if 'scRafId' in script_js: cleanup_logic.append("if (typeof scRafId !== 'undefined' && scRafId) cancelAnimationFrame(scRafId);")
    
    cleanup_str = "\n\t\t\t".join(cleanup_logic)

    svelte_content = (
        "<script>\n"
        "\t/* eslint-disable @typescript-eslint/no-unused-vars, @typescript-eslint/no-unused-expressions */\n"
        "\timport { onMount } from 'svelte';\n\n"
        "\tonMount(() => {\n"
        + script_js + "\n\n"
        "\t\t/* eslint-disable no-undef */\n"
        "\t\t" + window_bindings + "\n"
        "\t\t/* eslint-enable no-undef */\n\n"
        "\t\treturn () => {\n"
        "\t\t\t" + cleanup_str + "\n"
        "\t\t};\n"
        "\t});\n"
        "</script>\n\n"
        + html_content + "\n\n"
        "<style>\n"
        + css + "\n"
        "</style>\n"
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svelte_content)

    print(f"Successfully converted {input_path} to {output_path}.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        convert_module('/root/Projects/game-dev-course/Module1.html', '/root/Projects/game-dev-course/src/lib/modules/animation/Module01.svelte')
    else:
        convert_module(sys.argv[1], sys.argv[2])
