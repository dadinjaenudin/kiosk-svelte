# LLM Instruction Files - Kiosk POS Application

## Purpose
Dokumentasi ini dirancang sebagai **context reference untuk Large Language Models (LLMs)** agar dapat memahami arsitektur, konsep, dan implementasi aplikasi Kiosk POS dengan baik. Dokumentasi ini juga dapat digunakan sebagai **template untuk generate aplikasi serupa**.

## How to Use

### For LLM Context
Ketika bekerja dengan LLM untuk development, maintenance, atau troubleshooting aplikasi ini:

1. **Load dokumen sesuai kebutuhan**:
   - General understanding → Baca `00-OVERVIEW.md` dan `01-ARCHITECTURE.md`
   - Technical implementation → Baca `02-TECH-STACK.md` dan `05-MODULES.md`
   - RBAC/Multi-tenant issues → Baca `03-RBAC-MULTI-TENANT.md`
   - Database queries → Baca `04-DATABASE-SCHEMA.md`

2. **Provide relevant context dalam prompt**:
   ```
   "Berdasarkan arsitektur di .instruction/01-ARCHITECTURE.md,
   buatkan fitur baru untuk..."
   ```

3. **Reference specific sections**:
   ```
   "Sesuai dengan RBAC policy di .instruction/03-RBAC-MULTI-TENANT.md,
   bagaimana cara menambahkan role baru?"
   ```

### For Creating Similar Applications
Gunakan dokumentasi ini sebagai blueprint:

1. **Study the patterns**:
   - Multi-tenant architecture pattern
   - RBAC implementation
   - Module structure
   - API design

2. **Adapt to new requirements**:
   - Replace business domain (POS → Inventory, HR, etc.)
   - Keep the architecture patterns
   - Modify modules as needed

3. **Generate with LLM**:
   ```
   "Generate aplikasi [domain] menggunakan pattern dari
   .instruction folder kiosk-svelte, dengan adaptasi:
   - [Change 1]
   - [Change 2]"
   ```

## Document Structure

### 📄 [00-OVERVIEW.md](./00-OVERVIEW.md)
**Purpose**: High-level understanding aplikasi
**Contains**:
- Apa itu Kiosk POS
- Main objectives
- Target users
- Key capabilities

**Use when**: 
- Onboarding new developers
- Explaining system to stakeholders
- Planning new features

---

### 🏗️ [01-ARCHITECTURE.md](./01-ARCHITECTURE.md)
**Purpose**: System architecture & design patterns
**Contains**:
- System architecture diagram
- Component relationships
- Data flow
- Design decisions

**Use when**:
- Understanding system structure
- Planning architectural changes
- Debugging integration issues
- Scaling considerations

---

### 💻 [02-TECH-STACK.md](./02-TECH-STACK.md)
**Purpose**: Technology choices & versions
**Contains**:
- Backend technologies (Django, Python)
- Frontend technologies (SvelteKit, Tailwind)
- Infrastructure (Docker, Nginx)
- Libraries & dependencies

**Use when**:
- Setting up development environment
- Upgrading dependencies
- Evaluating technology alternatives
- Troubleshooting compatibility issues

---

### 🔐 [03-RBAC-MULTI-TENANT.md](./03-RBAC-MULTI-TENANT.md)
**Purpose**: Core concept explanation - RBAC & Multi-tenancy
**Contains**:
- Multi-tenant architecture explained
- RBAC (Role-Based Access Control) implementation
- Tenant isolation patterns
- Permission matrix
- Security considerations

**Use when**:
- Implementing tenant-specific features
- Adding new roles/permissions
- Debugging access control issues
- Ensuring data isolation
- Security auditing

---

### 🗄️ [04-DATABASE-SCHEMA.md](./04-DATABASE-SCHEMA.md)
**Purpose**: Database structure & relationships
**Contains**:
- Entity Relationship Diagrams (ERD)
- Table schemas
- Relationships & foreign keys
- Indexes
- Data flow

**Use when**:
- Writing database queries
- Planning schema migrations
- Optimizing database performance
- Understanding data relationships
- Creating new models

---

### 📦 [05-MODULES.md](./05-MODULES.md)
**Purpose**: Application modules & features
**Contains**:
- Module list & descriptions
- Module dependencies
- API endpoints per module
- File structure
- Feature capabilities

**Use when**:
- Adding new features
- Understanding module interactions
- API development
- Code navigation
- Testing

---

## Quick Reference

### Common LLM Prompts

**1. Add New Feature**
```
Context: Aplikasi Kiosk POS dengan RBAC Multi-tenant
(lihat .instruction/00-OVERVIEW.md dan 03-RBAC-MULTI-TENANT.md)

Task: Buatkan fitur [FEATURE_NAME] dengan:
- Tenant isolation sesuai pattern yang ada
- RBAC permissions untuk role [ROLES]
- API endpoint di module [MODULE]

Requirements:
- [REQ_1]
- [REQ_2]
```

