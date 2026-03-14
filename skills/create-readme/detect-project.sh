#!/bin/bash
# Detect project type and extract metadata for README generation
# Outputs JSON to stdout

set -e

# Initialize defaults
TYPE="unknown"
NAME=""
VERSION=""
DESCRIPTION=""
PACKAGE_MANAGER="unknown"
FRAMEWORK="none"
DATABASE="none"
HAS_TESTS=false
TEST_COMMAND=""
HAS_PRISMA=false
HAS_ENV_EXAMPLE=false

# Check for Node.js project
if [[ -f "package.json" ]]; then
	TYPE="node"
	NAME=$(jq -r '.name // ""' package.json 2>/dev/null || echo "")
	VERSION=$(jq -r '.version // ""' package.json 2>/dev/null || echo "")
	DESCRIPTION=$(jq -r '.description // ""' package.json 2>/dev/null || echo "")

	# Detect package manager
	if [[ -f "pnpm-lock.yaml" ]]; then
		PACKAGE_MANAGER="pnpm"
	elif [[ -f "yarn.lock" ]]; then
		PACKAGE_MANAGER="yarn"
	elif [[ -f "package-lock.json" ]]; then
		PACKAGE_MANAGER="npm"
	else
		PACKAGE_MANAGER="pnpm"  # Default per CLAUDE.md
	fi

	# Detect framework
	if [[ -f "next.config.js" ]] || [[ -f "next.config.ts" ]] || [[ -f "next.config.mjs" ]]; then
		TYPE="nextjs"
		FRAMEWORK="next"
	elif jq -e '.dependencies.express' package.json >/dev/null 2>&1; then
		FRAMEWORK="express"
	elif jq -e '.dependencies.fastify' package.json >/dev/null 2>&1; then
		FRAMEWORK="fastify"
	fi

	# Detect database
	if jq -e '.dependencies["@prisma/client"]' package.json >/dev/null 2>&1; then
		DATABASE="postgresql"
		HAS_PRISMA=true
	elif jq -e '.dependencies.pg' package.json >/dev/null 2>&1; then
		DATABASE="postgresql"
	elif jq -e '.dependencies.mysql2' package.json >/dev/null 2>&1; then
		DATABASE="mysql"
	elif jq -e '.dependencies.mongodb' package.json >/dev/null 2>&1; then
		DATABASE="mongodb"
	fi

	# Check for tests
	if jq -e '.scripts.test' package.json >/dev/null 2>&1; then
		HAS_TESTS=true
		TEST_COMMAND="${PACKAGE_MANAGER} test"
	fi

# Check for Python project
elif [[ -f "pyproject.toml" ]]; then
	TYPE="python"
	NAME=$(grep -E '^name\s*=' pyproject.toml | head -1 | sed 's/.*=\s*"\(.*\)"/\1/' 2>/dev/null || echo "")
	VERSION=$(grep -E '^version\s*=' pyproject.toml | head -1 | sed 's/.*=\s*"\(.*\)"/\1/' 2>/dev/null || echo "")
	DESCRIPTION=$(grep -E '^description\s*=' pyproject.toml | head -1 | sed 's/.*=\s*"\(.*\)"/\1/' 2>/dev/null || echo "")

	PACKAGE_MANAGER="uv"

	# Detect framework
	if grep -q "fastapi" pyproject.toml 2>/dev/null; then
		FRAMEWORK="fastapi"
	elif grep -q "flask" pyproject.toml 2>/dev/null; then
		FRAMEWORK="flask"
	elif grep -q "django" pyproject.toml 2>/dev/null; then
		FRAMEWORK="django"
	fi

	# Check for tests
	if [[ -d "tests" ]] || [[ -d "test" ]]; then
		HAS_TESTS=true
		TEST_COMMAND="pytest"
	fi

elif [[ -f "requirements.txt" ]]; then
	TYPE="python"
	PACKAGE_MANAGER="uv"

	if grep -q "fastapi" requirements.txt 2>/dev/null; then
		FRAMEWORK="fastapi"
	elif grep -q "flask" requirements.txt 2>/dev/null; then
		FRAMEWORK="flask"
	elif grep -q "django" requirements.txt 2>/dev/null; then
		FRAMEWORK="django"
	fi

	if [[ -d "tests" ]] || [[ -d "test" ]]; then
		HAS_TESTS=true
		TEST_COMMAND="pytest"
	fi
fi

# Check for Prisma
if [[ -d "prisma" ]]; then
	HAS_PRISMA=true
fi

# Check for .env.example
if [[ -f ".env.example" ]]; then
	HAS_ENV_EXAMPLE=true
fi

# Check for README
README_EXISTS=false
if [[ -f "README.md" ]] || [[ -f "readme.md" ]] || [[ -f "README" ]]; then
	README_EXISTS=true
fi

# Get project name from directory if not found
if [[ -z "$NAME" ]]; then
	NAME=$(basename "$(pwd)")
fi

# Output JSON safely with jq
jq -n \
	--arg type "$TYPE" \
	--arg name "$NAME" \
	--arg version "$VERSION" \
	--arg description "$DESCRIPTION" \
	--arg packageManager "$PACKAGE_MANAGER" \
	--arg framework "$FRAMEWORK" \
	--arg database "$DATABASE" \
	--argjson hasTests "$HAS_TESTS" \
	--arg testCommand "$TEST_COMMAND" \
	--argjson hasPrisma "$HAS_PRISMA" \
	--argjson hasEnvExample "$HAS_ENV_EXAMPLE" \
	--argjson readmeExists "$README_EXISTS" \
	'{type: $type, name: $name, version: $version, description: $description, packageManager: $packageManager, framework: $framework, database: $database, hasTests: $hasTests, testCommand: $testCommand, hasPrisma: $hasPrisma, hasEnvExample: $hasEnvExample, readmeExists: $readmeExists}'
