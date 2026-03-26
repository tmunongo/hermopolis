import type { PageLoad } from './$types';
import { getModule, getAdjacentModules } from '$lib/data/courses';
import { error } from '@sveltejs/kit';

export const load: PageLoad = ({ params }) => {
	const mod = getModule(params.module);
	if (!mod) {
		throw error(404, `Module ${params.module} not found`);
	}
	const { prev, next } = getAdjacentModules(params.module);
	return { module: mod, prev, next };
};
