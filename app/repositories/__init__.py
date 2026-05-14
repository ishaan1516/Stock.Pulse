def __init__(self):
    s = get_settings()
    # Use service key for writes, anon key for reads
    self.client = create_client(s.SUPABASE_URL, s.SUPABASE_SERVICE_KEY or s.SUPABASE_KEY)