<script>
	/* eslint-disable no-undef, no-useless-assignment */
	import { onMount } from 'svelte';

	let actions = new Proxy(
		{},
		{
			get: (target, prop) => {
				if (prop === 'then') return undefined;
				if (typeof prop !== 'string') return (..._args) => {};
				if (prop in target) return target[prop];
				return (..._args) => {};
			}
		}
	);

	onMount(() => {
		const _listeners = [];
		const _addWinListener = (type, listener, options) => {
			window.addEventListener(type, listener, options);
			_listeners.push({ target: window, args: [type, listener, options] });
		};
		const _addDocListener = (type, listener, options) => {
			document.addEventListener(type, listener, options);
			_listeners.push({ target: document, args: [type, listener, options] });
		};
		/* ── READING PROGRESS ── */
		_addWinListener('scroll', () => {
			const el = document.getElementById('reading-progress');
			const d = document.documentElement.scrollHeight - window.innerHeight;
			if (d > 0) el.style.width = Math.min(100, (window.scrollY / d) * 100) + '%';
		});

		/* ════════════════════════════════════════════
   COURSE KNOWLEDGE MAP
════════════════════════════════════════════ */
		const moduleData = [
			{
				num: '01',
				title: 'Foundations',
				color: '#4aafff',
				principle:
					'Cognitive load model: viewer attention is finite and must be managed across all channels simultaneously.',
				dependsOn: 'None — this is the foundation.',
				enables: 'Modules 2–10 all apply this model to specific craft domains.',
				keyDecision:
					'Every production decision filters through: does this reduce cognitive load without losing information?'
			},
			{
				num: '02',
				title: 'Pacing',
				color: '#f5b94a',
				principle:
					'Cadence is a structural tool. Beat maps, pacing modes, and chunking control when and how the viewer receives information.',
				dependsOn: 'M01: the cognitive model explains why pacing matters.',
				enables: 'M07 (narration rhythm), M08 (editing momentum), M10 (production workflow).',
				keyDecision:
					'What is the correct pacing mode for each section — and where are the chunk boundaries?'
			},
			{
				num: '03',
				title: 'Text',
				color: '#3dd9a4',
				principle:
					'On-screen text is a visual element with spatial weight, not a transcript. Three treatments: headline, support, annotation.',
				dependsOn: 'M01: text competes in the same cognitive budget as all other visual elements.',
				enables: 'M05 (text within composition), M09 (typographic consistency).',
				keyDecision: 'What job is this text doing? Is there a simpler way to do that job?'
			},
			{
				num: '04',
				title: 'B-Roll',
				color: '#ff4f68',
				principle:
					'Five visual functions: reinforce, contrast, scale, reveal process, atmosphere. The literal trap must be actively avoided.',
				dependsOn: 'M01: b-roll adds to cognitive load and must add something commensurate.',
				enables: 'M05 (b-roll composition), M08 (redundant b-roll removal).',
				keyDecision: 'What dimension does this visual add that the narration alone cannot provide?'
			},
			{
				num: '05',
				title: 'Composition',
				color: '#4aafff',
				principle:
					'Reading path, visual weight, negative space, leading lines, and the motion budget govern every frame.',
				dependsOn:
					'M03: text is positioned within the composition. M04: b-roll provides the background.',
				enables: 'M06 (motion within a frame), M09 (consistent spatial rules).',
				keyDecision: "Where does the viewer's eye go first — is that where it should go?"
			},
			{
				num: '06',
				title: 'Motion',
				color: '#f5b94a',
				principle:
					'Functional motion: reveal, highlight, transform. Zero-based approach. Motion cost model. Narration sync window ±200ms.',
				dependsOn:
					'M05: motion operates within the composition. M02: motion events sit on the beat map.',
				enables: 'M08 (motion as edit decision), M10 (motion polishing pass).',
				keyDecision: 'Does this element need to move? If so, which function is it serving?'
			},
			{
				num: '07',
				title: 'Audio',
				color: '#3dd9a4',
				principle:
					'Four channels (narration, ambient, SFX, music) each with a defined role. Pause architecture. Pre-emphasis pause. Audio lead.',
				dependsOn: 'M02: narration rhythm is the audio expression of pacing structure.',
				enables: 'M08 (J-cut / audio transitions), M10 (narration polishing pass).',
				keyDecision:
					'What is each audio channel doing right now — and is it supporting or competing with narration?'
			},
			{
				num: '08',
				title: 'Editing',
				color: '#ff4f68',
				principle:
					'Hard cuts as default. J-cut as primary transition. Redundancy removal in three categories. Temporal compression. Momentum arc.',
				dependsOn: 'All previous modules provide the content that editing assembles.',
				enables:
					'M09: a clean edit is the canvas on which visual language is applied. M10: editing is the production phase.',
				keyDecision: "Why does the viewer's attention need to change right now?"
			},
			{
				num: '09',
				title: 'Visual Language',
				color: '#4aafff',
				principle:
					'Colour system with roles. Typographic system with three roles. Reusable components. Style guide with exclusion list.',
				dependsOn:
					'M03, M05: visual language defines the rules that text and composition follow consistently.',
				enables:
					'M10: the style guide is a pre-production asset that the production workflow depends on.',
				keyDecision:
					'Do these two frames feel like the same creator? If not, which dimension broke?'
			},
			{
				num: '10',
				title: 'Production',
				color: '#f5b94a',
				principle:
					'End-to-end workflow: pre-production → production → post-production → polishing. Six-pass finishing workflow. Self-assessment rubric.',
				dependsOn: 'All previous modules — this is the integration layer.',
				enables:
					'The next video is better than this one because the gap-recognition document identified exactly what to improve.',
				keyDecision:
					'Which of the six polishing passes revealed the most issues — and is that where I will invest development effort next?'
			}
		];

		let selectedModule = null;

		function buildModuleMap() {
			const el = document.getElementById('module-map');
			el.innerHTML = moduleData
				.map(
					(m, i) => `
    <div class="mm-cell${selectedModule === i ? ' selected' : ''}" onclick="selectModule(${i})"
      style="border-bottom:3px solid ${selectedModule === i ? m.color : 'transparent'};">
      <div class="mm-num" style="color:${selectedModule === i ? m.color : 'var(--vs-border2)'};">${m.num}</div>
      <div class="mm-title">${m.title}</div>
    </div>`
				)
				.join('');
		}

		function selectModule(i) {
			selectedModule = selectedModule === i ? null : i;
			buildModuleMap();
			const detailEl = document.getElementById('mm-detail');
			if (selectedModule === null) {
				detailEl.classList.remove('open');
				return;
			}
			const m = moduleData[i];
			detailEl.className = 'mm-detail open';
			detailEl.innerHTML = `
    <div style="font-size:10px; letter-spacing:0.12em; text-transform:uppercase; color:${m.color}; margin-bottom:0.5rem; font-weight:600;">Module ${m.num} — ${m.title}</div>
    <div style="font-size:12px; color:#fff; margin-bottom:0.75rem; line-height:1.7;"><strong>Core principle:</strong> ${m.principle}</div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; font-size:11px; color:var(--vs-muted);">
      <div><div style="color:var(--vs-muted); letter-spacing:0.1em; text-transform:uppercase; font-size:9px; margin-bottom:0.25rem;">Depends on</div><div style="color:var(--vs-text);">${m.dependsOn}</div></div>
      <div><div style="color:var(--vs-muted); letter-spacing:0.1em; text-transform:uppercase; font-size:9px; margin-bottom:0.25rem;">Enables</div><div style="color:var(--vs-text);">${m.enables}</div></div>
    </div>
    <div style="margin-top:0.75rem; padding:0.5rem 0.75rem; border-left:2px solid ${m.color}; background:color-mix(in srgb,${m.color} 5%,transparent); font-size:11px; color:var(--vs-text);">
      <span style="color:${m.color}; font-size:9px; letter-spacing:0.12em; text-transform:uppercase; font-weight:600;">Key decision: </span>${m.keyDecision}
    </div>`;
		}

		buildModuleMap();

		/* ════════════════════════════════════════════
   PRODUCTION PIPELINE
════════════════════════════════════════════ */
		const pipelineStages = [
			{
				num: '01',
				title: 'Concept & Scripting',
				badge: 'PRE-PRODUCTION',
				badgeColor: '#4aafff',
				tasks: [
					{ text: 'Define the single core insight the video delivers', ref: 'M01' },
					{
						text: 'Write the script: opening hook, concept body, insight peak, brief close',
						ref: 'M01'
					},
					{ text: 'Apply minimum viable script — remove verbal redundancy', ref: 'M08' },
					{ text: 'Mark pause architecture on script: B / S / X / P', ref: 'M07' },
					{ text: 'Verify the "so what?" test passes for every section', ref: 'M01' }
				]
			},
			{
				num: '02',
				title: 'Visual Plan & Beat Map',
				badge: 'PRE-PRODUCTION',
				badgeColor: '#4aafff',
				tasks: [
					{
						text: 'Assign a visual function (reinforce/contrast/scale/process/atmosphere) to each narration block',
						ref: 'M04'
					},
					{ text: 'Plan the progressive reveal sequence for any diagram', ref: 'M04' },
					{
						text: 'Create a beat map: mark all visual events against narration timestamps',
						ref: 'M02'
					},
					{ text: 'Check beat map for deserts (>15s) and overload clusters', ref: 'M02' },
					{ text: 'Confirm style guide is complete: colour + type + components', ref: 'M09' }
				]
			},
			{
				num: '03',
				title: 'Recording & Asset Creation',
				badge: 'PRODUCTION',
				badgeColor: '#f5b94a',
				tasks: [
					{ text: 'Record narration at 110 WPM, following marked pause structure', ref: 'M07' },
					{ text: 'Verify narration clarity: run Pass 1 (narration only)', ref: 'M10' },
					{
						text: 'Source or create b-roll using three-question method (feel → situation → footage)',
						ref: 'M04'
					},
					{ text: 'Build all graphic components using style guide specifications', ref: 'M09' },
					{ text: 'Prepare diagram reveal sequence as separate assets/layers', ref: 'M04' }
				]
			},
			{
				num: '04',
				title: 'Assembly & Rough Edit',
				badge: 'POST-PRODUCTION',
				badgeColor: '#3dd9a4',
				tasks: [
					{ text: 'Lay narration as primary track; do not adjust timing yet', ref: 'M07' },
					{ text: 'Place visuals against narration — hard cuts as default', ref: 'M08' },
					{ text: 'Add motion events aligned to narration beats (±200ms window)', ref: 'M06' },
					{
						text: 'Add J-cuts at section transitions; add ambient and music yields',
						ref: 'M07,M08'
					},
					{ text: 'Run Pass 4 (1.5× speed) — mark all pacing issues', ref: 'M10' }
				]
			},
			{
				num: '05',
				title: 'Polishing & QC',
				badge: 'POST-PRODUCTION',
				badgeColor: '#3dd9a4',
				tasks: [
					{
						text: 'Pass 2: visual only — check hierarchy, composition, text legibility',
						ref: 'M03,M05'
					},
					{ text: 'Pass 3: full AV sync — motion windows, sound cue alignment', ref: 'M06,M07' },
					{
						text: 'Pass 5: consistency — compare three frames, check colour + type drift',
						ref: 'M09'
					},
					{ text: 'Remove all decorative motion; verify zero-based motion rule', ref: 'M06' },
					{ text: 'Confirm momentum arc: peak at 65–75%; resolution is brief', ref: 'M08' }
				]
			},
			{
				num: '06',
				title: 'Fresh Eyes & Final Export',
				badge: 'DELIVERY',
				badgeColor: '#a78bfa',
				tasks: [
					{ text: 'Wait minimum 24 hours; do Pass 6 (fresh eyes)', ref: 'M10' },
					{ text: 'Write gap-recognition document: three weakest decisions and why', ref: 'M10' },
					{ text: 'Export at correct resolution and frame rate for target platform', ref: '' },
					{ text: 'Archive project files + style guide for next video in series', ref: 'M09' }
				]
			}
		];

		const pipelineChecked = {};
		let activePipelineStage = 0;

		function buildPipeline() {
			const el = document.getElementById('pipeline-stages');
			el.innerHTML = pipelineStages
				.map((stage, si) => {
					const stageChecked = stage.tasks.filter((_, ti) => pipelineChecked[`${si}-${ti}`]).length;
					const allDone = stageChecked === stage.tasks.length;
					return `<div class="pipeline-stage${activePipelineStage === si ? ' active' : ''}${allDone ? ' done' : ''}" id="ps-${si}">
      <div class="ps-header" onclick="togglePipelineStage(${si})">
        <div class="ps-num">${stage.num}</div>
        <div class="ps-title">${stage.title}</div>
        <span class="ps-badge" style="border-color:${stage.badgeColor}; color:${stage.badgeColor};">${stage.badge}</span>
        <div style="font-size:11px; color:${allDone ? 'var(--vs-mint)' : stageChecked > 0 ? 'var(--vs-amber)' : 'var(--vs-muted)'}; min-width:36px; text-align:right;">${stageChecked}/${stage.tasks.length}</div>
      </div>
      <div class="ps-body">
        <ul class="ps-tasks">
          ${stage.tasks
						.map((task, ti) => {
							const checked = pipelineChecked[`${si}-${ti}`];
							return `<li class="ps-task">
              <div class="ps-task-check${checked ? ' checked' : ''}" onclick="togglePipelineTask(${si},${ti})">${checked ? '✓' : ''}</div>
              <div class="ps-task-text${checked ? ' done' : ''}">${task.text}</div>
              ${task.ref ? `<div class="ps-module-ref">M${task.ref.replace('M', '')}</div>` : ''}
            </li>`;
						})
						.join('')}
        </ul>
      </div>
    </div>`;
				})
				.join('');
			updatePipelineProgress();
		}

		function togglePipelineStage(si) {
			activePipelineStage = activePipelineStage === si ? -1 : si;
			buildPipeline();
		}

		function togglePipelineTask(si, ti) {
			const key = `${si}-${ti}`;
			pipelineChecked[key] = !pipelineChecked[key];
			buildPipeline();
		}

		function updatePipelineProgress() {
			const total = pipelineStages.reduce((s, p) => s + p.tasks.length, 0);
			const done = Object.values(pipelineChecked).filter(Boolean).length;
			document.getElementById('pipeline-progress-val').textContent = `${done} / ${total} tasks`;
			document.getElementById('pipeline-progress-fill').style.width = `${(done / total) * 100}%`;
			document.getElementById('pipeline-progress-fill').style.background =
				done === total ? '#3dd9a4' : done > total * 0.6 ? '#f5b94a' : '#4aafff';
		}

		buildPipeline();

		/* ════════════════════════════════════════════
   PRE-PRODUCTION CHECKLIST
════════════════════════════════════════════ */
		const preProdItems = {
			'Script & Narrative': [
				{
					text: 'Single core insight identified — one sentence that completes "After watching this, the viewer will understand…"',
					priority: 'Critical',
					ref: 'M01'
				},
				{
					text: 'Script written and passes the "so what?" test for every section',
					priority: 'Critical',
					ref: 'M01'
				},
				{
					text: 'Verbal redundancy removed — minimum viable script achieved',
					priority: 'Critical',
					ref: 'M08'
				},
				{
					text: 'Pause architecture marked on script: B / S / X / P with durations',
					priority: 'Important',
					ref: 'M07'
				},
				{
					text: 'Narrative structure confirmed: hook → build → peak (at ~70%) → brief close',
					priority: 'Important',
					ref: 'M01,M08'
				}
			],
			'Visual Plan': [
				{
					text: 'Visual function assigned to each narration block',
					priority: 'Critical',
					ref: 'M04'
				},
				{
					text: 'Beat map created: all visual events mapped to narration timestamps',
					priority: 'Critical',
					ref: 'M02'
				},
				{
					text: 'No beat deserts longer than 15s; no unintentional overload clusters',
					priority: 'Critical',
					ref: 'M02'
				},
				{
					text: 'Diagram reveal sequence planned: one element per narration beat',
					priority: 'Important',
					ref: 'M04'
				},
				{
					text: 'B-roll sourced using three-question method, not subject-search',
					priority: 'Important',
					ref: 'M04'
				}
			],
			'Visual Language': [
				{
					text: 'Style guide complete: primary, secondary, signal, background hex values assigned',
					priority: 'Critical',
					ref: 'M09'
				},
				{
					text: 'Display and body typefaces selected; weight hierarchy defined',
					priority: 'Critical',
					ref: 'M09'
				},
				{
					text: 'Component specs built: lower-third, key term callout, data label',
					priority: 'Important',
					ref: 'M09'
				},
				{
					text: 'Exclusion list written: at least 3 elements explicitly prohibited',
					priority: 'Important',
					ref: 'M09'
				},
				{
					text: 'Spacing rules documented: padding, safe zone, text max-width',
					priority: 'Useful',
					ref: 'M05,M09'
				}
			],
			Audio: [
				{
					text: 'Narration WPM target set: 100–125 for explanatory content',
					priority: 'Important',
					ref: 'M07'
				},
				{
					text: 'Audio channel plan: music yield points identified in script',
					priority: 'Important',
					ref: 'M07'
				},
				{
					text: 'Sound design cue density planned: target ≤5% of total duration',
					priority: 'Useful',
					ref: 'M07'
				}
			]
		};

		const checklistState = {};

		function buildChecklist() {
			const el = document.getElementById('pre-prod-checklist');
			el.innerHTML = Object.entries(preProdItems)
				.map(
					([group, items]) => `
    <div class="checklist-group">
      <div class="checklist-group-label">${group}</div>
      ${items
				.map((item, i) => {
					const key = `${group}-${i}`;
					const checked = checklistState[key];
					const pColor =
						item.priority === 'Critical'
							? '#ff4f68'
							: item.priority === 'Important'
								? '#f5b94a'
								: '#4aafff';
					return `<div class="checklist-item">
          <div class="check-box${checked ? ' checked' : ''}" onclick="toggleCheck('${key}')">${checked ? '✓' : ''}</div>
          <div class="check-label${checked ? ' done' : ''}">
            ${item.text}
            <span style="font-size:10px; color:var(--vs-muted); margin-left:6px;">M${item.ref}</span>
          </div>
          <span class="check-priority" style="border-color:${pColor}; color:${pColor};">${item.priority}</span>
        </div>`;
				})
				.join('')}
    </div>`
				)
				.join('');
			updateChecklistReadiness();
		}

		function toggleCheck(key) {
			checklistState[key] = !checklistState[key];
			buildChecklist();
		}

		function updateChecklistReadiness() {
			const all = Object.entries(preProdItems).flatMap(([g, items]) =>
				items.map((_, i) => ({ key: `${g}-${i}`, priority: _.priority }))
			);
			const crits = all.filter((i) => i.priority === 'Critical');
			const doneC = crits.filter((i) => checklistState[i.key]).length;
			const doneAll = all.filter((i) => checklistState[i.key]).length;
			const critPct = Math.round((doneC / crits.length) * 100);
			const allPct = Math.round((doneAll / all.length) * 100);

			document.getElementById('checklist-ready-val').textContent =
				`${allPct}% complete (${doneC}/${crits.length} critical items)`;
			document.getElementById('checklist-ready-val').style.color =
				critPct === 100 ? '#3dd9a4' : critPct >= 60 ? '#f5b94a' : '#ff4f68';
			document.getElementById('checklist-ready-fill').style.width = allPct + '%';
			document.getElementById('checklist-ready-fill').style.background =
				critPct === 100 ? '#3dd9a4' : critPct >= 60 ? '#f5b94a' : '#ff4f68';

			let v;
			if (critPct === 100 && allPct === 100)
				v = '✓ All items complete. You are fully production-ready. Begin recording.';
			else if (critPct === 100)
				v = `✓ All ${crits.length} critical gates passed. Production can begin. Complete remaining ${all.length - doneAll} items during production to maximise quality.`;
			else
				v = `⚠ ${crits.length - doneC} critical item${crits.length - doneC !== 1 ? 's' : ''} incomplete. Do not begin production until all Critical items are checked — these are the decisions that cannot be recovered in post-production.`;

			document.getElementById('checklist-verdict').textContent = v;
			document.getElementById('checklist-verdict').style.borderLeftColor =
				critPct === 100 ? '#3dd9a4' : '#ff4f68';
		}

		buildChecklist();

		/* ════════════════════════════════════════════
   SELF-ASSESSMENT RUBRIC
════════════════════════════════════════════ */
		const rubricDimensions = [
			{
				id: 'narrative',
				name: 'Narrative Clarity',
				module: 'M01',
				levels: [
					{
						score: 1,
						label: 'Developing',
						color: '#ff4f68',
						desc: 'The video presents information but the "so what?" is unclear. Viewer cannot explain why the content mattered after watching.'
					},
					{
						score: 2,
						label: 'Competent',
						color: '#f5b94a',
						desc: 'Clear argument structure with identifiable hook and insight. Some sections lack narrative momentum but the overall logic holds.'
					},
					{
						score: 3,
						label: 'Skilled',
						color: '#3dd9a4',
						desc: 'Viewer is pulled through a felt narrative arc. Stakes are established early; the insight lands with weight. "So what?" is unambiguous.'
					}
				]
			},
			{
				id: 'pacing',
				name: 'Pacing & Rhythm',
				module: 'M02,M07',
				levels: [
					{
						score: 1,
						label: 'Developing',
						color: '#ff4f68',
						desc: 'Uniform or uncontrolled pacing. No evidence of beat mapping. Sections feel either rushed or padded. Viewer cannot locate chunk boundaries.'
					},
					{
						score: 2,
						label: 'Competent',
						color: '#f5b94a',
						desc: 'Pacing varies intentionally in at least two sections. Pauses separate major sections. Some padding remains at 1.5× speed.'
					},
					{
						score: 3,
						label: 'Skilled',
						color: '#3dd9a4',
						desc: 'Deliberate three-tier pause architecture (breath/sentence/section). No deserts; no overload clusters. 1.5× speed reveals no significant padding.'
					}
				]
			},
			{
				id: 'visual',
				name: 'Visual Communication',
				module: 'M03,M04,M05',
				levels: [
					{
						score: 1,
						label: 'Developing',
						color: '#ff4f68',
						desc: 'Text is transcriptive or clutter-heavy. B-roll is literal. Composition is accidental. No clear reading path in most frames.'
					},
					{
						score: 2,
						label: 'Competent',
						color: '#f5b94a',
						desc: 'Three text treatments present and differentiated. B-roll adds at least reinforcement function. Composition guides eye in key frames.'
					},
					{
						score: 3,
						label: 'Skilled',
						color: '#3dd9a4',
						desc: 'Every text element has a defined job. B-roll serves non-literal functions. Visual hierarchy and reading path are deliberate in all frames.'
					}
				]
			},
			{
				id: 'motion',
				name: 'Motion & Audio Design',
				module: 'M06,M07',
				levels: [
					{
						score: 1,
						label: 'Developing',
						color: '#ff4f68',
						desc: 'Motion is primarily decorative. Audio channels compete. Narration pacing and sync are not deliberate. No evidence of the functional test applied.'
					},
					{
						score: 2,
						label: 'Competent',
						color: '#f5b94a',
						desc: "Motion events are mostly functional (reveal/highlight/transform). One or two decorative animations remain. Audio channels don't actively compete during narration."
					},
					{
						score: 3,
						label: 'Skilled',
						color: '#3dd9a4',
						desc: 'All motion is functional and within the ±200ms sync window. Audio channels yield during dense narration. Sound design cues are present and below 5% density.'
					}
				]
			},
			{
				id: 'editing',
				name: 'Editing & Momentum',
				module: 'M08',
				levels: [
					{
						score: 1,
						label: 'Developing',
						color: '#ff4f68',
						desc: 'Uniform cross-dissolves throughout. Significant structural redundancy. No clear momentum arc. Video extends past its natural end.'
					},
					{
						score: 2,
						label: 'Competent',
						color: '#f5b94a',
						desc: 'Hard cuts are the majority. One J-cut present. Obvious redundancy removed. A momentum arc is present though the peak position may be off.'
					},
					{
						score: 3,
						label: 'Skilled',
						color: '#3dd9a4',
						desc: 'Every cut type is justified. Minimum viable script achieved. Peak lands at 65–75%. Resolution is brief. 1.5× speed reveals no padding.'
					}
				]
			},
			{
				id: 'consistency',
				name: 'Visual Language',
				module: 'M09',
				levels: [
					{
						score: 1,
						label: 'Developing',
						color: '#ff4f68',
						desc: 'Colour and typography vary across the video. Components look different each time they appear. No evidence of a style guide applied.'
					},
					{
						score: 2,
						label: 'Competent',
						color: '#f5b94a',
						desc: 'Primary accent is consistent. Typeface is consistent. Two or more components reuse the same design. Minor colour drift in background elements.'
					},
					{
						score: 3,
						label: 'Skilled',
						color: '#3dd9a4',
						desc: 'Any two frames pass the same-creator test. All four colour roles used correctly. All component instances are identical. Exclusion list respected throughout.'
					}
				]
			}
		];

		const rubricScores = {};

		function buildRubric() {
			const el = document.getElementById('rubric-dimensions');
			el.innerHTML = rubricDimensions
				.map(
					(dim) => `
    <div class="rubric-dimension">
      <div class="rubric-dim-header">
        <div class="rubric-dim-name">${dim.name}</div>
        <span class="rubric-dim-module">Module ${dim.module}</span>
        <div style="font-family:'Syne',sans-serif; font-size:18px; font-weight:700; min-width:32px; text-align:right;
          color:${rubricScores[dim.id] ? dim.levels[rubricScores[dim.id] - 1].color : 'var(--vs-muted)'};">
          ${rubricScores[dim.id] || '—'}
        </div>
      </div>
      <div class="rubric-levels">
        ${dim.levels
					.map(
						(lv) => `
          <div class="rubric-level${rubricScores[dim.id] === lv.score ? ' selected-' + lv.score : ''}"
            onclick="scoreRubric('${dim.id}',${lv.score})">
            <div class="rl-score" style="color:${lv.color};">${lv.score}</div>
            <div class="rl-label" style="color:${lv.color};">${lv.label}</div>
            <div class="rl-desc">${lv.desc}</div>
          </div>`
					)
					.join('')}
      </div>
    </div>`
				)
				.join('');
			updateRubricTotal();
		}

		function scoreRubric(id, score) {
			rubricScores[id] = rubricScores[id] === score ? undefined : score;
			buildRubric();
		}

		function updateRubricTotal() {
			const scores = Object.values(rubricScores).filter((v) => v !== undefined);
			const total = scores.reduce((a, b) => a + b, 0);
			const rated = scores.length;
			const max = rubricDimensions.length * 3;

			document.getElementById('rubric-total-val').textContent = `${total} / ${max}`;
			document.getElementById('rubric-total-val').style.color =
				total >= 15 ? '#3dd9a4' : total >= 10 ? '#f5b94a' : '#ff4f68';
			const fillEl = document.getElementById('rubric-total-fill');
			fillEl.style.width = (total / max) * 100 + '%';
			fillEl.style.background = total >= 15 ? '#3dd9a4' : total >= 10 ? '#f5b94a' : '#ff4f68';

			if (rated === 0) {
				document.getElementById('rubric-verdict').textContent =
					'Rate each dimension to generate your quality assessment.';
				return;
			}

			const weakest = rubricDimensions
				.filter((d) => rubricScores[d.id] !== undefined)
				.sort((a, b) => (rubricScores[a.id] || 0) - (rubricScores[b.id] || 0))[0];
			const strongest = rubricDimensions
				.filter((d) => rubricScores[d.id] !== undefined)
				.sort((a, b) => (rubricScores[b.id] || 0) - (rubricScores[a.id] || 0))[0];

			let v = '';
			if (rated < rubricDimensions.length)
				v = `${rated}/${rubricDimensions.length} dimensions rated. `;
			if (total >= 15) v += `✓ Strong performance (${total}/${max}). `;
			else if (total >= 10) v += `Competent performance (${total}/${max}). `;
			else v += `Developing (${total}/${max}). `;

			if (weakest && rubricScores[weakest.id]) {
				const lvl = weakest.levels[rubricScores[weakest.id] - 1];
				v += `Weakest dimension: ${weakest.name} (${rubricScores[weakest.id]}/3 — ${lvl.label}). This is your highest-return improvement target for the next video. `;
			}
			if (strongest && rubricScores[strongest.id] === 3)
				v += `Strongest dimension: ${strongest.name} — maintain this standard.`;

			document.getElementById('rubric-verdict').textContent = v;
			document.getElementById('rubric-verdict').style.borderLeftColor =
				total >= 15 ? '#3dd9a4' : total >= 10 ? '#f5b94a' : '#ff4f68';
		}

		buildRubric();

		/* ════════════════════════════════════════════
   VIDEO QUALITY SIMULATOR
════════════════════════════════════════════ */
		const vpsParams = {
			narrative: { label: 'Narrative Clarity', val: 70, module: 'M01' },
			pacing: { label: 'Pacing & Rhythm', val: 70, module: 'M02' },
			visual: { label: 'Visual Hierarchy', val: 70, module: 'M03–05' },
			motion: { label: 'Motion Restraint', val: 70, module: 'M06' },
			audio: { label: 'Audio Design', val: 70, module: 'M07' },
			editing: { label: 'Edit Quality', val: 70, module: 'M08' }
		};

		function buildVPSControls() {
			const el = document.getElementById('vps-controls');
			el.innerHTML = Object.entries(vpsParams)
				.map(
					([id, p]) => `
    <div class="vps-control">
      <div class="vps-control-label">${p.label} <span style="color:var(--vs-border2);">· ${p.module}</span></div>
      <div class="vps-slider-row">
        <div class="vps-slider-label">Quality</div>
        <input type="range" class="vps-slider" id="vps-${id}" min="10" max="100" value="${p.val}" oninput="updateVPS('${id}',+this.value)">
        <span class="vps-val" id="vpsv-${id}">${p.val}%</span>
      </div>
    </div>`
				)
				.join('');
			drawVPS();
			updateVPSScores();
		}

		function updateVPS(id, val) {
			vpsParams[id].val = val;
			document.getElementById('vpsv-' + id).textContent = val + '%';
			drawVPS();
			updateVPSScores();
		}

		function drawVPS() {
			const canvas = document.getElementById('vps-canvas');
			if (!canvas) return;
			const dpr = window.devicePixelRatio || 1;
			const W = canvas.offsetWidth || 560;
			const H = (W * 9) / 16;
			if (canvas.width !== W * dpr) {
				canvas.width = W * dpr;
				canvas.height = H * dpr;
				canvas.style.height = H + 'px';
				canvas.getContext('2d').scale(dpr, dpr);
			}
			const ctx = canvas.getContext('2d');
			ctx.clearRect(0, 0, W, H);

			const vals = Object.values(vpsParams).map((p) => p.val / 100);
			const composite = vals.reduce((a, b) => a * Math.pow(b, 1 / vals.length), 1); // geometric mean
			const compPct = Math.round(composite * 100);

			// Background quality: darker/noisier with lower scores
			const bgNoise = 1 - vpsParams.visual.val / 100;
			ctx.fillStyle = `rgb(${Math.round(4 + bgNoise * 20)},${Math.round(8 + bgNoise * 12)},${Math.round(16 + bgNoise * 8)})`;
			ctx.fillRect(0, 0, W, H);

			// Grid (more chaotic with lower visual quality)
			const gridAlpha = 0.02 + (vpsParams.visual.val / 100) * 0.04;
			ctx.strokeStyle = `rgba(74,175,255,${gridAlpha})`;
			ctx.lineWidth = 0.5;
			const gridDensity = vpsParams.visual.val > 60 ? 8 : 5;
			for (let x = 0; x < W; x += W / gridDensity) {
				ctx.beginPath();
				ctx.moveTo(x, 0);
				ctx.lineTo(x, H);
				ctx.stroke();
			}

			// ── Narrative layer ──
			const narrativeAlpha = vpsParams.narrative.val / 100;
			ctx.font = `800 ${W * 0.065}px Syne,sans-serif`;
			ctx.fillStyle = `rgba(255,255,255,${0.4 + narrativeAlpha * 0.55})`;
			ctx.textAlign = 'left';
			const headline =
				vpsParams.narrative.val > 70
					? 'The Signal Reaches'
					: vpsParams.narrative.val > 40
						? 'Some Kind of Title'
						: 'Text Here';
			ctx.fillText(headline, W * 0.06, H * 0.38);
			ctx.fillStyle = `rgba(245,185,74,${0.3 + narrativeAlpha * 0.65})`;
			ctx.fillText('Through', W * 0.06, H * 0.52);
			ctx.fillStyle = `rgba(245,185,74,${narrativeAlpha * 0.8})`;
			ctx.fillRect(W * 0.06, H * 0.56, W * 0.22, 2);

			// ── Visual hierarchy layer ──
			const hier = vpsParams.visual.val / 100;
			ctx.font = `${W * 0.022}px IBM Plex Mono`;
			ctx.fillStyle = `rgba(184,200,222,${0.2 + hier * 0.55})`;
			if (hier > 0.5) {
				ctx.fillText('Secondary — supporting context', W * 0.06, H * 0.67);
				ctx.font = `${W * 0.016}px IBM Plex Mono`;
				ctx.fillStyle = `rgba(74,175,255,${hier * 0.6})`;
				ctx.fillText('annotation · ref', W * 0.06, H * 0.75);
			} else {
				ctx.fillText('same size as headline text is not great', W * 0.06, H * 0.67);
				ctx.fillText('annotation at same size competing', W * 0.06, H * 0.73);
				ctx.fillText('more text here also at same weight', W * 0.06, H * 0.79);
			}

			// ── Motion layer ── (overuse shown with decorative noise when low)
			const motionQ = vpsParams.motion.val / 100;
			if (motionQ < 0.5) {
				// Decorative noise: random pulsing elements
				const t = Date.now() / 1000;
				for (let i = 0; i < 5; i++) {
					const px = W * (0.5 + 0.3 * Math.sin(t + i * 1.3)),
						py = H * (0.3 + 0.2 * Math.cos(t * 0.7 + i));
					const r = W * 0.03 * (1 - motionQ);
					ctx.beginPath();
					ctx.arc(px, py, r, 0, Math.PI * 2);
					ctx.strokeStyle = `rgba(255,79,104,${(1 - motionQ) * 0.4})`;
					ctx.lineWidth = 1;
					ctx.stroke();
				}
			} else {
				// Clean reveal indicator
				ctx.fillStyle = `rgba(61,217,164,${motionQ * 0.2})`;
				ctx.fillRect(W * 0.7, H * 0.1, W * 0.24, H * 0.35);
				ctx.font = `${W * 0.016}px IBM Plex Mono`;
				ctx.fillStyle = `rgba(61,217,164,${motionQ * 0.5})`;
				ctx.textAlign = 'center';
				ctx.fillText('diagram zone', W * 0.82, H * 0.29);
				ctx.textAlign = 'left';
			}

			// ── Audio visual: pacing indicator ──
			const pacingQ = vpsParams.pacing.val / 100;
			const numBars = Math.round(3 + pacingQ * 9);
			for (let i = 0; i < numBars; i++) {
				const bx = W * 0.06 + i * ((W * 0.88) / numBars);
				const bh = H * 0.04 * (0.4 + Math.sin(i * 1.7) * 0.3 + pacingQ * 0.3);
				ctx.fillStyle = `rgba(74,175,255,${0.08 + pacingQ * 0.12})`;
				ctx.fillRect(bx, H * 0.91, (W * 0.88) / numBars - 2, bh);
			}

			// ── Lower third ──
			const editQ = vpsParams.editing.val / 100;
			if (editQ > 0.5) {
				ctx.fillStyle = `rgba(0,0,0,${0.5 + editQ * 0.3})`;
				ctx.fillRect(0, H * 0.84, W, H * 0.16);
				ctx.fillStyle = `rgba(245,185,74,${editQ * 0.9})`;
				ctx.fillRect(W * 0.04, H * 0.86, 2, H * 0.1);
				ctx.font = `700 ${W * 0.022}px Syne`;
				ctx.fillStyle = `rgba(255,255,255,${editQ * 0.85})`;
				ctx.fillText('Clean · Consistent · Structured', W * 0.06, H * 0.93);
			} else {
				ctx.fillStyle = 'rgba(0,0,0,0.3)';
				ctx.fillRect(0, H * 0.82, W, H * 0.18);
				ctx.font = `${W * 0.014}px monospace`;
				ctx.fillStyle = `rgba(255,100,100,${0.4})`;
				ctx.fillText('Some kind of text here lorem ipsum', W * 0.05, H * 0.9);
				ctx.font = `${W * 0.025}px Georgia`;
				ctx.fillStyle = 'rgba(255,255,100,0.3)';
				ctx.fillText('DIFFERENT FONT ALSO', W * 0.05, H * 0.96);
			}

			// ── Composite score overlay ──
			const scoreCol = compPct >= 75 ? '#3dd9a4' : compPct >= 50 ? '#f5b94a' : '#ff4f68';
			ctx.font = `700 ${W * 0.05}px Syne,sans-serif`;
			ctx.fillStyle = scoreCol + 'cc';
			ctx.textAlign = 'right';
			ctx.fillText(compPct + '%', W * 0.94, H * 0.12);
			ctx.font = `${W * 0.014}px IBM Plex Mono`;
			ctx.fillStyle = scoreCol + '80';
			ctx.fillText('composite', W * 0.94, H * 0.19);
			ctx.textAlign = 'left';
		}

		function updateVPSScores() {
			const vals = Object.values(vpsParams).map((p) => p.val / 100);
			const composite = Math.round(
				vals.reduce((a, b) => a * Math.pow(b, 1 / vals.length), 1) * 100
			);
			const weakest = Object.entries(vpsParams).sort((a, b) => a[1].val - b[1].val)[0];
			const strongest = Object.entries(vpsParams).sort((a, b) => b[1].val - a[1].val)[0];

			const scoreEl = document.getElementById('vps-scores');
			const scoreItems = [
				{
					label: 'Composite',
					val: composite + '%',
					color: composite >= 75 ? '#3dd9a4' : composite >= 50 ? '#f5b94a' : '#ff4f68'
				},
				{ label: 'Weakest', val: weakest[1].label.split(' ')[0], color: '#ff4f68' },
				{ label: 'Strongest', val: strongest[1].label.split(' ')[0], color: '#3dd9a4' },
				{
					label: 'All ≥70?',
					val: vals.every((v) => v >= 0.7) ? 'YES' : 'NO',
					color: vals.every((v) => v >= 0.7) ? '#3dd9a4' : '#ff4f68'
				}
			];
			scoreEl.innerHTML = scoreItems
				.map(
					(s) =>
						`<div class="vps-score-cell"><div class="vps-score-val" style="color:${s.color};">${s.val}</div><div class="vps-score-lbl">${s.label}</div></div>`
				)
				.join('');

			let verdict = '';
			if (composite >= 80)
				verdict = `✓ High composite quality (${composite}%). All layers are working together. A viewer watching this video will not need to compensate for any single weak layer.`;
			else if (composite >= 60)
				verdict = `Moderate composite quality (${composite}%). Most layers are working but ${weakest[1].label} is your lowest dimension at ${weakest[1].val}%. That weakness reduces the return on investment in all the stronger layers.`;
			else
				verdict = `⚠ Composite quality is low (${composite}%). The geometric mean compounds weaknesses — a 20% reduction in one dimension reduces the composite by more than 20%. Prioritise: raise ${weakest[1].label} (${weakest[1].val}%) first, as it has the highest leverage on the overall score.`;

			document.getElementById('vps-verdict').textContent = verdict;
			document.getElementById('vps-verdict').style.borderLeftColor =
				composite >= 75 ? '#3dd9a4' : composite >= 50 ? '#f5b94a' : '#ff4f68';
			drawVPS();
		}

		buildVPSControls();
		// Animate the decorative noise when motion quality is low
		(function animateVPS() {
			const hasLowMotion = vpsParams.motion.val < 50;
			if (hasLowMotion) drawVPS();
			requestAnimationFrame(animateVPS);
		})();
		_addWinListener('resize', () => {
			const canvas = document.getElementById('vps-canvas');
			if (!canvas) return;
			const dpr = window.devicePixelRatio || 1;
			const W = canvas.offsetWidth || 560;
			canvas.width = W * dpr;
			canvas.height = ((W * 9) / 16) * dpr;
			canvas.style.height = (W * 9) / 16 + 'px';
			canvas.getContext('2d').scale(dpr, dpr);
			drawVPS();
		});

		/* ── QUIZ ── */
		const scores = {};
		function answer(qId, el, correct) {
			if (scores[qId] !== undefined) return;
			scores[qId] = correct ? 1 : 0;
			el.parentElement.querySelectorAll('.option').forEach((o) => {
				o.classList.add('disabled');
				if (o.onclick.toString().includes(',true)')) o.classList.add('correct');
			});
			el.classList.remove('correct');
			if (!correct) el.classList.add('wrong');
			const fb = document.getElementById('fb-' + qId);
			fb.textContent = correct
				? '✓ Correct.'
				: '✗ Not quite — the correct answer is highlighted above.';
			fb.className = 'feedback ' + (correct ? 'ok' : 'bad');
			if (Object.keys(scores).length === 4) {
				const total = Object.values(scores).reduce((a, b) => a + b, 0);
				const sc = document.getElementById('quiz-score');
				sc.style.display = 'block';
				document.getElementById('score-display').textContent = total + ' / 4';
				document.getElementById('score-display').style.color =
					total >= 3 ? 'var(--vs-mint)' : total >= 2 ? 'var(--vs-amber)' : 'var(--vs-red)';
				if (total >= 3) {
					setTimeout(() => {
						document.getElementById('course-complete-msg').style.display = 'block';
					}, 400);
				}
			}
		}

		if (typeof buildModuleMap === 'function') actions.buildModuleMap = buildModuleMap;
		if (typeof selectModule === 'function') actions.selectModule = selectModule;
		if (typeof buildPipeline === 'function') actions.buildPipeline = buildPipeline;
		if (typeof togglePipelineStage === 'function')
			actions.togglePipelineStage = togglePipelineStage;
		if (typeof togglePipelineTask === 'function') actions.togglePipelineTask = togglePipelineTask;
		if (typeof updatePipelineProgress === 'function')
			actions.updatePipelineProgress = updatePipelineProgress;
		if (typeof buildChecklist === 'function') actions.buildChecklist = buildChecklist;
		if (typeof toggleCheck === 'function') actions.toggleCheck = toggleCheck;
		if (typeof updateChecklistReadiness === 'function')
			actions.updateChecklistReadiness = updateChecklistReadiness;
		if (typeof buildRubric === 'function') actions.buildRubric = buildRubric;
		if (typeof scoreRubric === 'function') actions.scoreRubric = scoreRubric;
		if (typeof updateRubricTotal === 'function') actions.updateRubricTotal = updateRubricTotal;
		if (typeof buildVPSControls === 'function') actions.buildVPSControls = buildVPSControls;
		if (typeof updateVPS === 'function') actions.updateVPS = updateVPS;
		if (typeof drawVPS === 'function') actions.drawVPS = drawVPS;
		if (typeof updateVPSScores === 'function') actions.updateVPSScores = updateVPSScores;
		if (typeof animateVPS === 'function') actions.animateVPS = animateVPS;
		if (typeof answer === 'function') actions.answer = answer;

		return () => {
			_listeners.forEach((l) => l.target.removeEventListener(...l.args));
		};
	});
