---
name: setup-integration
description: Scaffold third-party service integrations (Stripe, Notion, Twilio, Cloudinary, Supabase)
argument-hint: [stripe|notion|twilio|cloudinary|supabase]
---

# Setup Integration

Scaffold a third-party service integration into the current project: env vars, boilerplate client, and setup checklist.

**Argument:** $ARGUMENTS

**IMPORTANT:** Use the `AskUserQuestion` tool for ALL questions in this skill. Never list options as plain text.

---

## Step 1: Choose a Service

If a service name is not provided in $ARGUMENTS, ask using `AskUserQuestion`:

Question: "Which service do you want to integrate?"
Options:
1. Stripe (payments)
2. Notion (CMS / database)
3. Twilio (SMS)
4. Cloudinary (image hosting)
5. Supabase (additional tables / RLS setup)
6. Other (manual)

**Wait for response before proceeding.**

---

## Step 2: Service-Specific Setup

### If Stripe was selected:

#### 2a. Install package

```bash
pnpm add stripe @stripe/stripe-js
```

#### 2b. Add env vars

Append to `.env.local` if it exists, otherwise create it. Add only keys that are not already present:

```
# Stripe
STRIPE_SECRET_KEY=sk_test_REPLACE_ME
STRIPE_PUBLISHABLE_KEY=pk_test_REPLACE_ME
STRIPE_WEBHOOK_SECRET=whsec_REPLACE_ME
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_REPLACE_ME
```

Append the same keys (without values) to `.env.example` if it exists, otherwise create it:

```
# Stripe
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
```

#### 2c. Create `lib/stripe.ts`

Create the file only if it does not already exist:

```typescript
import Stripe from 'stripe'

if (!process.env.STRIPE_SECRET_KEY) {
	throw new Error('Missing STRIPE_SECRET_KEY environment variable')
}

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
	apiVersion: '2024-06-20',
	typescript: true,
})
```

#### 2d. Dashboard checklist

Output these steps for the user to complete manually:

```
Stripe Dashboard Steps:
1. Go to https://dashboard.stripe.com/apikeys
   - Copy Secret key → STRIPE_SECRET_KEY
   - Copy Publishable key → STRIPE_PUBLISHABLE_KEY and NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY

2. Go to https://dashboard.stripe.com/webhooks → Add endpoint
   - Endpoint URL: https://your-domain.com/api/webhooks/stripe
   - Select events to listen for (e.g. checkout.session.completed, payment_intent.succeeded)
   - Copy Signing secret → STRIPE_WEBHOOK_SECRET

3. For local testing, install the Stripe CLI and run:
   stripe listen --forward-to localhost:3000/api/webhooks/stripe
```

---

### If Notion was selected:

#### 2a. Install package

```bash
pnpm add @notionhq/client
```

#### 2b. Ask how many databases to connect

Using `AskUserQuestion`:

Question: "How many Notion databases will this integration use?"
Options:
1. One database
2. Two databases
3. Three or more — I'll add the rest manually

**Wait for response.**

For each database (up to the number selected), ask using `AskUserQuestion` (text input):

Question: "What is a short name for database [N]? (e.g. posts, products, users)"

Use the provided name in the env var key: `NOTION_DATABASE_ID_[NAME_UPPERCASE]`.

#### 2c. Add env vars

Append to `.env.local`:

```
# Notion
NOTION_API_KEY=secret_REPLACE_ME
NOTION_DATABASE_ID_[NAME]=REPLACE_ME
# (repeat for each database)
```

Append to `.env.example`:

```
# Notion
NOTION_API_KEY=
NOTION_DATABASE_ID_[NAME]=
# (repeat for each database)
```

#### 2d. Create `lib/notion.ts`

```typescript
import { Client } from '@notionhq/client'

if (!process.env.NOTION_API_KEY) {
	throw new Error('Missing NOTION_API_KEY environment variable')
}

export const notion = new Client({
	auth: process.env.NOTION_API_KEY,
})

// Example: fetch all entries from a database
export async function getDatabaseEntries(databaseId: string) {
	const response = await notion.databases.query({
		database_id: databaseId,
	})
	return response.results
}
```

#### 2e. Dashboard checklist

