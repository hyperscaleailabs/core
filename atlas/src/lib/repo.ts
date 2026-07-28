/**
 * Where this site lives in source control.
 *
 * Agentic Atlas was developed as a standalone repository and now ships as the
 * `atlas/` module of the hsailabs `core` monorepo. Every "view / edit / report
 * on GitHub" link in the UI is derived from the three constants below, so the
 * next move needs one edit rather than a sweep - the old repository's links
 * surviving a migration is the failure mode this file exists to prevent.
 *
 * The atlas CI workflow fails the build on any hardcoded repository URL
 * elsewhere in `src/`.
 */

/** Repository that hosts this module. */
export const REPO_URL = 'https://github.com/hyperscaleailabs/core';

/** Path of this module inside the repository, without leading or trailing slash. */
export const REPO_MODULE_PATH = 'atlas';

/** Browse the module's source. */
export const REPO_BROWSE_URL = `${REPO_URL}/tree/main/${REPO_MODULE_PATH}`;

/** Report a correction, a takedown request, or a bug. */
export const REPO_ISSUES_URL = `${REPO_URL}/issues`;

/** Repository-wide code license (Apache-2.0; content is CC BY 4.0). */
export const REPO_LICENSE_URL = `${REPO_URL}/blob/main/LICENSE`;

/** "Edit this page" target for one content entry. */
export function editUrlFor(collection: string, id: string): string {
  return `${REPO_URL}/edit/main/${REPO_MODULE_PATH}/src/content/${collection}/${id}`;
}
