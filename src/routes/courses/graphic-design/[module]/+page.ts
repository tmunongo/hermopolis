import type { PageLoad } from './$types';
import { graphicDesignModules } from '$lib/data/courses';
import { error } from '@sveltejs/kit';

export const load: PageLoad = ({ params }) => {
	const mod = graphicDesignModules.find((m) => m.id === params.module);
	if (!mod) {
		throw error(404, `Module ${params.module} not found`);
	}
	const idx = graphicDesignModules.findIndex((m) => m.id === params.module);
	const prev = idx > 0 ? graphicDesignModules[idx - 1] : null;
	const next = idx < graphicDesignModules.length - 1 ? graphicDesignModules[idx + 1] : null;

	return { module: mod, prev, next };
};
