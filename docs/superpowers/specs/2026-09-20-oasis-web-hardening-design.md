# O.A.S.I.S. web hardening design

## Goal

Improve the complete static website without changing its editorial/brutalist visual identity. The result must be clearer, more trustworthy, accessible, responsive and maintainable.

## Scope

### Shared foundation

- Keep current typography, monochrome palette, borders and layout language.
- Make `assets/site.css` the shared source of truth.
- Remove only duplicated rules from page-specific styles where safe.
- Preserve existing URLs and local anchors.

### Product truth and conversion

- Use one positioning line: local Windows assistant for files, documents and PC tasks.
- Label capabilities as available, beta, Max early access or roadmap.
- Clarify that Max has no checkout yet.
- Strengthen the first viewport and reduce technical jargon there.
- Keep technical detail on internal pages.

### Accessibility

- Preserve skip links, visible focus and reduced-motion support.
- Convert tooltip behavior to a non-disruptive accessible disclosure pattern.
- Avoid making every glossary term keyboard-focusable unless it has real interaction.
- Add proper labels/legends, live status updates and table header scopes.
- Mark decorative SVGs as hidden and keep meaningful diagrams described.
- Improve mobile menu focus and state handling.

### Privacy and runtime robustness

- Explain GitHub API and Cloudflare waitlist requests accurately.
- Add visible waitlist privacy/deletion guidance.
- Keep the waitlist fallback usable when JavaScript or network requests fail.
- Replace fragile browser API assumptions with guarded fallbacks.
- Keep external requests optional and non-blocking.

### SEO and sharing

- Add consistent Open Graph and Twitter metadata.
- Use the official `O.A.S.I.S.` brand consistently in metadata and schema.
- Keep canonical URLs and sitemap paths unchanged.
- Improve SoftwareApplication and FAQ structured data where applicable.

## Implementation order

1. Shared accessibility and runtime fixes.
2. Product truth, pricing, privacy and waitlist copy.
3. Shared CSS extraction and responsive refinements.
4. SEO metadata and structured data.
5. Home conversion improvements.
6. Static validation and manual responsive review.

## Constraints

- No framework migration.
- No analytics or tracking added.
- No destructive changes to existing content or URLs.
- No invented testimonials, metrics or product capabilities.
- Keep the site deployable as static HTML/Jekyll content.

## Verification

- Check all local links and anchors.
- Check heading order, labels, focus states and reduced motion.
- Check light/dark mode and narrow viewport layouts.
- Check metadata and JSON-LD validity.
- Run available project checks and report unavailable checks explicitly.
