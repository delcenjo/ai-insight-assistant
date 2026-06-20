# Engineering Guide

## Technology stack

The backend is built with **Python and FastAPI**, the frontend with **React**,
and data is stored in **PostgreSQL**. Services run on **AWS**.

## Deployment

We use continuous delivery through **GitHub Actions**. Merging to `main`
automatically deploys to the staging environment; promotion to production is a
manual approval step. Risky changes are rolled out behind feature flags.

## On-call

Engineers take part in a weekly on-call rotation managed through PagerDuty.
Every production incident is followed by a written postmortem within three
working days, focused on prevention rather than blame.
