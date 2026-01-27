# agents.md

This file provides guidance to AI coding assistants when working with this repository.

## Project Overview

<!-- Brief description of what this project does -->

## Tech Stack

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Database**: Supabase (Postgres)
- **Auth**: Supabase Auth
- **Deployment**: Vercel

## Code Style

- Concise and minimal - avoid unnecessary boilerplate
- Comments only when logic isn't self-evident
- Prefer simple solutions over clever ones
- Keep files focused and small
- Use tabs for indentation
- Use `pnpm` as package manager

## Conventions

- Mobile-first responsive design - always optimize for phone use
- Use Server Components by default, Client Components only when needed
- Colocate components with their routes when feature-specific
- Keep API routes thin - business logic in lib/
- Use Supabase RLS for authorization
- Commit format: `type: description` (feat, fix, refactor, docs, test, chore)

## Project Structure

```
app/
├── (auth)/           # Auth-related routes
├── api/              # API routes
├── layout.tsx        # Root layout
└── page.tsx          # Home page
components/
├── ui/               # Reusable UI components
└── [feature]/        # Feature-specific components
lib/
├── supabase/         # Supabase client and helpers
└── utils/            # Utility functions
```

## Key Features

<!-- List main features -->
