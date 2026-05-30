-- =====================================================
-- Pine Vision Language Model Application
-- Supabase PostgreSQL Schema
-- =====================================================

CREATE TABLE IF NOT EXISTS public.user_activity (
    user_name TEXT NOT NULL,
    mode TEXT NOT NULL,
    question TEXT,
    response TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.user_activity ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow inserts from app"
ON public.user_activity
FOR INSERT
TO anon
WITH CHECK (TRUE);

CREATE POLICY "Allow read in dashboard"
ON public.user_activity
FOR SELECT
TO anon
USING (TRUE);