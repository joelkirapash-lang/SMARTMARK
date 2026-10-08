# What's built, mapped to your two spec documents

## From the invitation/auth workflow spec — fully implemented
- Two-record model: pending `User` (status INVITED) + `Invitation`, created together, no SmartMark account required up front
- Only SCHOOL_ADMIN can invite; enforced server-side (role check on every write route, not just hidden buttons)
- Admin dashboard "Invite" flow for both Teacher/Educator and Student, with all the fields listed in the spec
- `personal_email` and `smartmark_email` stored as distinct fields everywhere
- Auto-generated SmartMark login email (`firstname.secondname@role.school-slug.smartmark`), normalized (lowercase, accents stripped, spaces/hyphens/apostrophes handled), with deterministic numeric-suffix uniqueness on collision
- Cryptographically random invitation token, SHA-256 hash stored, raw token only ever in the outgoing URL
- 48h default expiry (configurable per school), resend (invalidates old token), cancel, "already used"/"expired"/"invalid" states all handled with the exact messages from the spec
- Email sent to `personal_email`, never to the unconfirmed SmartMark address; pluggable console/SMTP mailer
- Accept → verification screen → password creation → account ACTIVE → invitation single-use, invalidated on accept
- Passwords bcrypt-hashed, minimum strength enforced, never logged/emailed/returned
- All values (school_id, role, personal_email, smartmark_email) taken from the server-side invitation record on accept — a client can't smuggle in a different role or school
- Full audit logging of every invitation lifecycle event

## From the CBC marks-management spec — implemented
- Multi-tenant schema: every school-specific table carries `school_id`, every route queries through a school-scoped helper
- Empty-by-default onboarding: registering a school creates only the tenant + its first admin — no grades, streams, subjects, or students until the admin adds them
- Admin: manage grades, streams, subjects, performance bands (BE/AE/ME/EE with configurable score ranges), teachers, teacher grade/stream/subject assignments, students (individual invite + CSV bulk import), exams (create/publish), school branding/settings, activity log
- Teacher: server-side locked to assigned grade/stream/subject combinations for marks entry; read access to their classes only
- Marks entry: grade → stream → exam → subject grid, inline numeric validation, multi-row paste from a clipboard column
- Marklist: ranked by average, per grade/stream/exam, Excel export, print stylesheet
- Report card: per-student, per-exam, subject breakdown with performance band, totals/average, signature lines, portrait/landscape toggle, browser print-to-PDF
- Shareable, token-based, no-login parent report-card link (30-day expiry, only issuable once an exam is published)
- Dashboard: stat cards, subject averages chart, performance-level distribution, exam-vs-prior-exam most-improved table
- Year-end bulk promotion endpoint (`POST /students/promote`) with graduation/archiving
- Full audit/activity log, viewable in the admin UI

## Stubbed or simplified — worth a follow-up pass
- **PDF generation**: report cards and marklists currently rely on the browser's print-to-PDF (matches the spec's "print/save-as-PDF" requirement) rather than a server-rendered PDF via WeasyPrint/ReportLab. Swapping in true server-side PDF generation is a contained addition to `app/routes/reports.py`.
- **Remarks/comments bank per subject**: not yet built as a managed list — the `remark` field exists on `Mark` and is editable, but there's no admin screen for a reusable comment bank yet.
- **Deadline reminders & notifications** for pending marks: not implemented — would need a scheduler (e.g. APScheduler/Celery beat) plus a notifications table.
- **Global search** (student by name/admission number across the whole school) exists for students specifically (`/students?search=`) but isn't a unified cross-entity search yet.
- **Rate limiting** on login and the public report-card link: not yet added — recommend `Flask-Limiter` in front of `/api/auth/login` and `/api/reports/shared/*`.
- **Automated database backups**: infrastructure concern, left to your hosting setup (e.g. managed Postgres automated snapshots).
- **File/image storage** (crests, logos, student photos): the schema has `crest_url`/`logo_url`/`photo_url` fields and `STORAGE_BACKEND` is a config toggle, but no S3/Cloudinary upload endpoint is wired up yet — currently you'd set these fields to already-hosted URLs.
- **PWA / "Add to Home Screen"**: not configured; the spec marked this optional/later.
- **Automated test suite**: I ran a thorough manual/scripted integration test (see README) covering tenant isolation and RBAC, but there's no `pytest` suite checked in yet for CI.

None of the stubbed items affect the core guarantees (tenant isolation, the
invitation workflow, and role-based marks access) — they're additive
features on top of a working foundation.
