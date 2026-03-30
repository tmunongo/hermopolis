import type { PageLoad } from './$types';
import { visualStorytellingModules } from '$lib/data/courses';
import { error } from '@sveltejs/kit';

export const load: PageLoad = ({ params }) => {
	const mod = visualStorytellingModules.find((m) => m.id === params.module);
	if (!mod) {
		throw error(404, `Module ${params.module} not found`);
	}
	const idx = visualStorytellingModules.findIndex((m) => m.id === params.module);
	const prev = idx > 0 ? visualStorytellingModules[idx - 1] : null;
	const next =
		idx < visualStorytellingModules.length - 1 ? visualStorytellingModules[idx + 1] : null;

	return { module: mod, prev, next };
};
