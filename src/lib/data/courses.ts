export interface Module {
	id: string; // e.g. "01"
	number: number;
	title: string;
	subtitle: string;
	status: 'available' | 'coming-soon';
	accentVar: string; // CSS variable name for accent
	description: string;
}

export interface Course {
	id: string;
	title: string;
	subtitle: string;
	description: string;
	totalModules: number;
}

export const gameDevCourse: Course = {
	id: 'game-dev',
	title: 'Game Development Fundamentals',
	subtitle: 'From Pixels to Play',
	description:
		'This course introduces the foundations of game development by starting from the basics of computer graphics and progressing toward interactive 2D games. Students learn how images are represented, how transformations work, how rendering pipelines function, and how shaders operate.',
	totalModules: 12
};

export const gameDevModules: Module[] = [
	{
		id: '01',
		number: 1,
		title: 'Pixels and the Structure of Images',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--accent',
		description:
			'Understand color models, pixel grids, image channels, and the fundamental nature of raster images.'
	},
	{
		id: '02',
		number: 2,
		title: 'The Rendering Process',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--accent2',
		description:
			'Trace the journey from geometric data to pixels: triangles, rasterization, and why GPUs exist.'
	},
	{
		id: '03',
		number: 3,
		title: 'Coordinate Systems and Transformations',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--accent3',
		description:
			'Master 2D and 3D coordinate spaces, matrix transformations, and the transformation pipeline.'
	},
	{
		id: '04',
		number: 4,
		title: 'Shaders and the GPU Pipeline',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--accent',
		description:
			'Write vertex and fragment shaders. Understand how GPU programs compute color for every pixel.'
	},
	{
		id: '05',
		number: 5,
		title: 'Textures and Sampling',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--accent2',
		description:
			'Load images onto GPU memory, sample them in shaders, and control filtering and wrapping modes.'
	},
	{
		id: '06',
		number: 6,
		title: 'Lighting and Shading Models',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--accent3',
		description:
			'Implement ambient, diffuse, and specular lighting. Understand normal vectors and Phong shading.'
	},
	{
		id: '07',
		number: 7,
		title: 'Sprite Animation and Tilemaps',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--accent',
		description:
			'Build sprite sheets, animate frame sequences, and render tile-based worlds efficiently.'
	},
	{
		id: '08',
		number: 8,
		title: 'Input and Game Loop',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--accent2',
		description:
			'Implement a fixed-timestep game loop, handle keyboard and mouse input, and manage game state.'
	},
	{
		id: '09',
		number: 9,
		title: '2D Physics Fundamentals',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--accent3',
		description:
			'Integrate velocity and acceleration, detect collisions between shapes, and resolve them correctly.'
	},
	{
		id: '10',
		number: 10,
		title: 'Cameras and Viewports',
		subtitle: 'Theory + Practice',
		status: 'coming-soon',
		accentVar: '--accent',
		description:
			'Build a scrolling camera, implement parallax layers, and convert between world and screen space.'
	},
	{
		id: '11',
		number: 11,
		title: 'Audio and Game Feel',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--accent2',
		description:
			'Add sound effects and music, implement screen shake and juice, and polish the player experience.'
	},
	{
		id: '12',
		number: 12,
		title: 'Building a Complete 2D Game',
		subtitle: 'Capstone Project',
		status: 'available',
		accentVar: '--accent3',
		description: 'Combine all modules into a complete, playable 2D game from design to final build.'
	}
];

export function getModule(id: string): Module | undefined {
	return gameDevModules.find((m) => m.id === id);
}

export function getAdjacentModules(id: string): { prev: Module | null; next: Module | null } {
	const idx = gameDevModules.findIndex((m) => m.id === id);
	return {
		prev: idx > 0 ? gameDevModules[idx - 1] : null,
		next: idx < gameDevModules.length - 1 ? gameDevModules[idx + 1] : null
	};
}

export const animationCourse: Course = {
	id: 'animation',
	title: 'Animation Fundamentals',
	subtitle: 'Motion, Characters & Visual Storytelling',
	description:
		'Learn animation from the ground up — from timing and spacing through character rigging to full explainer video production.',
	totalModules: 10
};

