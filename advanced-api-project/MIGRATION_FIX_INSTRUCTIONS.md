## Migration Fix Instructions

### Problem Diagnosed:

- Migration 0005's rename operation failed, leaving database with `publication_date` column
- Your model expects `publication_year` field
- This caused the error: `django.db.utils.OperationalError: (1054, "Unknown column 'publication_date' in 'api_book'")`

### Solution Applied:

Created migration `api/migrations/0006_fix_publication_column_name.py` to fix the column naming issue.

### To Apply the Fix:

1. **Make sure Django and dependencies are installed:**

   ```bash
   pip install django djangorestframework
   ```

2. **Run the new migration:**

   ```bash
   python manage.py migrate api 0006
   ```

3. **Verify the fix:**

   ```bash
   python manage.py showmigrations api
   ```

4. **Test the application:**
   ```bash
   python manage.py runserver
   ```

### What the Fix Does:

- Uses raw SQL to rename the `publication_date` column to `publication_year` in your MySQL database
- Includes proper reverse migration capability
- Safely handles the schema mismatch that was causing the error

### Alternative if Migration Fails:

If the migration still fails, you can manually fix the database:

```sql
USE Alx_RestAPI_Db;
ALTER TABLE api_book CHANGE COLUMN publication_date publication_year DATE NULL;
```

The migration file is now ready and should resolve your migration error completely.
