#!/bin/bash
# Backfill existing data after migration
# Run this after applying 001_add_multi_tenancy.sql

echo "ACQUISITOR Database Backfill Script"
echo "=================================="
echo ""

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL environment variable not set"
    echo "   Set it with: export DATABASE_URL=postgresql://..."
    exit 1
fi

echo "This script will backfill user_id for existing leads."
echo ""
echo "Options:"
echo "1. Assign all existing leads to a specific user (by email)"
echo "2. Delete all existing leads (clean slate)"
echo "3. Exit without changes"
echo ""
read -p "Choose option (1-3): " choice

case $choice in
    1)
        read -p "Enter admin user email: " email
        
        echo "Backfilling leads to user: $email..."
        
        psql $DATABASE_URL << EOF
-- Get user ID
DO \$\$
DECLARE
    admin_id UUID;
    lead_count INTEGER;
BEGIN
    SELECT id INTO admin_id FROM users WHERE email = '$email';
    
    IF admin_id IS NULL THEN
        RAISE EXCEPTION 'User with email % not found', '$email';
    END IF;
    
    UPDATE leads SET user_id = admin_id WHERE user_id IS NULL;
    
    GET DIAGNOSTICS lead_count = ROW_COUNT;
    
    RAISE NOTICE 'Assigned % leads to user %', lead_count, '$email';
END \$\$;
EOF
        
        echo "✅ Backfill complete"
        ;;
        
    2)
        echo "⚠️  WARNING: This will DELETE all existing leads!"
        read -p "Type 'DELETE' to confirm: " confirm
        
        if [ "$confirm" = "DELETE" ]; then
            psql $DATABASE_URL -c "DELETE FROM leads WHERE user_id IS NULL;"
            echo "✅ Orphaned leads deleted"
        else
            echo "❌ Cancelled"
        fi
        ;;
        
    3)
        echo "Exiting without changes"
        exit 0
        ;;
        
    *)
        echo "Invalid option"
        exit 1
        ;;
esac
