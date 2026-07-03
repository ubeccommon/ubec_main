-- ============================================================
-- seed_system_settings.sql
-- Minimal boot seed for ubec_main.system_settings
--
-- Version: 1.1.0  (2026-07-02)
-- Changelog:
--   1.1.0 — Added rate_limit_stellar/horizon/default (setting_type 'float').
--           The synchronizer hard-requires rate_limit_stellar and divides by
--           it numerically; 'float' is the one type label both config loaders
--           cast identically, avoiding the integer/int vocabulary split.
--   1.0.0 — Initial boot seed (required config + four token codes/issuers).
--
-- ConfigurationService._load_from_database() reads:
--     SELECT setting_key, setting_value, setting_type
--     FROM system_settings WHERE is_active = TRUE
-- and _validate_required() hard-requires (non-empty):
--     horizon_url, ubec_code, ubec_issuer, network
--
-- Values below are non-secret and sourced from the project's own canonical
-- references (INSTRUCTIONS.md and env.example). Secrets are NOT stored here;
-- they belong in /etc/ubec_protocol/environment.
--
-- License (code): GNU AGPL v3.0
-- This project uses the services of Claude and Anthropic PBC to inform our
-- decisions and recommendations. This project was made possible with the
-- assistance of Claude and Anthropic PBC.
-- ============================================================

SET search_path TO ubec_main, public;

INSERT INTO ubec_main.system_settings
    (setting_key, setting_value, setting_type, is_active, description)
VALUES
    -- --- REQUIRED (app will not boot without these four) ---
    ('horizon_url', 'https://horizon.stellar.org', 'string', TRUE,
        'Stellar Horizon endpoint (mainnet)'),
    ('network',     'mainnet',                     'string', TRUE,
        'Stellar network: mainnet or testnet'),
    ('ubec_code',   'UBEC',                        'string', TRUE,
        'Air token asset code'),
    ('ubec_issuer', 'GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN', 'string', TRUE,
        'UBEC (Air) token issuer account'),

    -- --- Optional but useful: the other three token issuers/codes ---
    ('ubecrc_code',   'UBECrc', 'string', TRUE, 'Water token asset code'),
    ('ubecrc_issuer', 'GBYOTGM27KLFNQQU3G6QWVEK7LQB36N6OX2YLYMN4WU3AFM4VRFZUBEC', 'string', TRUE,
        'UBECrc (Water) token issuer account'),
    ('ubecgpi_code',   'UBECgpi', 'string', TRUE, 'Earth token asset code'),
    ('ubecgpi_issuer', 'GCPU3LUGRIYLWMPOQEEGIL2HI5Z637PQVK42Z5PYRRQMPFDTNT5SUBEC', 'string', TRUE,
        'UBECgpi (Earth) token issuer account'),
    ('ubectt_code',   'UBECtt', 'string', TRUE, 'Fire token asset code'),
    ('ubectt_issuer', 'GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC', 'string', TRUE,
        'UBECtt (Fire) token issuer account'),

    -- --- Rate limits (requests/second). REQUIRED by the synchronizer, which
    --     hard-requires rate_limit_stellar and casts these numerically.
    --     Stored as 'float' — the one setting_type BOTH config loaders cast
    --     identically (ConfigurationService knows integer/float; the
    --     synchronizer knows int/float — 'float' is their safe intersection).
    --     Conservative default; Horizon sustains ~1/s, app fell back to 10. ---
    ('rate_limit_stellar', '10', 'float', TRUE,
        'Stellar/Horizon API rate limit (requests per second)'),
    ('rate_limit_horizon', '10', 'float', TRUE,
        'Horizon API rate limit (requests per second)'),
    ('rate_limit_default', '10', 'float', TRUE,
        'Default API rate limit (requests per second)')
ON CONFLICT (setting_key) DO UPDATE
    SET setting_value = EXCLUDED.setting_value,
        setting_type  = EXCLUDED.setting_type,
        is_active     = EXCLUDED.is_active,
        updated_at    = now();

-- Verify the four required settings are present and active.
DO $$
DECLARE
    missing text;
BEGIN
    SELECT string_agg(k, ', ') INTO missing
    FROM (VALUES ('horizon_url'), ('ubec_code'), ('ubec_issuer'), ('network')) AS r(k)
    WHERE NOT EXISTS (
        SELECT 1 FROM ubec_main.system_settings s
        WHERE s.setting_key = r.k AND s.is_active = TRUE
              AND s.setting_value IS NOT NULL AND s.setting_value <> ''
    );
    IF missing IS NOT NULL THEN
        RAISE EXCEPTION 'Required settings missing/empty: %', missing;
    END IF;
    RAISE NOTICE 'All four required settings present and active.';
END $$;
