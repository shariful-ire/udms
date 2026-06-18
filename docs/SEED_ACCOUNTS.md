# UDMS — Seed Accounts

These accounts are created by `scripts/seed_db.py` for development and testing.

## Default Accounts

| Role | Username | Email | Password |
|---|---|---|---|
| **Provost** | `provost` | `provost@udms.edu` | `Admin@1234!` |
| **Dining Manager** | `diningmgr` | `diningmgr@udms.edu` | `Manager@1234!` |
| **Customer** (enrolled student) | `student_customer` | `customer@udms.edu` | `Student@1234!` |
| **Student** (not enrolled) | `student_normal` | `student@udms.edu` | `Student@1234!` |

Additionally, **20 random student accounts** are seeded with:
- Usernames: `student_001` through `student_020`
- Password: `Student@1234!`
- Mix of CUSTOMER and NON_CUSTOMER roles

---

## Seeded Data

| Entity | Amount |
|---|---|
| Meal records | 90 days of history for all CUSTOMER accounts |
| Expenses | 30 days of dining hall expenses across all categories |
| Meal requests | 10 sample requests in various statuses |
| System settings | Default meal rate, deadlines, security config |
| Meal schedules | Breakfast, Lunch, Dinner with default serving hours |

---

## Resetting Seed Data

```bash
# Drop and re-seed (warning: destroys all data)
docker compose exec api alembic downgrade base
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed_db.py
```

---

## Notes

- All seed accounts have `is_email_verified = True`
- All seed accounts have `status = ACTIVE`
- The Provost account cannot be deleted or demoted
- The seed script is idempotent — safe to run multiple times
