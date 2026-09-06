# Indigenous Podcast

Responsive landing page for Indigenous Podcast, using the approved branding and supplied copy. The original uploaded logo is included byte for byte without alteration. No framework or build step is required.

## Cloudflare Pages

- Connect the `tryjesusmedia/indigenouspodcast` GitHub repository.
- Production branch: `main`.
- Framework preset: None.
- Build command: leave empty.
- Build output directory: `dist`.
- Add `indigenouspodcast.org` in the Cloudflare project's custom domains after the preview is approved.

The optional `wrangler.jsonc` also supports Cloudflare Workers static asset deployment using `npx wrangler deploy` in an authenticated Cloudflare environment. Use either Pages or Workers for the public domain, not both.

## Omnisend

- Brand ID: `67cb56fd73be448eba677afd`
- Embedded form: `omnisend-embedded-v2-67cb633ee44f1e1e39dd4822`
- Launcher: `https://omnisnippet1.com/inshop/launcher-v2.js`

`dist/main.js` loads the corrected snippet once. Actual form fields, consent, submission, and success/delivery behavior remain in the supplied Omnisend form. The page does not simulate submissions or store subscriber information. A loading/error state offers a retry if the external form is blocked or unavailable. Confirm the form is published and allowed on the final domain, its button reads “Send Me My Free Bible Guides,” and its success/automation delivers the promised immediate guide access. No test subscribers were created.

## Assets and content

- Original logo supplied by the site owner, preserved unchanged.
- Self-hosted Google Fonts: Manrope 700/800 and Source Sans 3 400/600. License files are in `dist/assets/licenses`.
- The preview is accurately labeled as an excerpt of the supplied introduction. A published lesson excerpt was not available.
- No verified host portrait, host name, or genuine community photograph was provided or available on the existing site. The page uses the original logo and an organization-level introduction. Replace this with owner-approved host material when supplied.

## Files

`dist/index.html` contains the full page; `dist/styles.css` contains responsive brand styling; `dist/main.js` manages Omnisend loading and updates the year. `.openai/hosting.json` identifies the private review Site.
