# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

<!-- Brief description of what this project does -->

## Tech Stack

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Database**: Supabase (Postgres)
- **Auth**: Supabase Auth
- **Deployment**: Vercel

## Commands

```bash
pnpm dev         # Start development server (localhost:3000)
pnpm build       # Production build (runs lint + type-check first)
pnpm lint        # Run ESLint
pnpm type-check  # Run TypeScript compiler check
pnpm test        # Run tests (if configured)
```

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

## Conventions

- Mobile-first responsive design - always optimize for phone use
- Use Server Components by default, Client Components only when needed
- Colocate components with their routes when feature-specific
- Keep API routes thin - business logic in lib/
- Use Supabase RLS for authorization
- Use tabs for indentation
- Commit format: `type: description` (feat, fix, refactor, docs, test, chore)