</script>

<div class="page-wrapper">
	<header class="course-header">
		<div>
			<div class="course-label">Visual Storytelling for Faceless Video</div>
			<div class="course-title">Narrative, Pacing &amp; Visual Communication</div>
		</div>
		<div style="font-size: 11px; color: var(--vs-muted); text-align: right">Module 10 of 10</div>
	</header>

	<div class="module-hero">
		<div class="module-number">10</div>
		<div class="capstone-badge">⬡ Capstone Module</div>
		<h1 class="module-title">End-to-End<br /><span>Faceless Video Production</span></h1>
		<div class="progress-bar-wrap">
			<div
				class="progress-bar-fill"
				id="reading-progress"
				role="progressbar"
				aria-valuemin="0"
				aria-valuemax="100"
				aria-valuenow="0"
			></div>
		</div>
	</div>

	<nav class="toc">
		<div class="toc-label">Contents</div>
		<ul class="toc-list">
			<li><a href="#objectives">Objectives</a></li>
			<li><a href="#course-map">Course Knowledge Map</a></li>
			<li><a href="#workflow">Production Workflow</a></li>
			<li><a href="#preproduction">Pre-Production Checklist</a></li>
			<li><a href="#polishing">Final Polishing Workflow</a></li>
			<li><a href="#self-assessment">Self-Assessment Rubric</a></li>
			<li><a href="#simulator">Video Quality Simulator</a></li>
			<li><a href="#final-project">Final Project</a></li>
			<li><a href="#quiz">Quiz</a></li>
		</ul>
	</nav>

	<section id="objectives" class="objectives">
		<div class="objectives-label">Learning Objectives</div>
		<ul>
			<li>Integrate all course concepts into a coherent end-to-end production workflow</li>
			<li>Apply the pre-production checklist to a video before beginning production</li>
			<li>Self-assess a completed video against the six-dimension quality rubric</li>
			<li>Produce a complete 1–2 minute faceless video using all course principles</li>
		</ul>
	</section>

	<!-- ═══ COURSE KNOWLEDGE MAP ═══ -->
	<section id="course-map" class="section">
		<div class="section-header">
			<span class="section-num">10.01</span>
			<h2 class="section-title">Course Knowledge Map</h2>
		</div>

		<p>
			Before building the production workflow, it is worth mapping how the ten modules relate to
			each other. The course is not a linear sequence of independent topics — it is a set of layers
			that build on each other. Module 1 established the cognitive model for viewer attention. Every
			subsequent module is, in some sense, an application of that model to a specific craft domain.
			Understanding how the layers relate is what allows you to make decisions when two principles
			appear to conflict.
		</p>

		<!-- DEMO: Course Module Map -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Course Knowledge Map</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					Click any module to see its core principle, what it depends on, and what it enables.
					Understanding these relationships helps you prioritise when you cannot perfect every layer
					simultaneously.
				</p>
				<div class="module-map" id="module-map"></div>
				<div class="mm-detail" id="mm-detail"></div>
			</div>
		</div>

		<p>
			The dependencies flow in one direction: cognitive and structural principles (Modules 1–2)
			underpin everything else. If pacing is broken, no amount of well-designed text or precisely
			timed motion will rescue the video. The craft layers (Modules 3–7) are how you execute the
			structure. The integration layers (Modules 8–9) are how you make the execution consistent and
			efficient. This module is where you produce the whole.
		</p>
	</section>

	<!-- ═══ PRODUCTION WORKFLOW ═══ -->
	<section id="workflow" class="section">
		<div class="section-header">
			<span class="section-num">10.02</span>
			<h2 class="section-title">The End-to-End Production Workflow</h2>
		</div>

		<p>
			A production workflow is a sequence of phases, each with defined deliverables, that transforms
			an idea into a finished video. Without a defined workflow, production sprawls: decisions are
			revisited, assets are made before their context is clear, and the edit reflects accumulated
			accidents rather than deliberate choices. The workflow is the structure that prevents this.
		</p>
		<p>
			The workflow below is designed for faceless video specifically. It differs from general video
			production in one important way: because there is no on-camera presenter, the script and
			visual plan must be more fully resolved before recording begins. A talking head can improvise;
			a faceless video's visual layer must be designed, not discovered. This shifts significant work
			into pre-production.
		</p>

		<!-- DEMO: Production Pipeline -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Production Pipeline Tracker</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					Click each phase to expand its task list. Check off tasks as you complete them. The
					pipeline tracks your progress across all phases.
				</p>
				<div id="pipeline-stages"></div>
				<div style="margin-top: 1.25rem">
					<div
						style="
									display: flex;
									justify-content: space-between;
									font-size: 11px;
									margin-bottom: 5px;
								"
					>
						<span style="color: var(--vs-muted)">Pipeline progress</span>
						<span id="pipeline-progress-val" style="color: var(--vs-amber); font-weight: 600"
							>0 / 0 tasks</span
						>
					</div>
					<div
						style="
									height: 6px;
									background: var(--vs-border);
									border-radius: 3px;
									overflow: hidden;
								"
					>
						<div
							id="pipeline-progress-fill"
							style="
										height: 100%;
										background: var(--vs-amber);
										width: 0%;
										border-radius: 3px;
										transition: width 0.4s ease;
									"
						></div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ═══ PRE-PRODUCTION CHECKLIST ═══ -->
	<section id="preproduction" class="section">
		<div class="section-header">
			<span class="section-num">10.03</span>
			<h2 class="section-title">Pre-Production Checklist</h2>
		</div>

		<p>
			Pre-production is the phase that determines whether production is controlled or chaotic. Every
			decision that is not made before production begins will be made during it — under time
			pressure, with incomplete information, in the context of sunk cost. The pre-production
			checklist exists to front-load all decisions that can be made in advance, so that production
			is execution rather than discovery.
		</p>
		<p>
			The items marked <strong>Critical</strong> are gates: if they are not complete, production
			should not begin. The items marked <strong>Important</strong> should be completed but can be
			refined during production. Items marked <strong>Useful</strong> improve quality but do not block
			the workflow.
		</p>

		<!-- DEMO: Pre-Production Checklist -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Pre-Production Checklist</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					Work through the checklist before starting production on any video. Critical items are
					gates — do not begin until they are checked. Your completion status is saved for this
					session.
				</p>

				<div id="pre-prod-checklist"></div>

				<div style="margin-top: 1.25rem">
					<div
						style="
									display: flex;
									justify-content: space-between;
									font-size: 11px;
									margin-bottom: 5px;
								"
					>
						<span style="color: var(--vs-muted)">Readiness</span>
						<span id="checklist-ready-val" style="font-weight: 600">—</span>
					</div>
					<div
						style="
									height: 8px;
									background: var(--vs-border);
									border-radius: 4px;
									overflow: hidden;
								"
					>
						<div
							id="checklist-ready-fill"
							style="
										height: 100%;
										border-radius: 4px;
										transition:
											width 0.4s ease,
											background 0.3s;
									"
						></div>
					</div>
				</div>
				<div
					id="checklist-verdict"
					style="
								margin-top: 0.75rem;
								padding: 0.75rem 1rem;
								border-left: 2px solid var(--vs-border2);
								font-size: 12px;
								color: var(--vs-text);
								line-height: 1.7;
								background: var(--vs-raised);
								min-height: 40px;
							"
				></div>
			</div>
		</div>
	</section>

	<!-- ═══ FINAL POLISHING WORKFLOW ═══ -->
	<section id="polishing" class="section">
		<div class="section-header">
			<span class="section-num">10.04</span>
			<h2 class="section-title">The Final Polishing Workflow</h2>
		</div>

		<p>
			Polishing is not the same as finishing. Finishing means the video contains all its content and
			plays from start to end. Polishing means reviewing every layer in isolation — narration only,
			then visual only, then audio mix, then the complete video — to catch the errors that only
			become visible when you stop working on a specific layer and listen or watch the whole thing
			fresh.
		</p>
		<p>
			The polishing workflow is a sequence of single-layer passes, each with a specific evaluation
			criterion. Multi-layer reviews tend to catch the most obvious issues while missing the subtle
			ones. Layer isolation forces attention on the specific qualities of each channel without the
			others masking the problems.
		</p>

		<table>
			<thead>
				<tr>
					<th>Pass</th>
					<th>What to Listen / Watch</th>
					<th>What to Fix</th>
					<th>Module Reference</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td>Pass 1 — Narration only</td>
					<td>Listen with eyes closed; no visuals</td>
					<td>Pacing, pause architecture, WPM, clarity of argument</td>
					<td>M2, M7</td>
				</tr>
				<tr>
					<td>Pass 2 — Visual only</td>
					<td>Watch without audio; mute completely</td>
					<td>Hierarchy, composition, text legibility, motion overuse</td>
					<td>M3, M5, M6</td>
				</tr>
				<tr>
					<td>Pass 3 — Audio-visual sync</td>
					<td>Full audio, no pausing</td>
					<td>Motion sync windows, sound cue alignment, J-cut positioning</td>
					<td>M6, M7</td>
				</tr>
				<tr>
					<td>Pass 4 — Redundancy pass</td>
					<td>Fast-forward at 1.5×; stop when bored</td>
					<td>Any segment that loses you at 1.5× has too much padding</td>
					<td>M8</td>
				</tr>
				<tr>
					<td>Pass 5 — Consistency pass</td>
					<td>Compare three frames from different timestamps</td>
					<td>Colour system drift, component inconsistency, type misuse</td>
					<td>M9</td>
				</tr>
				<tr>
					<td>Pass 6 — Fresh eyes (24h later)</td>
					<td>Watch as if seeing for the first time</td>
					<td>Everything you can no longer see after spending too much time in the edit</td>
					<td>All</td>
				</tr>
			</tbody>
		</table>

		<div class="callout mint">
			<div class="callout-label">The 1.5× Pass</div>
			Watching your own video at 1.5× speed is the single most efficient quality control technique in
			this workflow. At normal speed, familiarity with the content creates tolerance for pacing problems
			you would not accept in another creator's work. At 1.5×, padding becomes intolerable immediately
			— you will feel yourself wanting to skip the exact moments that need cutting. Mark them, then watch
			those segments at normal speed to confirm the diagnosis.
		</div>
	</section>

	<!-- ═══ SELF-ASSESSMENT RUBRIC ═══ -->
	<section id="self-assessment" class="section">
		<div class="section-header">
			<span class="section-num">10.05</span>
			<h2 class="section-title">Self-Assessment Rubric</h2>
		</div>

		<p>
			The self-assessment rubric is a diagnostic tool for evaluating a completed video against the
			course's core principles. Each of the six dimensions is scored 1–3, producing a maximum score
			of 18. The rubric is not designed to produce a final grade — it is designed to identify the
			weakest dimension so you know where to focus improvement effort on the next video.
		</p>

		<!-- DEMO: Self-Assessment Rubric -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Six-Dimension Quality Rubric</span>
				<span class="demo-badge interactive">INTERACTIVE</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					Score your completed video on each dimension by selecting the level that best describes
					it. The total and the weakest dimension are identified at the bottom.
				</p>

				<div id="rubric-dimensions"></div>

				<div style="margin-top: 1.5rem">
					<div
						style="
									display: flex;
									justify-content: space-between;
									font-size: 11px;
									margin-bottom: 5px;
								"
					>
						<span style="color: var(--vs-muted)">Total score</span>
						<span id="rubric-total-val" style="font-weight: 600; color: var(--vs-amber)"
							>0 / 18</span
						>
					</div>
					<div class="rubric-total-bar">
						<div class="rubric-total-fill" id="rubric-total-fill" style="width: 0%"></div>
					</div>
				</div>
				<div
					id="rubric-verdict"
					style="
								margin-top: 0.75rem;
								padding: 0.75rem 1rem;
								border-left: 2px solid var(--vs-border2);
								font-size: 12px;
								color: var(--vs-text);
								line-height: 1.7;
								background: var(--vs-raised);
								min-height: 44px;
							"
				>
					Rate each dimension to generate your quality assessment.
				</div>
			</div>
		</div>
	</section>

	<!-- ═══ VIDEO QUALITY SIMULATOR ═══ -->
	<section id="simulator" class="section">
		<div class="section-header">
			<span class="section-num">10.06</span>
			<h2 class="section-title">Video Quality Simulator</h2>
		</div>

		<p>
			This simulator models the relationship between production decisions and the viewer's felt
			experience of a video. Adjust the six sliders — each corresponding to a course principle — and
			observe how the composite quality score and the simulated frame respond. The purpose is to
			make visceral what the course has argued analytically: all layers compound, and weakness in
			any one layer reduces the return on investment in all the others.
		</p>

		<!-- DEMO: Production Quality Simulator -->
		<div class="demo-box">
			<div class="demo-header">
				<span>Interactive · Production Quality Simulator</span>
				<span class="demo-badge animated">ANIMATED</span>
			</div>
			<div class="demo-body">
				<p style="font-size: 12px; color: var(--vs-muted); margin-bottom: 1.25rem">
					Adjust each quality dimension and see how the combined effect renders in a simulated video
					frame. All dimensions compound — a 10% weakness in narration pacing affects the perceived
					quality of every other layer.
				</p>

				<canvas
					id="vps-canvas"
					aria-label="Vps Canvas Demonstration"
					role="application"
					tabindex="0"
				></canvas>

				<div class="vps-controls" id="vps-controls"></div>

				<div class="vps-score-row" id="vps-scores"></div>
				<div
					id="vps-verdict"
					style="
								margin-top: 0.75rem;
								padding: 0.75rem 1rem;
								border-left: 2px solid var(--vs-border2);
								font-size: 12px;
								color: var(--vs-text);
								line-height: 1.7;
								background: var(--vs-raised);
								min-height: 40px;
							"
				></div>
			</div>
		</div>
	</section>

	<!-- ═══ FINAL PROJECT ═══ -->
	<section id="final-project" class="section">
		<div class="section-header">
			<span class="section-num">10.07</span>
			<h2 class="section-title">Final Project</h2>
		</div>

		<p>
			The final project is the integration of every module in this course into a single, complete,
			polished faceless video. The brief is deliberately open — the topic is yours to choose —
			because the constraints are craft-based, not content-based.
		</p>

		<div
			style="
						border: 1px solid var(--vs-amber);
						padding: 1.5rem 2rem;
						background: color-mix(in srgb, var(--vs-amber) 4%, var(--vs-surface));
						margin: 1.5rem 0;
					"
		>
			<div
				style="
							font-size: 10px;
							letter-spacing: 0.2em;
							text-transform: uppercase;
							color: var(--vs-amber);
							margin-bottom: 1rem;
							font-weight: 600;
						"
			>
				Final Project Brief
			</div>

			<div
				style="
							font-family: 'Syne', sans-serif;
							font-size: 18px;
							color: #fff;
							margin-bottom: 0.75rem;
							font-weight: 700;
						"
			>
				Produce a 1–2 minute faceless video on any topic you know well.
			</div>

			<div style="font-size: 12px; color: var(--vs-text); margin-bottom: 1.5rem; line-height: 1.8">
				The video must demonstrate conscious application of course principles, not merely include
				visual elements. Each production decision should be one you can explain with reference to
				the appropriate module.
			</div>

			<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem">
				<div>
					<div
						style="
									font-size: 10px;
									letter-spacing: 0.12em;
									text-transform: uppercase;
									color: var(--vs-mint);
									margin-bottom: 0.75rem;
									font-weight: 600;
								"
					>
						Required elements
					</div>
					<div style="font-size: 12px; color: var(--vs-text); line-height: 2">
						<div style="display: flex; gap: 0.5rem">
							<span style="color: var(--vs-mint)">✓</span> Structured narration rhythm with three pause
							types
						</div>
						<div style="display: flex; gap: 0.5rem">
							<span style="color: var(--vs-mint)">✓</span> Progressive diagram or visual sequence (not
							static)
						</div>
						<div style="display: flex; gap: 0.5rem">
							<span style="color: var(--vs-mint)">✓</span> Three text treatments (headline, support, annotation)
						</div>
						<div style="display: flex; gap: 0.5rem">
							<span style="color: var(--vs-mint)">✓</span> At least one J-cut section transition
						</div>
						<div style="display: flex; gap: 0.5rem">
							<span style="color: var(--vs-mint)">✓</span> Consistent visual language (colour + type system)
						</div>
						<div style="display: flex; gap: 0.5rem">
							<span style="color: var(--vs-mint)">✓</span> Momentum arc: build → peak at 65–75% → resolve
						</div>
					</div>
				</div>
				<div>
					<div
						style="
									font-size: 10px;
									letter-spacing: 0.12em;
									text-transform: uppercase;
									color: var(--vs-red);
									margin-bottom: 0.75rem;
									font-weight: 600;
								"
					>
						Excluded elements
					</div>
					<div style="font-size: 12px; color: var(--vs-text); line-height: 2">
						<div style="display: flex; gap: 0.5rem">
							<span style="color: var(--vs-red)">✕</span> On-camera presenter of any kind
						</div>
						<div style="display: flex; gap: 0.5rem">
							<span style="color: var(--vs-red)">✕</span> Decorative motion (motion without communicative
							function)
						</div>
						<div style="display: flex; gap: 0.5rem">
							<span style="color: var(--vs-red)">✕</span> Full sentences of narration reproduced as on-screen
							text
						</div>
						<div style="display: flex; gap: 0.5rem">
							<span style="color: var(--vs-red)">✕</span> Uniform cross-dissolve applied to all cuts
						</div>
						<div style="display: flex; gap: 0.5rem">
							<span style="color: var(--vs-red)">✕</span> Summary section restating the body content
						</div>
					</div>
				</div>
			</div>
		</div>

		<div class="callout">
			<div class="callout-label">Assessment Criterion</div>
			Submit the video alongside a brief production document (one page maximum) that identifies the three
			decisions in the video you are least satisfied with — the three places where the gap between what
			you intended and what you produced is largest. This document is the most important part of the submission:
			it demonstrates that you can see the difference between your current skill level and the standard
			you are working toward. That gap-recognition is the foundation of improvement.
		</div>
	</section>

	<!-- PRACTICAL -->
	<section id="practical" class="section">
		<div class="section-header">
			<span class="section-num">10.08</span>
			<h2 class="section-title">Course Summary</h2>
		</div>

		<p>
			This course has built a complete framework for faceless video production across ten modules.
			Each layer amplifies the others — the structure from Module 1 determines the effectiveness of
			the pacing from Module 2; the visual hierarchy from Module 5 determines the legibility of the
			text from Module 3. None of the layers is optional. A video that excels in five dimensions and
			fails in one will feel like a video that fails.
		</p>

		<div class="two-col">
			<div class="stats-panel">
				<div class="stat-row">
					<span class="stat-label">M01 — Cognitive load</span><span class="stat-val"
						>viewer attention model</span
					>
				</div>
				<div class="stat-row">
					<span class="stat-label">M02 — Cadence</span><span class="stat-val"
						>deliberate rhythm</span
					>
				</div>
				<div class="stat-row">
					<span class="stat-label">M03 — Text</span><span class="stat-val"
						>visual element, not transcript</span
					>
				</div>
				<div class="stat-row">
					<span class="stat-label">M04 — B-roll</span><span class="stat-val"
						>five visual functions</span
					>
				</div>
				<div class="stat-row">
					<span class="stat-label">M05 — Composition</span><span class="stat-val"
						>reading path + weight</span
					>
				</div>
			</div>
			<div class="stats-panel">
				<div class="stat-row">
					<span class="stat-label">M06 — Motion</span><span class="stat-val"
						>reveal / highlight / transform</span
					>
				</div>
				<div class="stat-row">
					<span class="stat-label">M07 — Audio</span><span class="stat-val"
						>four channels + pause arch.</span
					>
				</div>
				<div class="stat-row">
					<span class="stat-label">M08 — Editing</span><span class="stat-val"
						>momentum + compression</span
					>
				</div>
				<div class="stat-row">
					<span class="stat-label">M09 — Visual language</span><span class="stat-val"
						>colour + type + components</span
					>
				</div>
				<div class="stat-row">
					<span class="stat-label">M10 — Integration</span><span class="stat-val"
						>end-to-end production</span
					>
				</div>
			</div>
		</div>
	</section>

	<hr class="divider" />

	<!-- QUIZ — Final Module -->
	<section id="quiz" class="quiz-section">
		<div class="quiz-header">Module 10 — Final Assessment</div>
		<div class="quiz-sub">4 questions synthesising the full course · No time limit</div>

		<div class="question" id="q1">
			<div class="q-text">
				<span class="q-num">01.</span>A creator produces a video with excellent composition, a
				well-designed colour system, and precisely timed motion graphics. However, the narration
				pacing is too fast and the script contains significant verbal redundancy. How will the
				viewer most likely experience this video?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q1', e.currentTarget, false)}
				>
					The strong visual production will compensate for the narration issues — viewers primarily
					process visual information
				</button>
				<button
					type="button"
					class="option"
					data-correct="true"
					onclick={(e) => actions.answer('q1', e.currentTarget, true)}
				>
					The video will feel polished but dense and exhausting — narration carries the argument,
					and if that layer fails, the viewer cannot build the mental model the visuals are designed
					to enhance; the visual quality increases production value but cannot rescue comprehension
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q1', e.currentTarget, false)}
				>
					The viewer will notice the pacing issues but forgive them given the visual quality —
					production value creates tolerance for delivery flaws
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q1', e.currentTarget, false)}
				>
					The redundancy will actually help the viewer by reinforcing key concepts multiple times at
					the cost of some time efficiency
				</button>
			</div>
			<div class="feedback" id="fb-q1"></div>
		</div>

		<div class="question" id="q2">
			<div class="q-text">
				<span class="q-num">02.</span>In the polishing workflow, why is watching your own video at
				1.5× speed a more effective pacing diagnostic than watching it at normal speed?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q2', e.currentTarget, false)}
				>
					1.5× speed reduces total review time, allowing you to conduct more passes within the same
					timeframe
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q2', e.currentTarget, false)}
				>
					At 1.5× speed, audio quality issues become more audible because frequency responses change
					with playback rate
				</button>
				<button
					type="button"
					class="option"
					data-correct="true"
					onclick={(e) => actions.answer('q2', e.currentTarget, true)}
				>
					Familiarity with your own content creates tolerance for pacing problems at normal speed.
					At 1.5×, padding becomes immediately intolerable — you feel the urge to skip at the exact
					moments that need cutting, which you would not have noticed at normal speed due to the
					content's familiarity
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q2', e.currentTarget, false)}
				>
					1.5× speed matches the typical viewing speed of experienced viewers, providing a more
					accurate representation of the actual audience experience
				</button>
			</div>
			<div class="feedback" id="fb-q2"></div>
		</div>

		<div class="question" id="q3">
			<div class="q-text">
				<span class="q-num">03.</span>The final project brief excludes a "summary section restating
				the body content." What principle from Module 8 does this exclusion reflect?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q3', e.currentTarget, false)}
				>
					Summary sections use too many words and violate the minimum viable script principle from
					Module 3
				</button>
				<button
					type="button"
					class="option"
					data-correct="true"
					onclick={(e) => actions.answer('q3', e.currentTarget, true)}
				>
					The Last 20% rule: the resolution phase should be brief — once the peak insight has
					landed, the video is complete. A summary section extends the video past its natural
					endpoint by restating what the viewer already understood, flattening the momentum arc and
					reducing the impact of the peak
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q3', e.currentTarget, false)}
				>
					Summary sections introduce structural redundancy that makes the video difficult to
					compress in the temporal compression pass
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q3', e.currentTarget, false)}
				>
					Summary sections are only appropriate for videos longer than 5 minutes and are excluded
					for the 1–2 minute duration requirement
				</button>
			</div>
			<div class="feedback" id="fb-q3"></div>
		</div>

		<div class="question" id="q4">
			<div class="q-text">
				<span class="q-num">04.</span>The production document asks you to identify the three
				decisions you are least satisfied with. Why is this more valuable than identifying what you
				did well?
			</div>
			<div class="options">
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q4', e.currentTarget, false)}
				>
					Identifying weaknesses is easier than identifying strengths, so it provides more
					information in less time
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q4', e.currentTarget, false)}
				>
					Negative feedback is more actionable than positive feedback because it specifies changes
					that can be made
				</button>
				<button
					type="button"
					class="option"
					data-correct="true"
					onclick={(e) => actions.answer('q4', e.currentTarget, true)}
				>
					Gap-recognition — the ability to see the difference between your current output and the
					standard you are working toward — is the cognitive skill that drives improvement. A
					creator who can accurately identify their own weakest decisions is demonstrating the
					critical listening and watching capacity that makes every subsequent video better than the
					last
				</button>
				<button
					type="button"
					class="option"
					data-correct="false"
					onclick={(e) => actions.answer('q4', e.currentTarget, false)}
				>
					Cataloguing what worked well risks creating over-reliance on familiar techniques, while
					cataloguing failures encourages experimentation
				</button>
			</div>
			<div class="feedback" id="fb-q4"></div>
		</div>

		<div class="quiz-score" id="quiz-score">
			<div class="score-num" id="score-display">—</div>
			<div class="score-label">questions correct out of 4</div>
			<div
				id="course-complete-msg"
				style="display: none; margin-top: 1rem; font-size: 12px; color: var(--vs-mint)"
			>
				✓ Course complete — you have covered all ten modules.
			</div>
		</div>
	</section>

	<!-- COURSE COMPLETE -->
	<div class="course-complete">
		<div class="cc-title">Visual Storytelling for Faceless Video</div>
		<div class="cc-sub">10 modules · Narrative, Pacing &amp; Visual Communication · Complete</div>
		<div
			style="
						display: flex;
						flex-wrap: wrap;
						gap: 0.5rem;
						justify-content: center;
						margin-bottom: 2rem;
					"
		>
			<span
				style="
							padding: 4px 14px;
							border: 1px solid var(--vs-amber);
							color: var(--vs-amber);
							font-size: 11px;
							letter-spacing: 0.1em;
						">Story Structure</span
			>
			<span
				style="
							padding: 4px 14px;
							border: 1px solid var(--vs-blue);
							color: var(--vs-blue);
							font-size: 11px;
							letter-spacing: 0.1em;
						">Pacing &amp; Rhythm</span
			>
			<span
				style="
							padding: 4px 14px;
							border: 1px solid var(--vs-mint);
							color: var(--vs-mint);
							font-size: 11px;
							letter-spacing: 0.1em;
						">Text &amp; Visual Hierarchy</span
			>
			<span
				style="
							padding: 4px 14px;
							border: 1px solid var(--vs-red);
							color: var(--vs-red);
							font-size: 11px;
							letter-spacing: 0.1em;
						">B-Roll &amp; Diagrams</span
			>
			<span
				style="
							padding: 4px 14px;
							border: 1px solid var(--vs-blue);
							color: var(--vs-blue);
							font-size: 11px;
							letter-spacing: 0.1em;
						">Composition</span
			>
			<span
				style="
							padding: 4px 14px;
							border: 1px solid var(--vs-amber);
							color: var(--vs-amber);
							font-size: 11px;
							letter-spacing: 0.1em;
						">Motion Graphics</span
			>
			<span
				style="
							padding: 4px 14px;
							border: 1px solid var(--vs-mint);
							color: var(--vs-mint);
							font-size: 11px;
							letter-spacing: 0.1em;
						">Audio Design</span
			>
			<span
				style="
							padding: 4px 14px;
							border: 1px solid var(--vs-red);
							color: var(--vs-red);
							font-size: 11px;
							letter-spacing: 0.1em;
						">Editing</span
			>
			<span
				style="
							padding: 4px 14px;
							border: 1px solid var(--vs-blue);
							color: var(--vs-blue);
							font-size: 11px;
							letter-spacing: 0.1em;
						">Visual Language</span
			>
			<span
				style="
							padding: 4px 14px;
							border: 1px solid var(--vs-amber);
							color: var(--vs-amber);
							font-size: 11px;
							letter-spacing: 0.1em;
						">Production</span
			>
		</div>
		<div
			style="
						font-size: 13px;
						color: var(--vs-muted);
						max-width: 520px;
						margin: 0 auto;
						line-height: 1.8;
					"
		>
			The principles in this course are not rules to memorise — they are tools to internalise. A
			creator who has absorbed these layers stops asking "what should I do here?" and starts asking
			"what does this content need?" That shift is the transition from learning craft to practising
			it.
		</div>
	</div>

	<div class="nav-links">
		<a href="./09" class="prev-link">← Module 09: Building a Repeatable Visual Language</a>
	</div>
