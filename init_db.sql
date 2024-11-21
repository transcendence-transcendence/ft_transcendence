DO $$ BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ft_transcendence') THEN
        CREATE DATABASE ft_transcendence;
    END IF;
END $$;