```
Notion Setup Steps:
1. Go to https://www.notion.so/profile/integrations → New integration
   - Give it a name and select your workspace
   - Copy Internal Integration Secret → NOTION_API_KEY

2. For each database you want to connect:
   - Open the database in Notion
   - Click ••• (top-right) → Connections → Add connection → select your integration
   - Copy the database ID from the URL:
     notion.so/[workspace]/[DATABASE_ID]?v=...
     → NOTION_DATABASE_ID_[NAME]

3. Repeat step 2 for every database this integration needs access to.
```

---

### If Twilio was selected:

#### 2a. Install package

```bash
pnpm add twilio
```

#### 2b. Add env vars

Append to `.env.local`:

```
# Twilio
TWILIO_ACCOUNT_SID=ACREPLACE_ME
TWILIO_AUTH_TOKEN=REPLACE_ME
TWILIO_PHONE_NUMBER=+1REPLACE_ME
TWILIO_MESSAGING_SERVICE_SID=MGREPLACE_ME
```

Append to `.env.example`:

```
# Twilio
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
TWILIO_MESSAGING_SERVICE_SID=
```

#### 2c. Create `lib/twilio.ts`

```typescript
import twilio from 'twilio'

if (
	!process.env.TWILIO_ACCOUNT_SID ||
	!process.env.TWILIO_AUTH_TOKEN ||
	!process.env.TWILIO_PHONE_NUMBER
) {
	throw new Error('Missing required Twilio environment variables')
}

const client = twilio(
	process.env.TWILIO_ACCOUNT_SID,
	process.env.TWILIO_AUTH_TOKEN
)

export async function sendSms({
	to,
	body,
}: {
	to: string
	body: string
}) {
	return client.messages.create({
		body,
		from: process.env.TWILIO_MESSAGING_SERVICE_SID
			? undefined
			: process.env.TWILIO_PHONE_NUMBER,
		messagingServiceSid: process.env.TWILIO_MESSAGING_SERVICE_SID || undefined,
		to,
	})
}
```

#### 2d. Dashboard checklist

```
Twilio Setup Steps:
1. Go to https://console.twilio.com
   - Copy Account SID → TWILIO_ACCOUNT_SID
   - Copy Auth Token → TWILIO_AUTH_TOKEN

2. Go to Phone Numbers → Manage → Active Numbers
   - Copy your number → TWILIO_PHONE_NUMBER

3. (Recommended) Go to Messaging → Services → Create Messaging Service
   - Add your phone number to the service
   - Copy Messaging Service SID → TWILIO_MESSAGING_SERVICE_SID
   - Using a Messaging Service improves deliverability and enables sticky sender
```

#### 2e. SMS compliance reminder

```
SMS Compliance (Required):
- Only send to users who have explicitly opted in — document consent
- Always honor STOP: auto-unsubscribe users who reply STOP
- Always respond to HELP: reply with your support contact
- Include your brand name in the first message: "Reply STOP to unsubscribe"
- Do not send between 9 PM and 8 AM in the recipient's timezone
- Review TCPA and carrier guidelines before launching
```

---

### If Cloudinary was selected:

#### 2a. Install package

```bash
pnpm add cloudinary
```

#### 2b. Add env vars

Append to `.env.local`:

```
# Cloudinary
CLOUDINARY_CLOUD_NAME=REPLACE_ME
CLOUDINARY_API_KEY=REPLACE_ME
CLOUDINARY_API_SECRET=REPLACE_ME
NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME=REPLACE_ME
```

Append to `.env.example`:

```
# Cloudinary
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME=
```

#### 2c. Create `lib/cloudinary.ts`

```typescript
import { v2 as cloudinary } from 'cloudinary'

if (
	!process.env.CLOUDINARY_CLOUD_NAME ||
	!process.env.CLOUDINARY_API_KEY ||
	!process.env.CLOUDINARY_API_SECRET
) {
	throw new Error('Missing required Cloudinary environment variables')
}

cloudinary.config({
	cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
	api_key: process.env.CLOUDINARY_API_KEY,
	api_secret: process.env.CLOUDINARY_API_SECRET,
	secure: true,
})

export { cloudinary }

// Upload a file from a local path or remote URL
export async function uploadImage(
	source: string,
	options?: { folder?: string; public_id?: string }
) {
	return cloudinary.uploader.upload(source, {
		folder: options?.folder,
		public_id: options?.public_id,
	})
}

// Delete an image by public_id
export async function deleteImage(publicId: string) {
	return cloudinary.uploader.destroy(publicId)
}
```

