# Non-EpicBharat publishing hardening plan

Scope: all channels in this repository except EpicBharat. EpicBharat workflows, files, credentials, schedules, and publishing state are explicitly out of scope.

## Approved operating policy

- Publishing mode: automatic public publishing at each channel's configured schedule.
- MindNest Tales: retain the existing Wednesday, Saturday, Sunday cadence for all 11 language channels. Do not convert it to daily.
- Quality preference: 8K is the target where the source pipeline, encoder, runner capacity, and platform upload path support it. Do not silently upscale a 1080p render and label it 8K. Current DigitalImmortals pipeline is fixed at 1080x1920; it remains native 1080p until its renderer is redesigned and tested. TigerVlogs config has 4K slots while its workflow labels its render stage 1080p; reconcile this mismatch before claiming 8K output. 8K on GitHub-hosted runners needs a measured time/disk/memory test before enabling it.
- No workflow should be considered successful merely because a local file was generated. Confirm the returned platform post/video ID and final visibility/scheduled state.

## Changes staged on this branch

1. TigerVlogs config: remove EpicBharat handle/email from TigerVlogs branding; use its own configured channel handle and no invented contact email.
2. BuzzStormNow: archive only Blogger-confirmed PUBLISHED/SCHEDULED posts with a real post ID. Local fallback drafts, API errors, and Blogger drafts fail the run and do not advance the published archive. Add a source-URL idempotency guard.
3. DigitalImmortals: default scheduled uploads to public, validate privacy values and OAuth inputs, and require a returned YouTube video ID.

## P0: diagnose the current failed scheduled runs

The latest observed non-EpicBharat scheduled executions were failing. Obtain complete logs for:
- BuzzStormNow
- TigerVlogs-2026
- DigitalImmortals
- IndianHorrorTapes
- AllTrainReels
- MindNest Tales (all 11 language jobs)

Do not rerun the production schedules blindly. First reproduce with workflow_dispatch in a controlled test mode where upload is disabled or output is private, verify generated artifacts, and only then run one approved public canary per channel.

## Channel-specific remediation

- TigerVlogs: inspect the failing asset-preparation job; compare workflow's 1080p label with config's 4K slots; verify channel ID against token identity before upload; verify 2-versus-3 daily slot intent with the active scheduler; check topic exhaustion and no duplicate topics; ensure descriptions link to TigerVlogs only.
- AllTrainReels: inspect asset generation exception; verify YouTube token resolves to the expected channel ID; only advance episode state after confirmed upload; reconcile committed state with YouTube upload history before changing episode number.
- IndianHorrorTapes: inspect image/video generation exception; verify OAuth refresh and channel identity; preserve Wednesday/Sunday schedule; advance story only after confirmed YouTube video ID and scheduled/public status.
- MindNest Tales: run a per-language OAuth and upload preflight for all 11 locales; isolate failures so one language cannot mask another; retain Wednesday/Saturday/Sunday cadence; persist per-language story progress only after confirmed upload; reconcile story #2 state with YouTube history before resuming.
- DigitalImmortals: verify Anthropic key/model availability, Gemini image key/quota, YouTube token refresh, generated MP4, and returned video ID. Pipeline resolution currently 1080x1920; 8K requires a separately benchmarked render implementation.
- BuzzStormNow: verify Blogger token/client-secret scopes and target blog ID; publish a test draft only in an explicit dry-run; only mark source as published after Blogger returns post ID and public URL.

## Required common safeguards

- Channel identity preflight: OAuth token channel ID must match the configured channel ID before any upload.
- Duplicate protection: use stable source/story ID plus platform post ID; never rely solely on a local counter.
- Publication verification: after upload, fetch the uploaded resource and confirm channel ID, privacyStatus, publishAt (when scheduled), title, and returned ID.
- State discipline: commit progress only after platform confirmation; failed generation/upload must leave queue position unchanged.
- Timezone: declare schedule times in IST in documentation and verify UTC cron conversion.
- Monitoring: report each channel independently with expected slots, generated count, uploaded count, public/scheduled count, failed stage, run URL, and next retry.
- Retry: bounded retries with backoff for transient API errors; never retry an upload blindly if the previous request may have succeeded. Reconcile by idempotency key/video ID first.
- Secrets: validate presence without printing values; never commit token files or OAuth secrets.

## Acceptance checklist

A channel is green only when all checks pass:
1. Scheduled workflow ran at the intended IST time.
2. Generation completed and output has the expected aspect ratio, codec, duration, and declared resolution.
3. OAuth identity matches that channel's expected YouTube channel ID.
4. Upload returned a real platform ID.
5. Follow-up API read confirms channel ID, privacyStatus=public (or a confirmed future scheduled release), and expected publish time.
6. Persistent state advances exactly once.
7. Re-running the same job does not create a duplicate.
8. Failure notifications identify the failed stage and leave state recoverable.

## Safety boundary

No file or workflow belonging to EpicBharat may be included in this branch or PR. Do not merge or enable public scheduled runs until the failed workflows are diagnosed and the canary acceptance checks pass.
