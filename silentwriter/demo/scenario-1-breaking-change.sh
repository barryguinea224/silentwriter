#!/usr/bin/env bash
# ─────────────────────────────────────────────
# 🤫 SilentWriter — Demo Scenario 1
# "The Breaking Change That Never Happened"
# ─────────────────────────────────────────────
# Shows how SilentWriter BLOCKS a breaking API
# change and guides the developer to fix it.
# ─────────────────────────────────────────────

set -euo pipefail

# Colors for cinematic output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Simulated typing effect for cinematic feel
type_text() {
    local text="$1"
    local delay="${2:-0.03}"
    for (( i=0; i<${#text}; i++ )); do
        echo -n "${text:$i:1}"
        sleep "$delay"
    done
    echo
}

# Banner
clear
echo -e "${CYAN}${BOLD}"
echo "╔══════════════════════════════════════════════════╗"
echo "║  🤫 SilentWriter — IBM Bob Hackathon 2025       ║"
echo "║  Scenario 1: The Breaking Change                ║"
echo "║  \"Protecting the API from certain disaster\"      ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"
sleep 2

# ─────────────────────────────────────────────
# ACT 1: THE SETUP
# ─────────────────────────────────────────────
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}ACT 1: The Peaceful Codebase${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
sleep 1

echo -e "${BLUE}📂 Current state of src/api/users.ts:${NC}\n"
sleep 0.5

cat << 'EOF'
  // src/api/users.ts
  /**
   * Get a user by their ID.
   * Called by: 12 external services
   * @param id - string
   * @returns User | null
   */
  export function getUser(id: string): User | null {
    return db.users.findUnique({ where: { id } });
  }
EOF

echo -e "\n${GREEN}✅ This API is stable. 12 services depend on it.${NC}"
sleep 2

# ─────────────────────────────────────────────
# ACT 2: THE DEVELOPER MAKES A MISTAKE
# ─────────────────────────────────────────────
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}ACT 2: The Developer Arrives${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
sleep 1

echo -e "${BLUE}👨‍💻 A developer is adding email lookup functionality...${NC}\n"
sleep 1

echo -e "${RED}❌ They modify getUser() without realizing the impact:${NC}\n"
sleep 1

cat << 'EOF'
  // src/api/users.ts (MODIFIED — BREAKING CHANGE)
  export function getUser(email: string): User | null {
  //                          ^^^^^ changed from 'id' to 'email'
    return db.users.findUnique({ where: { email } });
  }
EOF

echo -e "\n${RED}⚠️  The parameter was changed from 'id' to 'email'${NC}"
echo -e "${RED}⚠️  This will break ALL 12 services calling getUser()${NC}"
sleep 2

# ─────────────────────────────────────────────
# ACT 3: THE COMMIT & PR
# ─────────────────────────────────────────────
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}ACT 3: The Pull Request${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
sleep 1

echo -e "${BLUE}📝 Developer commits and opens a PR...${NC}\n"
sleep 1

type_text "$ git add src/api/users.ts" 0.05
sleep 0.3
type_text "$ git commit -m \"feat: add email lookup to getUser\"" 0.05
sleep 0.3
type_text "$ git push origin feature/email-lookup" 0.05
sleep 1

echo -e "\n${CYAN}🔄 GitHub Actions triggers SilentWriter...${NC}\n"
sleep 1

# ─────────────────────────────────────────────
# ACT 4: BOB / SILENTWRITER INTERVENTION
# ─────────────────────────────────────────────
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}ACT 4: SilentWriter Intervention${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
sleep 1

echo -e "${CYAN}🤫 IBM Bob activates 'silent-guardian' mode...${NC}\n"
sleep 1

echo -e "${CYAN}📋 Loading .silentwriter.yml...${NC}"
sleep 0.5
echo -e "${CYAN}🔍 Analyzing diff against SILENT-001...${NC}"
sleep 1
echo -e "${CYAN}🧠 IBM Granite analyzing code semantics...${NC}\n"
sleep 1.5

echo -e "${RED}${BOLD}┌─────────────────────────────────────────────┐${NC}"
echo -e "${RED}${BOLD}│  🛡️  VERDICT: BLOCK                         │${NC}"
echo -e "${RED}${BOLD}│  Rule: SILENT-001 — Protect API Contracts   │${NC}"
echo -e "${RED}${BOLD}│  Impact: 12 services would break            │${NC}"
echo -e "${RED}${BOLD}└─────────────────────────────────────────────┘${NC}\n"
sleep 2

# Bob's response
echo -e "${CYAN}🤖 Bob posts on the PR:${NC}\n"
sleep 0.5

cat << 'EOF'
  ┌────────────────────────────────────────────────────
  │ 🤫 SilentWriter
  │
  │ 🛡️ Breaking change detected in API layer.
  │
  │ File: src/api/users.ts
  │ Function: getUser()
  │ Rule: SILENT-001 — Protect API Contracts
  │
  │ This function is called by 12 external services.
  │ Changing 'id' to 'email' would break all of them.
  │
  │ What to do instead:
  │ 1. Create getUserByEmail() for your new feature
  │ 2. Keep getUser(id) untouched
  │ 3. Add @deprecated if migrating later
  │
  │ I can generate the code. Type /silent-fix
  └────────────────────────────────────────────────────
EOF

sleep 3

# ─────────────────────────────────────────────
# ACT 5: THE FIX
# ─────────────────────────────────────────────
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}ACT 5: The Developer Fixes It${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
sleep 1

echo -e "${BLUE}👨‍💻 Developer: /silent-fix${NC}\n"
sleep 1

echo -e "${CYAN}🤖 Bob generates the fix:${NC}\n"
sleep 1

cat << 'EOF'
  // src/api/users.ts (FIXED)
  
  /**
   * Get a user by their ID.
   * Called by: 12 external services
   * @param id - string
   * @returns User | null
   */
  export function getUser(id: string): User | null {
    return db.users.findUnique({ where: { id } });
  }
  
  /**
   * Get a user by their email.
   * NEW — no breaking changes
   * @param email - string
   * @returns User | null
   */
  export function getUserByEmail(email: string): User | null {
    return db.users.findUnique({ where: { email } });
  }
EOF

echo -e "\n${GREEN}✅ No breaking changes. Both functions coexist.${NC}"
sleep 2

# ─────────────────────────────────────────────
# ACT 6: BOOMERANG — AUTO-APPROVE
# ─────────────────────────────────────────────
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}ACT 6: SilentWriter Auto-Approve${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
sleep 1

echo -e "${BLUE}📝 Developer pushes the fix...${NC}\n"
sleep 1

echo -e "${CYAN}🔄 SilentWriter re-analyzes...${NC}\n"
sleep 1.5

echo -e "${GREEN}${BOLD}┌─────────────────────────────────────────────┐${NC}"
echo -e "${GREEN}${BOLD}│  ✅  VERDICT: PASS                          │${NC}"
echo -e "${GREEN}${BOLD}│  All rules satisfied                        │${NC}"
echo -e "${GREEN}${BOLD}│  Auto-approved & merged                     │${NC}"
echo -e "${GREEN}${BOLD}└─────────────────────────────────────────────┘${NC}\n"
sleep 2

# ─────────────────────────────────────────────
# OUTRO
# ─────────────────────────────────────────────
echo -e "\n${CYAN}${BOLD}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║  🤫 SilentWriter prevented a production outage  ║${NC}"
echo -e "${CYAN}${BOLD}║  12 services saved from certain breakage         ║${NC}"
echo -e "${CYAN}${BOLD}║  Zero human intervention needed                  ║${NC}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════════╝${NC}"
echo
echo -e "${CYAN}Powered by IBM Bob · Granite · WatsonX${NC}"
echo -e "${CYAN}Learn more: github.com/your-org/silentwriter${NC}\n"