</div>

<style>
	.page-wrapper {
		background: var(--vs-bg);
		color: var(--vs-text);
		font-family: 'IBM Plex Mono', monospace;
		font-size: 14px;
		line-height: 1.8;
	}

	.page-wrapper {
		max-width: 960px;
		margin: 0 auto;
		padding: 0 2rem 6rem;
	}
	:global(.two-col) {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1.5rem;
	}
	:global(.three-col) {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr;
		gap: 1rem;
	}
	@media (max-width: 640px) {
		:global(.two-col),
		:global(.three-col) {
			grid-template-columns: 1fr;
		}
	}

	.course-header {
		border-bottom: 1px solid var(--vs-border);
		padding: 2rem 0 1.5rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.course-label {
		font-size: 11px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--vs-muted);
	}
	.course-title {
		font-family: 'Syne', sans-serif;
		font-size: 13px;
		color: var(--vs-muted);
		font-weight: 400;
	}

	.module-hero {
		padding: 5rem 0 3.5rem;
		border-bottom: 1px solid var(--vs-border);
		position: relative;
		overflow: hidden;
	}
	.module-hero::before {
		content: '';
		position: absolute;
		inset: 0;
		pointer-events: none;
		background: repeating-linear-gradient(
			0deg,
			transparent,
			transparent 2px,
			rgba(245, 185, 74, 0.016) 2px,
			rgba(245, 185, 74, 0.016) 4px
		);
	}
	/* Gold glow for capstone */
	.module-hero::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		height: 1px;
		background: linear-gradient(90deg, transparent, var(--vs-amber), transparent);
		opacity: 0.5;
	}
	.module-number {
		font-family: 'Syne', sans-serif;
		font-size: clamp(80px, 15vw, 140px);
		font-weight: 800;
		line-height: 1;
		color: transparent;
		-webkit-text-stroke: 1px var(--vs-border2);
		position: absolute;
		right: -10px;
		top: 50%;
		transform: translateY(-50%);
		pointer-events: none;
		user-select: none;
	}
	.module-tag {
		display: inline-block;
		font-size: 10px;
		letter-spacing: 0.25em;
		text-transform: uppercase;
		color: var(--vs-amber);
		border: 1px solid var(--vs-amber);
		padding: 3px 10px;
		margin-bottom: 1.5rem;
	}
	.module-title {
		font-family: 'Syne', sans-serif;
		font-size: clamp(28px, 5vw, 48px);
		font-weight: 800;
		line-height: 1.1;
		color: #fff;
		max-width: 600px;
	}
	.module-title span {
		color: var(--vs-amber);
	}

	/* Capstone badge */
	:global(.capstone-badge) {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 4px 14px;
		border: 1px solid var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 8%, transparent);
		color: var(--vs-amber);
		font-size: 11px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		margin-bottom: 1.5rem;
	}

	.toc {
		margin: 3rem 0;
		padding: 1.5rem;
		border: 1px solid var(--vs-border);
		background: var(--vs-surface);
	}
	.toc-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--vs-muted);
		margin-bottom: 1rem;
	}
	.toc-list {
		list-style: none;
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}
	.toc-list a {
		font-size: 12px;
		color: var(--vs-muted);
		text-decoration: none;
		border: 1px solid var(--vs-border);
		padding: 4px 10px;
		transition: all 0.15s;
	}
	.toc-list a:hover {
		color: var(--vs-amber);
		border-color: var(--vs-amber);
	}

	.objectives {
		margin: 2.5rem 0;
		padding: 1.5rem 2rem;
		border-left: 2px solid var(--vs-amber);
		background: var(--vs-surface);
	}
	.objectives-label {
		font-size: 10px;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--vs-amber);
		margin-bottom: 1rem;
	}
	.objectives ul {
		list-style: none;
	}
	.objectives li {
		padding: 0.2rem 0;
		padding-left: 1.2rem;
		position: relative;
	}
	.objectives li::before {
		content: '→';
		position: absolute;
		left: 0;
		color: var(--vs-blue);
	}

	.section {
		margin: 4rem 0;
	}
	.section-header {
		display: flex;
		align-items: baseline;
		gap: 1rem;
		margin-bottom: 2rem;
		padding-bottom: 0.75rem;
		border-bottom: 1px solid var(--vs-border);
	}
	.section-num {
		font-size: 11px;
		color: var(--vs-blue);
		letter-spacing: 0.1em;
		font-weight: 600;
	}
	.section-title {
		font-family: 'Syne', sans-serif;
		font-size: 22px;
		font-weight: 700;
		color: #fff;
	}

	p {
		margin-bottom: 1.2rem;
		color: var(--vs-text);
	}
	p:last-child {
		margin-bottom: 0;
	}
	strong {
		color: var(--vs-amber);
		font-weight: 600;
	}
	em {
		color: #fff;
		font-style: normal;
		font-weight: 500;
	}
	a {
		color: inherit;
		text-decoration: none;
	}
	:global(code) {
		background: #040710;
		border: 1px solid var(--vs-border);
		padding: 1px 6px;
		font-size: 12px;
		color: var(--vs-mint);
		font-family: 'IBM Plex Mono', monospace;
	}

	.callout {
		margin: 1.5rem 0;
		padding: 1rem 1.5rem;
		border-left: 2px solid var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 5%, var(--vs-surface));
		font-size: 13px;
	}
	:global(.callout.blue) {
		border-color: var(--vs-blue);
		background: color-mix(in srgb, var(--vs-blue) 5%, var(--vs-surface));
	}
	:global(.callout.red) {
		border-color: var(--vs-red);
		background: color-mix(in srgb, var(--vs-red) 5%, var(--vs-surface));
	}
	:global(.callout.mint) {
		border-color: var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 5%, var(--vs-surface));
	}
	.callout-label {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--vs-amber);
		margin-bottom: 0.4rem;
		font-weight: 600;
	}
	:global(.callout.blue) .callout-label {
		color: var(--vs-blue);
	}
	:global(.callout.red) .callout-label {
		color: var(--vs-red);
	}
	:global(.callout.mint) .callout-label {
		color: var(--vs-mint);
	}

	.demo-box {
		background: var(--vs-surface);
		border: 1px solid var(--vs-border);
		margin: 2rem 0;
	}
	.demo-header {
		padding: 0.75rem 1.25rem;
		border-bottom: 1px solid var(--vs-border);
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.demo-header > span {
		font-size: 11px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--vs-muted);
	}
	:global(.demo-badge) {
		font-size: 10px;
		padding: 2px 8px;
		border: 1px solid;
	}
	:global(.demo-badge.interactive) {
		color: var(--vs-amber);
		border-color: var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 10%, transparent);
	}
	:global(.demo-badge.animated) {
		color: var(--vs-blue);
		border-color: var(--vs-blue);
		background: color-mix(in srgb, var(--vs-blue) 10%, transparent);
	}
	.demo-body {
		padding: 1.5rem;
	}

	:global(.btn) {
		background: transparent;
		border: 1px solid var(--vs-border2);
		color: var(--vs-text);
		padding: 6px 16px;
		font-family: 'IBM Plex Mono', monospace;
		font-size: 12px;
		cursor: pointer;
		transition: all 0.15s;
	}
	:global(.btn:hover) {
		border-color: var(--vs-amber);
		color: var(--vs-amber);
	}
	:global(.btn.active) {
		border-color: var(--vs-amber);
		color: var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 10%, transparent);
	}
	:global(.btn.blue:hover) {
		border-color: var(--vs-blue);
		color: var(--vs-blue);
	}
	:global(.btn.blue.active) {
		border-color: var(--vs-blue);
		color: var(--vs-blue);
		background: color-mix(in srgb, var(--vs-blue) 10%, transparent);
	}
	:global(.btn.mint:hover) {
		border-color: var(--vs-mint);
		color: var(--vs-mint);
	}
	:global(.btn.mint.active) {
		border-color: var(--vs-mint);
		color: var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 10%, transparent);
	}
	:global(.btn.red:hover) {
		border-color: var(--vs-red);
		color: var(--vs-red);
	}
	:global(.btn.red.active) {
		border-color: var(--vs-red);
		color: var(--vs-red);
		background: color-mix(in srgb, var(--vs-red) 10%, transparent);
	}
	:global(.btn-row) {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 1.25rem;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		margin: 1.5rem 0;
		font-size: 12px;
	}
	th {
		background: var(--vs-raised);
		color: var(--vs-amber);
		text-align: left;
		padding: 0.6rem 1rem;
		border: 1px solid var(--vs-border);
		font-weight: 600;
		letter-spacing: 0.05em;
	}
	td {
		padding: 0.5rem 1rem;
		border: 1px solid var(--vs-border);
		color: var(--vs-text);
	}
	tr:nth-child(even) td {
		background: color-mix(in srgb, var(--vs-raised) 50%, transparent);
	}

	.divider {
		border: none;
		border-top: 1px solid var(--vs-border);
		margin: 3rem 0;
	}
	.stats-panel {
		background: #040710;
		border: 1px solid var(--vs-border);
		padding: 1rem;
		font-size: 12px;
	}
	.stat-row {
		display: flex;
		justify-content: space-between;
		padding: 0.2rem 0;
		border-bottom: 1px solid var(--vs-border);
	}
	.stat-row:last-child {
		border-bottom: none;
	}
	.stat-label {
		color: var(--vs-muted);
	}
	.stat-val {
		color: var(--vs-amber);
		font-weight: 600;
	}

	.progress-bar-wrap {
		height: 3px;
		background: var(--vs-border);
		width: 100%;
		margin: 2rem 0 0;
	}
	.progress-bar-fill {
		height: 100%;
		background: var(--vs-amber);
		width: 0;
		transition: width 0.4s ease;
	}

	.quiz-section {
		margin: 4rem 0;
		padding: 2rem;
		border: 1px solid var(--vs-border);
		background: var(--vs-surface);
	}
	.quiz-header {
		font-family: 'Syne', sans-serif;
		font-size: 18px;
		font-weight: 700;
		color: #fff;
		margin-bottom: 0.5rem;
	}
	.quiz-sub {
		font-size: 12px;
		color: var(--vs-muted);
		margin-bottom: 2rem;
	}
	:global(.question) {
		margin: 2rem 0;
	}
	:global(.q-text) {
		font-size: 13px;
		color: #fff;
		margin-bottom: 1rem;
	}
	:global(.q-num) {
		color: var(--vs-blue);
		margin-right: 0.5rem;
	}
	:global(.options) {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}
	:global(.option) {
		padding: 0.6rem 1rem;
		border: 1px solid var(--vs-border);
		cursor: pointer;
		font-size: 12px;
		transition: all 0.15s;
		user-select: none;
		font-family: 'IBM Plex Mono', monospace;
	}
	:global(.option:hover) {
		border-color: var(--vs-border2);
		background: var(--vs-raised);
	}
	:global(.option.correct) {
		border-color: var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 10%, transparent);
		color: var(--vs-mint);
	}
	:global(.option.wrong) {
		border-color: var(--vs-red);
		background: color-mix(in srgb, var(--vs-red) 10%, transparent);
		color: var(--vs-red);
	}
	:global(.option.disabled) {
		pointer-events: none;
	}
	:global(.feedback) {
		font-size: 12px;
		margin-top: 0.75rem;
		min-height: 1.5em;
		color: var(--vs-muted);
	}
	:global(.feedback.ok) {
		color: var(--vs-mint);
	}
	:global(.feedback.bad) {
		color: var(--vs-red);
	}
	.quiz-score {
		margin-top: 2rem;
		padding: 1.5rem;
		border: 1px solid var(--vs-amber);
		text-align: center;
		display: none;
		background: color-mix(in srgb, var(--vs-amber) 5%, var(--vs-surface));
	}
	.score-num {
		font-family: 'Syne', sans-serif;
		font-size: 36px;
		font-weight: 800;
		color: var(--vs-amber);
	}
	.score-label {
		font-size: 12px;
		color: var(--vs-muted);
		margin-top: 0.25rem;
	}

	/* Course complete card */
	:global(.course-complete) {
		margin-top: 4rem;
		padding: 3rem 2rem;
		border: 1px solid var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 4%, var(--vs-surface));
		text-align: center;
		position: relative;
		overflow: hidden;
	}
	.course-complete::before {
		content: '';
		position: absolute;
		inset: 0;
		background: repeating-linear-gradient(
			45deg,
			transparent,
			transparent 10px,
			rgba(245, 185, 74, 0.02) 10px,
			rgba(245, 185, 74, 0.02) 20px
		);
		pointer-events: none;
	}
	:global(.cc-title) {
		font-family: 'Syne', sans-serif;
		font-size: clamp(22px, 4vw, 36px);
		font-weight: 800;
		color: #fff;
		margin-bottom: 0.5rem;
	}
	:global(.cc-sub) {
		font-size: 12px;
		color: var(--vs-muted);
		margin-bottom: 2rem;
	}

	.nav-links {
		display: flex;
		justify-content: flex-start;
		align-items: stretch;
		margin-top: 4rem;
		flex-wrap: wrap;
		gap: 1rem;
	}
	:global(.prev-link) {
		font-size: 12px;
		color: var(--vs-muted);
		text-decoration: none;
		border: 1px solid var(--vs-border);
		padding: 0.75rem 1.25rem;
		transition: all 0.2s;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
	}
	:global(.prev-link:hover) {
		border-color: var(--vs-blue);
		color: var(--vs-blue);
	}

	/* ══════════════════════════════
     MODULE-SPECIFIC COMPONENTS
  ══════════════════════════════ */

	/* ── PRODUCTION WORKFLOW PIPELINE ── */
	:global(.pipeline-stage) {
		border: 1px solid var(--vs-border);
		background: var(--vs-raised);
		cursor: pointer;
		transition: all 0.2s;
		position: relative;
		overflow: hidden;
	}
	.pipeline-stage::before {
		content: '';
		position: absolute;
		left: 0;
		top: 0;
		bottom: 0;
		width: 3px;
		background: var(--vs-border2);
		transition: background 0.2s;
	}
	.pipeline-stage.active::before {
		background: var(--vs-amber);
	}
	.pipeline-stage.done::before {
		background: var(--vs-mint);
	}
	:global(.pipeline-stage:hover) {
		border-color: var(--vs-border2);
	}
	:global(.pipeline-stage.active) {
		border-color: var(--vs-amber);
		background: color-mix(in srgb, var(--vs-amber) 5%, var(--vs-raised));
	}
	:global(.pipeline-stage.done) {
		border-color: var(--vs-mint);
		background: color-mix(in srgb, var(--vs-mint) 4%, var(--vs-raised));
	}
	:global(.ps-header) {
		padding: 0.75rem 1rem 0.75rem 1.25rem;
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}
	:global(.ps-num) {
		font-family: 'Syne', sans-serif;
		font-size: 22px;
		font-weight: 700;
		min-width: 28px;
		color: var(--vs-muted);
		transition: color 0.2s;
	}
	:global(.pipeline-stage.active) :global(.ps-num) {
		color: var(--vs-amber);
	}
	:global(.pipeline-stage.done) :global(.ps-num) {
		color: var(--vs-mint);
	}
	:global(.ps-title) {
		font-size: 12px;
		font-weight: 600;
		color: var(--vs-text);
		transition: color 0.2s;
		flex: 1;
	}
	:global(.pipeline-stage.active) :global(.ps-title) {
		color: #fff;
	}
	:global(.ps-badge) {
		font-size: 9px;
		padding: 2px 8px;
		border: 1px solid;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		flex-shrink: 0;
	}
	:global(.ps-body) {
		display: none;
		padding: 0 1.25rem 1rem 2.5rem;
	}
	:global(.pipeline-stage.active) :global(.ps-body) {
		display: block;
	}
	:global(.ps-tasks) {
		list-style: none;
		margin-top: 0.5rem;
	}
	:global(.ps-task) {
		padding: 0.25rem 0;
		font-size: 12px;
		display: flex;
		align-items: flex-start;
		gap: 0.6rem;
		border-bottom: 1px solid var(--vs-border);
	}
	:global(.ps-task:last-child) {
		border-bottom: none;
	}
	:global(.ps-task-check) {
		width: 16px;
		height: 16px;
		border: 1px solid var(--vs-border2);
		cursor: pointer;
		flex-shrink: 0;
		margin-top: 3px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 10px;
		transition: all 0.15s;
	}
	:global(.ps-task-check.checked) {
		background: color-mix(in srgb, var(--vs-mint) 15%, transparent);
		border-color: var(--vs-mint);
		color: var(--vs-mint);
	}
	:global(.ps-task-text) {
		flex: 1;
		color: var(--vs-text);
		line-height: 1.6;
	}
	:global(.ps-task-text.done) {
		color: var(--vs-muted);
		text-decoration: line-through;
	}
	:global(.ps-module-ref) {
		font-size: 10px;
		color: var(--vs-muted);
		padding: 3px 7px;
		border: 1px solid var(--vs-border);
		white-space: nowrap;
		flex-shrink: 0;
	}

	/* ── PRE-PRODUCTION CHECKLIST ── */
	:global(.checklist-group) {
		margin-bottom: 1.5rem;
	}
	:global(.checklist-group-label) {
		font-size: 10px;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--vs-amber);
		margin-bottom: 0.5rem;
		font-weight: 600;
		padding-bottom: 0.3rem;
		border-bottom: 1px solid var(--vs-border);
	}
	:global(.checklist-item) {
		display: flex;
		align-items: flex-start;
		gap: 0.75rem;
		padding: 0.4rem 0;
		border-bottom: 1px solid var(--vs-border);
	}
	:global(.checklist-item:last-child) {
		border-bottom: none;
	}
	:global(.check-box) {
		width: 18px;
		height: 18px;
		border: 1px solid var(--vs-border2);
		cursor: pointer;
		flex-shrink: 0;
		margin-top: 2px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 11px;
		transition: all 0.15s;
	}
	.check-box.checked {
		background: color-mix(in srgb, var(--vs-mint) 15%, transparent);
		border-color: var(--vs-mint);
		color: var(--vs-mint);
	}
	.check-box.warn {
		background: color-mix(in srgb, var(--vs-red) 15%, transparent);
		border-color: var(--vs-red);
		color: var(--vs-red);
	}
	.check-label {
		flex: 1;
		font-size: 12px;
		color: var(--vs-text);
		line-height: 1.6;
	}
	.check-label.done {
		color: var(--vs-muted);
	}
	.check-priority {
		font-size: 9px;
		padding: 2px 6px;
		border: 1px solid;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		flex-shrink: 0;
		margin-top: 2px;
	}

	/* ── SELF-ASSESSMENT RUBRIC ── */
	.rubric-dimension {
		border: 1px solid var(--vs-border);
		margin-bottom: 0.75rem;
		background: var(--vs-raised);
	}
	.rubric-dim-header {
		padding: 0.65rem 1rem;
		display: flex;
		align-items: center;
		gap: 1rem;
		border-bottom: 1px solid var(--vs-border);
		cursor: pointer;
	}
	.rubric-dim-name {
		font-size: 12px;
		font-weight: 600;
		color: #fff;
		flex: 1;
	}
	.rubric-dim-module {
		font-size: 9px;
		color: var(--vs-muted);
		padding: 2px 6px;
		border: 1px solid var(--vs-border);
	}
	.rubric-levels {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr;
		gap: 1px;
		background: var(--vs-border);
	}
	@media (max-width: 560px) {
		.rubric-levels {
			grid-template-columns: 1fr;
		}
	}
	.rubric-level {
		padding: 0.65rem 0.75rem;
		cursor: pointer;
		transition: all 0.15s;
		background: var(--vs-raised);
	}
	.rubric-level:hover {
		background: color-mix(in srgb, var(--vs-amber) 5%, var(--vs-raised));
	}
	.rubric-level.selected-1 {
		background: color-mix(in srgb, var(--vs-red) 10%, var(--vs-raised));
		border-top: 2px solid var(--vs-red);
	}
	.rubric-level.selected-2 {
		background: color-mix(in srgb, var(--vs-amber) 10%, var(--vs-raised));
		border-top: 2px solid var(--vs-amber);
	}
	.rubric-level.selected-3 {
		background: color-mix(in srgb, var(--vs-mint) 10%, var(--vs-raised));
		border-top: 2px solid var(--vs-mint);
	}
	.rl-score {
		font-family: 'Syne', sans-serif;
		font-size: 20px;
		font-weight: 700;
		margin-bottom: 2px;
	}
	.rl-label {
		font-size: 9px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--vs-muted);
		margin-bottom: 4px;
	}
	.rl-desc {
		font-size: 10px;
		color: var(--vs-text);
		line-height: 1.6;
	}
	.rubric-total-bar {
		height: 8px;
		background: var(--vs-border);
		margin-top: 1.5rem;
		border-radius: 4px;
		overflow: hidden;
	}
	.rubric-total-fill {
		height: 100%;
		border-radius: 4px;
		transition:
			width 0.5s ease,
			background 0.3s;
	}

	/* ── VIDEO PRODUCTION SIMULATOR ── */
	.vps-canvas-wrap {
		position: relative;
	}
	#vps-canvas {
		display: block;
		width: 100%;
		aspect-ratio: 16/9;
		border: 1px solid var(--vs-border);
		background: #040710;
	}
	.vps-controls {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.75rem;
		margin-top: 1rem;
	}
	@media (max-width: 560px) {
		.vps-controls {
			grid-template-columns: 1fr;
		}
	}
	.vps-control {
		border: 1px solid var(--vs-border);
		padding: 0.75rem;
		background: var(--vs-raised);
	}
	.vps-control-label {
		font-size: 9px;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--vs-muted);
		margin-bottom: 0.5rem;
	}
	.vps-slider-row {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin: 0.35rem 0;
	}
	.vps-slider-label {
		font-size: 10px;
		color: var(--vs-text);
		min-width: 90px;
	}
	.vps-slider {
		flex: 1;
		-webkit-appearance: none;
		height: 3px;
		background: var(--vs-border2);
		outline: none;
	}
	.vps-slider::-webkit-slider-thumb {
		-webkit-appearance: none;
		width: 10px;
		height: 10px;
		border-radius: 50%;
		background: var(--vs-amber);
		cursor: pointer;
	}
	.vps-val {
		font-size: 10px;
		color: var(--vs-amber);
		min-width: 28px;
		text-align: right;
		font-weight: 600;
	}
	.vps-score-row {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 1px;
		background: var(--vs-border);
		margin-top: 0.75rem;
	}
	.vps-score-cell {
		background: var(--vs-raised);
		padding: 0.5rem 0.4rem;
		text-align: center;
	}
	.vps-score-val {
		font-family: 'Syne', sans-serif;
		font-size: 17px;
		font-weight: 700;
		line-height: 1;
	}
	.vps-score-lbl {
		font-size: 8px;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--vs-muted);
		margin-top: 3px;
	}

	/* ── MODULE MAP ── */
	.module-map {
		display: grid;
		grid-template-columns: repeat(5, 1fr);
		gap: 1px;
		background: var(--vs-border);
		margin: 1.5rem 0;
	}
	@media (max-width: 560px) {
		.module-map {
			grid-template-columns: repeat(2, 1fr);
		}
	}
	.mm-cell {
		background: var(--vs-raised);
		padding: 0.75rem 0.5rem;
		text-align: center;
		cursor: pointer;
		transition: all 0.15s;
		position: relative;
		overflow: hidden;
	}
	.mm-cell::before {
		content: '';
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		height: 2px;
		background: var(--vs-border2);
	}
	.mm-cell:hover {
		background: color-mix(in srgb, var(--vs-amber) 6%, var(--vs-raised));
	}
	.mm-cell.selected {
		background: color-mix(in srgb, var(--vs-amber) 10%, var(--vs-raised));
	}
	.mm-cell.selected::before {
		background: var(--vs-amber);
	}
	.mm-num {
		font-family: 'Syne', sans-serif;
		font-size: 22px;
		font-weight: 700;
		color: var(--vs-border2);
		transition: color 0.2s;
	}
	.mm-cell.selected .mm-num {
		color: var(--vs-amber);
	}
	.mm-title {
		font-size: 9px;
		letter-spacing: 0.06em;
		color: var(--vs-muted);
		margin-top: 3px;
		line-height: 1.4;
	}
	.mm-detail {
		margin-top: 0;
		padding: 1rem;
		border: 1px solid var(--vs-border);
		border-top: none;
		background: color-mix(in srgb, var(--vs-amber) 4%, var(--vs-surface));
		font-size: 12px;
		color: var(--vs-text);
		line-height: 1.7;
		display: none;
	}
	.mm-detail.open {
		display: block;
	}
	.mm-detail strong {
		color: var(--vs-amber);
	}

	.btn:focus,
	.btn:focus-visible {
		outline: 3px solid currentColor;
		outline-offset: 3px;
	}
</style>