export const animationModules: Module[] = [
	{
		id: '01',
		number: 1,
		title: 'What Animation Is',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--anim-gold',
		description:
			'How motion emerges from still images — persistence of vision, FPS, timing vs spacing, and animation workflows.'
	},
	{
		id: '02',
		number: 2,
		title: 'Timing, Spacing & Weight',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--anim-coral',
		description:
			'Produce convincing motion using slow-in/slow-out curves, arcs, and spacing charts to convey weight and gravity.'
	},
	{
		id: '03',
		number: 3,
		title: 'The 12 Principles',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--anim-mint',
		description:
			'Understand and apply the classical principles: squash & stretch, anticipation, follow-through, arcs, and more.'
	},
	{
		id: '04',
		number: 4,
		title: 'Drawing for Animation',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--anim-gold',
		description:
			'Breaking characters into simple forms, line-of-action, silhouette clarity, and designing diagram elements for motion.'
	},
	{
		id: '05',
		number: 5,
		title: 'Digital 2D Tools',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--anim-coral',
		description:
			'Layers, keyframes, tweens, onion skinning, and the timeline — a hands-on introduction to 2D animation software.'
	},
	{
		id: '06',
		number: 6,
		title: 'Rigging for 2D Characters',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--anim-mint',
		description:
			'Build a basic 2D rig with bones, hierarchies, constraints, and controllers. Animate a walk cycle.'
	},
	{
		id: '07',
		number: 7,
		title: 'Lip Sync & Expression',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--anim-gold',
		description:
			'Phoneme shapes, matching sound to frames, expressive timing, and body language for emotional clarity.'
	},
	{
		id: '08',
		number: 8,
		title: 'Diagram & Concept Animation',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--anim-coral',
		description:
			'Animate arrows, labels, highlights, and flows to explain ideas. Reveal, transform, and focus with motion.'
	},
	{
		id: '09',
		number: 9,
		title: 'Layout, Staging & Scenes',
		subtitle: 'Theory + Practice',
		status: 'coming-soon',
		accentVar: '--anim-mint',
		description:
			'Composition, framing, rule of thirds, multi-shot sequences, and scene continuity for educational content.'
	},
	{
		id: '10',
		number: 10,
		title: 'Complete Animated Sequence',
		subtitle: 'Capstone',
		status: 'coming-soon',
		accentVar: '--anim-gold',
		description:
			'Produce a 15–30 second explainer combining character, diagrams, narration, and final polish for publishing.'
	}
];

export const graphicDesignCourse: Course = {
	id: 'graphic-design',
	title: 'Graphic Design & Visual Storytelling',
	subtitle: 'Building a Personal Creative Identity',
	description:
		'This course teaches the foundational skills of graphic design for people who want to build their own visual identity but do not yet feel artistic. Students explore the underlying principles of design, color, composition, typography, branding, and visual storytelling.',
	totalModules: 10
};

export const graphicDesignModules: Module[] = [
	{
		id: '01',
		number: 1,
		title: "What Design Is (and Isn't)",
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--gd-rose',
		description:
			'Design as intentional problem-solving, not decoration. The invisible structure behind good design, and why your taste already gives you an advantage.'
	},
	{
		id: '02',
		number: 2,
		title: 'Visual Perception & Composition',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--gd-violet',
		description:
			'How the eye moves across an image. Visual hierarchy, rule of thirds, balance, contrast, alignment, spacing, and grouping.'
	},
	{
		id: '03',
		number: 3,
		title: 'Typography Essentials',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--gd-sky',
		description:
			'Use type to communicate tone and personality. Serif, sans-serif, pairing fonts, kerning, leading, and type for thumbnails and websites.'
	},
	{
		id: '04',
		number: 4,
		title: 'Color Theory & Emotional Impact',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--gd-amber',
		description:
			'Build color palettes that communicate ideas. Hues, saturation, complementary palettes, warm vs cool behavior, and accessibility.'
	},
	{
		id: '05',
		number: 5,
		title: 'Shape Language & Iconography',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--gd-sage',
		description:
			'Use shapes to express personality. Sharp vs rounded forms, geometric vs organic, symbol design rules, and how shape language builds identity.'
	},
	{
		id: '06',
		number: 6,
		title: 'Brand Identity & Visual Systems',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--gd-rose',
		description:
			'Build a functional identity system: logo, colors, fonts, patterns. Designing a logo from concept and establishing a style guide.'
	},
	{
		id: '07',
		number: 7,
		title: 'Layout for Digital Platforms',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--gd-violet',
		description:
			'Design for YouTube and websites. Thumbnails, banners, spacing systems, grids, and visual rhythm across screen sizes.'
	},
	{
		id: '08',
		number: 8,
		title: 'Designing Story-Driven Visuals',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--gd-sky',
		description:
			'Use visuals to explain concepts clearly. Visual analogies, sequential design, and simplifying complex ideas into clear graphics.'
	},
	{
		id: '09',
		number: 9,
		title: 'Motion as a Design Tool',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--gd-amber',
		description:
			'Use motion to reinforce meaning. Anticipation, easing, and the relationship between static design and animated design.'
	},
	{
		id: '10',
		number: 10,
		title: 'Building Final Assets & Style Guide',
		subtitle: 'Capstone Project',
		status: 'available',
		accentVar: '--gd-sage',
		description:
			'Finalize your brand system. Logo, thumbnail templates, title cards, diagram sets, and a complete website layout kit.'
	}
];

