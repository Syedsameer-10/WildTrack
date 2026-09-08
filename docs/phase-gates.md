# Phase Gates

No phase begins until the preceding phase is tested by the user and explicitly approved.

## Required completion report

Every phase handoff contains:

```text
Phase:
Implemented:
Architecture decisions:
Automated checks:
How to start it:
User test procedure:
Expected results:
Known limitations:
Approval required:
```

## Definition of done

A phase is complete only when:

- Its stated scope is implemented without pulling unfinished features forward.
- Relevant automated checks pass.
- Documentation and `.env.example` match the implementation.
- No secret is committed or exposed to the frontend.
- New database changes are expressed as repeatable migrations.
- Deployment assumptions remain valid.
- Failure states produce useful messages.
- The user completes the manual test and approves proceeding.

## Change control

Defects found during user testing remain part of the current phase. Architecture changes are recorded before dependent implementation proceeds. Generated files, credentials, and unrelated project artifacts are not included in a phase checkpoint.