#### 2d. Dashboard checklist

```
Cloudinary Setup Steps:
1. Go to https://cloudinary.com/console
   - Copy Cloud name → CLOUDINARY_CLOUD_NAME and NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME
   - Copy API Key → CLOUDINARY_API_KEY
   - Copy API Secret → CLOUDINARY_API_SECRET

2. (Optional) Create upload presets for unsigned client-side uploads:
   Settings → Upload → Upload presets → Add upload preset
   Set signing mode to "Unsigned" for client-side use

3. (Recommended) Set up a default folder structure in Media Library to keep uploads organized
```

---

### If Supabase was selected:

#### 2a. Ask what to set up

Using `AskUserQuestion` with `multiSelect: true`:

Question: "What Supabase setup do you need?"
Options:
- Create new table(s) with SQL migration
- Add Row Level Security (RLS) policies to existing table(s)
- Create a storage bucket
- Set up edge function scaffold
- Add missing env vars (NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY)

**Wait for response.**

#### 2b. New table(s)

For each table, ask using `AskUserQuestion` (text input):

Question: "Describe the table — name and columns (e.g. 'posts: id, user_id, title, body, created_at')"

Generate the SQL migration and write it to `supabase/migrations/[timestamp]_create_[table].sql`:

```sql
create table [table_name] (
  id uuid primary key default gen_random_uuid(),
  -- columns from user description
  created_at timestamptz not null default now()
);

-- Enable RLS immediately
alter table [table_name] enable row level security;
```

Then ask using `AskUserQuestion`:

Question: "Should I add a basic RLS policy for this table? (authenticated users can read/write their own rows)"
Options:
1. Yes, add owner-based policy (user_id = auth.uid())
2. Yes, add public read / authenticated write policy
3. No, I'll write the policies manually

Append the selected policy to the migration file.

#### 2c. RLS on existing table

Ask using `AskUserQuestion` (text input):

Question: "Which table needs RLS policies? What access pattern? (e.g. 'posts — owners can CRUD, everyone can read')"

Generate and output the SQL policies. Remind user to run them in the Supabase SQL editor or via migration.

#### 2d. Storage bucket

Ask using `AskUserQuestion` (text input):

Question: "What should the storage bucket be named? (e.g. avatars, uploads)"

Output the SQL:

```sql
insert into storage.buckets (id, name, public)
values ('[bucket-name]', '[bucket-name]', false);

-- Allow authenticated users to upload
create policy "Authenticated users can upload"
on storage.objects for insert
to authenticated
with check (bucket_id = '[bucket-name]');

-- Allow owners to read their own files
create policy "Owners can read their files"
on storage.objects for select
to authenticated
using (auth.uid() = owner);
```

#### 2e. Missing env vars

Append to `.env.local` if not already present:

```
NEXT_PUBLIC_SUPABASE_URL=https://REPLACE_ME.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=REPLACE_ME
```

Append to `.env.example`:

```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

---

### If Other was selected:

Ask using `AskUserQuestion` (text input):

Question: "Describe the service you want to integrate and what you need (env vars, boilerplate, setup steps)."

**Wait for response.**

Use the description to:
1. Identify required env vars and add them to `.env.local` and `.env.example`
2. Create a `lib/[service-name].ts` client boilerplate if applicable
3. List manual dashboard steps the user needs to take

---

## Step 3: Verify

After scaffolding, output a summary checklist:

```
Integration scaffolded: [Service Name]

Files created/updated:
- .env.local (env var placeholders added)
- .env.example (env var keys added)
- lib/[service].ts (client boilerplate)
[- supabase/migrations/... (if applicable)]

Next steps:
1. Fill in the real values in .env.local
2. Complete the dashboard steps listed above
3. Restart your dev server: pnpm dev
4. Test the integration with a minimal call before building on top of it
```

Then ask using `AskUserQuestion`:

Question: "Do you want to set up another integration?"
Options:
1. Yes, go back to the service list
2. No, I'm done

If yes, return to Step 1.

---

## Quick Start Examples

```bash
# Interactive — asks which service
/setup-integration

# Skip the service selection
/setup-integration stripe
/setup-integration notion
/setup-integration twilio
/setup-integration cloudinary
/setup-integration supabase
```