export const visualStorytellingCourse: Course = {
	id: 'visual-storytelling',
	title: 'Visual Storytelling for Faceless Video',
	subtitle: 'Narrative, Pacing & Visual Communication',
	description:
		'Learn to create compelling faceless videos using text, images, b-roll, motion graphics, and pacing. This course teaches you to communicate meaning — not just information — through deliberate visual and narrative structure.',
	totalModules: 10
};

export const visualStorytellingModules: Module[] = [
	{
		id: '01',
		number: 1,
		title: 'The Foundations of Visual Storytelling',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--vs-blue',
		description:
			"What makes faceless content engaging, story structure for informational video, and how the viewer's cognitive process shapes every production decision."
	},
	{
		id: '02',
		number: 2,
		title: 'Sequencing, Pacing & Viewer Retention',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--vs-amber',
		description:
			'Use pacing strategically to maintain attention. Combine narration, visuals, and beats into deliberate rhythms that prevent cognitive drift.'
	},
	{
		id: '03',
		number: 3,
		title: 'Structuring Text for Video',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--vs-mint',
		description:
			'Use text as a visual element, not a transcript. Emphasis, contrast, hierarchy, and when to animate vs keep static.'
	},
	{
		id: '04',
		number: 4,
		title: 'Using Images, Diagrams & B-Roll Intentionally',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--vs-red',
		description:
			'Choose visuals that support the narrative rather than distract from it. Build diagrammatic clarity for educational storytelling.'
	},
	{
		id: '05',
		number: 5,
		title: 'Composition & Visual Hierarchy in Video Frames',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--vs-blue',
		description:
			"Plan frames that guide the viewer's eye purposefully. Use composition, balance, contrast, and isolation to support meaning."
	},
	{
		id: '06',
		number: 6,
		title: 'Motion Graphics for Narrative Support',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--vs-amber',
		description:
			'Use movement to explain concepts, not merely decorate. Direct attention with motion: reveal, highlight, transform.'
	},
	{
		id: '07',
		number: 7,
		title: 'Audio as a Narrative Anchor',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--vs-mint',
		description:
			'Use narration and sound design to reinforce visual meaning. Align audio beats with visual beats for deliberate rhythm.'
	},
	{
		id: '08',
		number: 8,
		title: 'Editing Techniques for Clarity & Engagement',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--vs-red',
		description:
			'Make purposeful cuts, transitions, and timing adjustments. Remove redundancy and build momentum that sustains viewer interest.'
	},
	{
		id: '09',
		number: 9,
		title: 'Building a Repeatable Visual Language',
		subtitle: 'Theory + Practice',
		status: 'available',
		accentVar: '--vs-blue',
		description:
			'Develop a consistent style your audience recognizes. Color, fonts, and layout as narrative tools. Reusable graphic systems.'
	},
	{
		id: '10',
		number: 10,
		title: 'End-to-End Faceless Video Production',
		subtitle: 'Capstone Project',
		status: 'available',
		accentVar: '--vs-amber',
		description:
			'Combine narration, images, text, pacing, and motion into a complete 1–2 minute polished, engagement-oriented faceless video.'
	}
];

export function getVSModule(id: string): Module | undefined {
	return visualStorytellingModules.find((m) => m.id === id);
}
export function getAdjacentVSModules(id: string): { prev: Module | null; next: Module | null } {
	const idx = visualStorytellingModules.findIndex((m) => m.id === id);
	return {
		prev: idx > 0 ? visualStorytellingModules[idx - 1] : null,
		next: idx < visualStorytellingModules.length - 1 ? visualStorytellingModules[idx + 1] : null
	};
}

export function getGraphicDesignModule(id: string): Module | undefined {
	return graphicDesignModules.find((m) => m.id === id);
}

export function getAdjacentGraphicDesignModules(id: string): {
	prev: Module | null;
	next: Module | null;
} {
	const idx = graphicDesignModules.findIndex((m) => m.id === id);
	return {
		prev: idx > 0 ? graphicDesignModules[idx - 1] : null,
		next: idx < graphicDesignModules.length - 1 ? graphicDesignModules[idx + 1] : null
	};
}