**2. Fix Bug**
```
Context: [MODULE] module (lihat .instruction/05-MODULES.md)
Database schema: [TABLE] (lihat .instruction/04-DATABASE-SCHEMA.md)

Issue: [DESCRIBE_BUG]

Expected: [EXPECTED_BEHAVIOR]
Actual: [ACTUAL_BEHAVIOR]

Debug dengan mempertimbangkan:
- Tenant context isolation
- RBAC permissions
- Data relationships
```

**3. Generate Similar App**
```
Task: Generate aplikasi [NEW_DOMAIN] menggunakan pattern 
dari Kiosk POS (lihat .instruction/)

Base patterns to follow:
- Multi-tenant architecture (03-RBAC-MULTI-TENANT.md)
- Module structure (05-MODULES.md)
- Tech stack (02-TECH-STACK.md)

Adaptations needed:
- Business domain: POS → [NEW_DOMAIN]
- Modules: [OLD_MODULES] → [NEW_MODULES]
- Entities: [OLD_ENTITIES] → [NEW_ENTITIES]

Keep:
- RBAC implementation
- Tenant isolation patterns
- API structure
- Docker setup
```

---

## Maintenance

### Updating Documentation

**When to update**:
- ✅ Major architectural changes
- ✅ New modules added
- ✅ Database schema changes
- ✅ Technology stack updates
- ✅ RBAC policy changes

**How to update**:
1. Identify affected document(s)
2. Update content with clear change notes
3. Update version/date at document footer
4. Commit with descriptive message:
   ```bash
   git commit -m "docs: Update .instruction/[FILE] - [CHANGE_SUMMARY]"
   ```

### Version History
Track major changes:
```
v2.0 - 2026-01-04: Added product role feature for Buy X Get Y
v1.0 - 2026-01-01: Initial documentation structure
```

---

## File Relationships

```
README.md (you are here)
├── 00-OVERVIEW.md ────────────► High-level context
├── 01-ARCHITECTURE.md ────────► System design
│   ├── References: 02-TECH-STACK.md
│   └── References: 03-RBAC-MULTI-TENANT.md
├── 02-TECH-STACK.md ──────────► Technologies used
├── 03-RBAC-MULTI-TENANT.md ───► Core concepts
│   └── References: 04-DATABASE-SCHEMA.md
├── 04-DATABASE-SCHEMA.md ─────► Data structure
│   └── Referenced by: 05-MODULES.md
└── 05-MODULES.md ─────────────► Features & APIs
    └── References: 03, 04
```

---

## Best Practices for LLM Interaction

### 1. Provide Context
❌ Bad:
```
"Buatkan fitur product management"
```

✅ Good:
```
"Berdasarkan architecture di .instruction/01-ARCHITECTURE.md dan 
module structure di .instruction/05-MODULES.md, buatkan fitur 
product management dengan tenant isolation"
```

### 2. Reference Specific Patterns
❌ Bad:
```
"Add authentication"
```

✅ Good:
```
"Add authentication menggunakan RBAC pattern yang dijelaskan di 
.instruction/03-RBAC-MULTI-TENANT.md, dengan support untuk 
role: owner, manager, cashier"
```

### 3. Specify Constraints
✅ Include:
- Tenant isolation requirements
- RBAC permission needs
- Database relationships (from schema)
- Module dependencies
- Technology stack limitations

### 4. Iterative Refinement
```
1st prompt: "Overview fitur X berdasarkan .instruction/"
2nd prompt: "Detail implementasi dengan contoh code"
3rd prompt: "Add error handling sesuai pattern yang ada"
```

---

## Contributing

### Adding New Instruction Files

**When to add new file**:
- New major concept introduced (e.g., real-time sync, reporting engine)
- Existing file becomes too large (>1000 lines)
- Separate concern needs detailed explanation

**Naming convention**:
```
[NUMBER]-[TOPIC-NAME].md

Examples:
06-API-DESIGN.md
07-DEPLOYMENT.md
08-TESTING-STRATEGY.md
```

**Template structure**:
```markdown
# [TOPIC NAME]

## Overview
Brief introduction

## Key Concepts
Main ideas

## Implementation Details
Technical specifics

## Code Examples
Real code snippets

## Best Practices
Guidelines

## Common Issues & Solutions
Troubleshooting

## References
Links to related docs

---
**Last Updated**: [DATE]
**Version**: [VERSION]
```

---

## External Resources

- **Main README**: `../README.md` - Setup & quickstart
- **API Documentation**: `../markdown/` - Specific API guides
- **Feature Docs**: `../PRODUCT_FEATURE.md`, `../PROMOTION_ENGINE_DOCUMENTATION.md`
- **Testing**: `../MULTI_TENANT_TESTING.md`, `../USER_TESTING_GUIDE.md`

---

## Feedback & Improvements

Dokumentasi ini adalah living document. Jika ada:
- ❓ Bagian yang kurang jelas
- 📝 Informasi yang perlu ditambahkan
- 🐛 Error atau kesalahan
- 💡 Saran improvement

Silakan update atau buat issue untuk tracking.

---

**Created**: January 4, 2026
**Last Updated**: January 4, 2026
**Maintainer**: Development Team
**Purpose**: LLM Context & Application Template
