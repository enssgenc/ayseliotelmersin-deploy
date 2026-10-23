Ayseli Reseliva integration — 23 October 2026

This release preserves the exact 22 October production export and its consent,
phone conversion, WhatsApp, gallery, map and branding assets. The booking card
now mounts the official HTTPS Reseliva widget once, after React hydration.

Reproduce from this repository:
  python3 integration/reseliva/prepare_reseliva_release.py
The generated static site is integration/reseliva/ayseli-reseliva/.
The published tarball is releases/2026-10-23/ayseli-reseliva-release.tar.gz.

Source changes are in reseliva-init.js and reseliva-theme.css. The Python script
applies the booking card and associated FAQ/privacy copy to the static export,
then gives changed client assets content hashes to avoid stale cached code.

Verified in the browser: date selection and checkout adjustment; 30–31 October
2026 / 2 adults transferred to Reseliva with available rooms and prices; 1 adult
transferred without silently reverting to 2; 390px responsive layout.
No reservation, payment or message was submitted.

Provider limitation: the current Ayseli engine resets searches containing
children to 2 adults / 0 children. maxChild=0 therefore hides this unsupported
selection. An explicit children/group WhatsApp enquiry link preserves that flow.
Re-enable children only after confirming the provider's occupancy configuration.
The Reseliva contact phone differs from the hotel's current public website.

For rollback, restore the previous pinned release URL and SHA256 from the
22 October production Dockerfile; do not deploy a different application's build.
