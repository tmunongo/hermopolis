import type { PageLoad } from './$types';
import { animationModules } from '$lib/data/courses';
import { error } from '@sveltejs/kit';

export const load: PageLoad = ({ params }) => {
	const mod = animationModules.find((m) => m.id === params.module);
	if (!mod) {
		throw error(404, `Module ${params.module} not found`);
	}
	const idx = animationModules.findIndex((m) => m.id === params.module);
	const prev = idx > 0 ? animationModules[idx - 1] : null;
	const next = idx < animationModules.length - 1 ? animationModules[idx + 1] : null;

	return { module: mod, prev, next };
};
