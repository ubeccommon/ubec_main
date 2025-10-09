--
-- PostgreSQL database dump
--

-- Dumped from database version 15.12 (Debian 15.12-0+deb12u2)
-- Dumped by pg_dump version 15.12 (Debian 15.12-0+deb12u2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: ubec_recipro; Type: SCHEMA; Schema: -; Owner: recipro
--

CREATE SCHEMA ubec_recipro;


ALTER SCHEMA ubec_recipro OWNER TO recipro;

--
-- Name: SCHEMA ubec_recipro; Type: COMMENT; Schema: -; Owner: recipro
--

COMMENT ON SCHEMA ubec_recipro IS 'Schema for UBEC Reciprocity Token system';


--
-- Name: hstore; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS hstore WITH SCHEMA ubec_recipro;


--
-- Name: EXTENSION hstore; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION hstore IS 'data type for storing sets of (key, value) pairs';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA ubec_recipro;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: analyze_asset_holders(character varying, character varying); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.analyze_asset_holders(asset_code_param character varying, asset_issuer_param character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    total_holders INTEGER;
    active_holders INTEGER;
    new_holders INTEGER;
    whale_percent DECIMAL(5,2);
    total_supply DECIMAL(18,8);
    whale_threshold DECIMAL(18,8);
    whale_holdings DECIMAL(18,8);
    gini DECIMAL(5,4);
    sum_balances DECIMAL(18,8);
BEGIN
    -- Get total holders
    SELECT COUNT(*) INTO total_holders
    FROM asset_holders
    WHERE asset_code = asset_code_param
    AND asset_issuer = asset_issuer_param;
    
    -- Get active holders (had activity in last 30 days)
    SELECT COUNT(*) INTO active_holders
    FROM asset_holders ah
    JOIN participants p ON ah.account_id = p.account_id
    WHERE ah.asset_code = asset_code_param
    AND ah.asset_issuer = asset_issuer_param
    AND p.last_activity_at > NOW() - INTERVAL '30 days';
    
    -- Get new holders (joined in last 30 days)
    SELECT COUNT(*) INTO new_holders
    FROM asset_holders ah
    JOIN participants p ON ah.account_id = p.account_id
    WHERE ah.asset_code = asset_code_param
    AND ah.asset_issuer = asset_issuer_param
    AND p.joined_at > NOW() - INTERVAL '30 days';
    
    -- Get total supply
    SELECT COALESCE(SUM(balance), 0) INTO total_supply
    FROM asset_holders
    WHERE asset_code = asset_code_param
    AND asset_issuer = asset_issuer_param;
    
    -- Set whale threshold at 5% of total supply
    whale_threshold := total_supply * 0.05;
    
    -- Update classifications based on balances
    UPDATE asset_holders
    SET classification = 
        CASE 
            WHEN balance >= whale_threshold THEN 'whale'
            WHEN balance > 0 THEN 'retail'
            ELSE 'inactive'
        END,
    is_active = (balance > 0)
    WHERE asset_code = asset_code_param
    AND asset_issuer = asset_issuer_param;
    
    -- Get whale concentration percentage
    SELECT COALESCE(SUM(balance) / NULLIF(total_supply, 0) * 100, 0) INTO whale_percent
    FROM asset_holders
    WHERE asset_code = asset_code_param
    AND asset_issuer = asset_issuer_param
    AND balance >= whale_threshold;
    
    -- Calculate Gini coefficient for wealth distribution
    -- Using alternative approach that doesn't mix window and aggregate functions
    IF total_holders > 1 THEN
        -- Calculate Gini using a different method - approximate with a two-step approach
        -- First, get the sum of all balances
        SELECT SUM(balance) INTO sum_balances
        FROM asset_holders
        WHERE asset_code = asset_code_param
        AND asset_issuer = asset_issuer_param
        AND balance > 0;
        
        -- Then calculate Gini using a cursor-based approach
        DECLARE
            total_cumulative DECIMAL(18,8) := 0;
            pos INTEGER := 0;
            balance_record RECORD;
            cumulative_balances DECIMAL(18,8) := 0;
        BEGIN
            -- Compute cumulative balances using a cursor instead of window functions
            FOR balance_record IN
                SELECT balance
                FROM asset_holders
                WHERE asset_code = asset_code_param
                AND asset_issuer = asset_issuer_param
                AND balance > 0
                ORDER BY balance
            LOOP
                pos := pos + 1;
                cumulative_balances := cumulative_balances + (pos - 0.5) * balance_record.balance;
            END LOOP;
            
            -- Calculate Gini coefficient
            gini := 1 - (2 * cumulative_balances / (total_holders * sum_balances));
        END;
    ELSE
        gini := 0; -- If there's only one holder or none, Gini is 0
    END IF;
    
    -- Insert asset holder analysis
    INSERT INTO asset_holder_analysis (
        analysis_date,
        asset_code,
        asset_issuer,
        total_holders,
        total_supply,
        active_holders,
        new_holders_last_30_days,
        whale_concentration_percent,
        gini_coefficient,
        distribution_metrics
    ) VALUES (
        NOW(),
        asset_code_param,
        asset_issuer_param,
        total_holders,
        total_supply,
        active_holders,
        new_holders,
        whale_percent,
        gini,
        jsonb_build_object(
            'whale_threshold', whale_threshold,
            'whale_count', (SELECT COUNT(*) FROM asset_holders WHERE asset_code = asset_code_param AND asset_issuer = asset_issuer_param AND balance >= whale_threshold),
            'retail_count', (SELECT COUNT(*) FROM asset_holders WHERE asset_code = asset_code_param AND asset_issuer = asset_issuer_param AND balance > 0 AND balance < whale_threshold),
            'inactive_count', (SELECT COUNT(*) FROM asset_holders WHERE asset_code = asset_code_param AND asset_issuer = asset_issuer_param AND balance = 0),
            'top_10_percent_holdings', (
                SELECT SUM(balance) / total_supply * 100
                FROM (
                    SELECT balance
                    FROM asset_holders
                    WHERE asset_code = asset_code_param
                    AND asset_issuer = asset_issuer_param
                    ORDER BY balance DESC
                    LIMIT (total_holders / 10)
                ) AS top_10
            )
        )
    );
    
    RETURN total_holders;
END;
$$;


ALTER FUNCTION ubec_recipro.analyze_asset_holders(asset_code_param character varying, asset_issuer_param character varying) OWNER TO recipro;

--
-- Name: apply_daily_reciprocity_decay(); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.apply_daily_reciprocity_decay() RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    decay_rate DECIMAL(10,8);
    updated_count INTEGER := 0;
BEGIN
    -- Get decay rate from system configuration
    SELECT CAST(parameter_value AS DECIMAL(10,8)) INTO decay_rate
    FROM system_configuration 
    WHERE parameter_name = 'reciprocity_decay_rate';
    
    -- Apply decay to all agents with positive reciprocity score
    UPDATE agents
    SET reciprocity_score = reciprocity_score * (1 - decay_rate)
    WHERE reciprocity_score > 0;
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    
    -- Record the decay in reciprocity_scores table for tracking
    INSERT INTO reciprocity_scores (
        agent_id,
        participant_id,
        score_value,
        previous_score,
        reason,
        score_component
    )
    SELECT 
        a.id,
        a.participant_id,
        a.reciprocity_score,
        a.reciprocity_score / (1 - decay_rate),
        'Daily decay applied',
        json_build_object(
            'decay_rate', decay_rate,
            'decay_date', NOW()::date
        )
    FROM agents a
    WHERE a.reciprocity_score > 0;
    
    RETURN updated_count;
END;
$$;


ALTER FUNCTION ubec_recipro.apply_daily_reciprocity_decay() OWNER TO recipro;

--
-- Name: audit_table_change(); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.audit_table_change() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO ubec_recipro.audit_log(operation_type, performed_by, details)
    VALUES (
        TG_OP, 
        current_user, 
        jsonb_build_object('table', TG_TABLE_NAME, 'old_data', row_to_json(OLD), 'new_data', row_to_json(NEW))
    );
    RETURN NULL;
END;
$$;


ALTER FUNCTION ubec_recipro.audit_table_change() OWNER TO recipro;

--
-- Name: calculate_agent_reputation(character varying); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.calculate_agent_reputation(agent_id_param character varying) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    agent_record RECORD;
    new_score DECIMAL(18,8);
    activity_score DECIMAL(18,8);
    contribution_score DECIMAL(18,8);
    benefit_score DECIMAL(18,8);
    longevity_factor DECIMAL(10,2);
BEGIN
    -- Get the agent record
    SELECT 
        a.id, 
        a.reputation_score,
        p.joined_at,
        p.total_activity_count
    INTO agent_record 
    FROM agents a
    JOIN participants p ON a.participant_id = p.id
    WHERE a.agent_id = agent_id_param;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Agent with ID % not found', agent_id_param;
    END IF;
    
    -- Calculate activity component - based on total activity and recent activity ratio
    SELECT COALESCE(COUNT(*), 0) INTO activity_score
    FROM agent_activity_history
    WHERE agent_id = agent_record.id
    AND timestamp > extract(epoch from (NOW() - INTERVAL '30 days'));
    
    activity_score := LEAST(activity_score / 10, 10); -- Cap at 10
    
    -- Calculate contribution component - based on contribution amount
    SELECT COALESCE(SUM(amount), 0) INTO contribution_score
    FROM agent_contribution_history
    WHERE agent_id = agent_record.id;
    
    contribution_score := LEAST(contribution_score / 100, 10); -- Cap at 10
    
    -- Calculate benefit component - negative impact for excessive benefits
    SELECT COALESCE(SUM(amount), 0) INTO benefit_score
    FROM agent_benefit_history
    WHERE agent_id = agent_record.id;
    
    benefit_score := LEAST(benefit_score / 200, 5); -- Cap at 5
    
    -- Calculate longevity factor - rewards longer participation
    longevity_factor := LEAST(
        EXTRACT(EPOCH FROM (NOW() - agent_record.joined_at)) / (60 * 60 * 24 * 30), -- Months as participant
        5
    );
    
    -- Calculate final score - weighted combination of components
    new_score := (
        activity_score * 0.3 +
        contribution_score * 0.4 +
        longevity_factor * 0.3 -
        benefit_score * 0.1
    ) * 10; -- Scale to 0-100 range
    
    -- Ensure score is never negative
    new_score := GREATEST(new_score, 0);
    
    -- Update agent's reputation score
    UPDATE agents
    SET reputation_score = new_score
    WHERE id = agent_record.id;
    
    RETURN new_score;
END;
$$;


ALTER FUNCTION ubec_recipro.calculate_agent_reputation(agent_id_param character varying) OWNER TO recipro;

--
-- Name: calculate_holonic_scores(integer); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.calculate_holonic_scores(agent_id_param integer) RETURNS TABLE(agent_id integer, autonomy_score numeric, multi_scale_score numeric, regenerative_score numeric, network_score numeric, ubuntu_score numeric, composite_score numeric, category character varying)
    LANGUAGE plpgsql
    AS $$
DECLARE
    autonomy DECIMAL(5,4);
    multi_scale DECIMAL(5,4);
    regenerative DECIMAL(5,4);
    network DECIMAL(5,4);
    ubuntu DECIMAL(5,4);
    composite DECIMAL(5,4);
    category VARCHAR(50);
    
    -- Variables for calculation
    holding_period INTEGER;
    transaction_count INTEGER;
    balance_stability DECIMAL(5,4);
    network_integration DECIMAL(5,4);
    local_participation INTEGER;
    regional_participation INTEGER;
    global_participation INTEGER;
    impact_project_count INTEGER;
    connector_score DECIMAL(10,8);
    reciprocity_ratio DECIMAL(5,4);
    community_support DECIMAL(5,4);
BEGIN
    -- 1. Calculate Autonomy and Integration Score
    -- Get transaction history statistics
    SELECT 
        COUNT(*),
        COALESCE(1.0 - VARIANCE(rcl.amount)/NULLIF(AVG(rcl.amount), 0)^2, 0.5)::DECIMAL(5,4)
    INTO
        transaction_count,
        balance_stability
    FROM ubec_recipro.rc_ledger rcl
    WHERE rcl.agent_id = agent_id_param
    AND rcl.timestamp > extract(epoch from (now() - INTERVAL '90 days'));
    
    -- Get network position (placeholder - would be based on actual network analysis)
    network_integration := COALESCE(
        (SELECT COUNT(*) FROM ubec_recipro.participant_relationships 
         WHERE agent_id = agent_id_param)::DECIMAL / 100, 
        0.1
    );
    
    -- Calculate autonomy integration score
    autonomy := LEAST(
        (0.25 * LEAST(transaction_count / 10, 1.0) + 
         0.25 * LEAST(balance_stability, 1.0) + 
         0.25 * network_integration + 
         0.25 * LEAST(EXTRACT(DAY FROM now() - p.joined_at) / 180, 1.0))::DECIMAL(5,4),
        1.0
    );
    
    -- 2. Calculate Multi-scale Participation Score
    -- Counts of participation at different levels
    local_participation := COALESCE(
        (SELECT COUNT(*) FROM ubec_recipro.agent_activity_history aah
         WHERE aah.agent_id = agent_id_param 
         AND aah.activity_type = 'LOCAL_INTERACTION'),
        0
    );
    
    regional_participation := COALESCE(
        (SELECT COUNT(*) FROM ubec_recipro.agent_activity_history aah
         WHERE aah.agent_id = agent_id_param 
         AND aah.activity_type = 'REGIONAL_INTERACTION'),
        0
    );
    
    global_participation := COALESCE(
        (SELECT COUNT(*) FROM ubec_recipro.agent_activity_history aah
         WHERE aah.agent_id = agent_id_param 
         AND aah.activity_type = 'GLOBAL_INTERACTION'),
        0
    );
    
    -- Calculate multi-scale score
    multi_scale := LEAST(
        (0.3 * LEAST(local_participation / 10.0, 1.0) +
         0.3 * LEAST(regional_participation / 5.0, 1.0) +
         0.3 * LEAST(global_participation / 2.0, 1.0) +
         0.1 * LEAST((local_participation + regional_participation + global_participation) / 20.0, 1.0))::DECIMAL(5,4),
        1.0
    );
    
    -- 3. Calculate Regenerative Impact Score
    -- Count impact projects (placeholder - would be based on actual data)
    impact_project_count := COALESCE(
        (SELECT COUNT(*) FROM ubec_recipro.regenerative_projects rp
         WHERE rp.agent_id = agent_id_param),
        0
    );
    
    -- Calculate impact score
    regenerative := LEAST(
        (0.4 * LEAST(impact_project_count / 1.0, 1.0) +
         0.4 * LEAST(a.reciprocity_score / 100.0, 1.0) +
         0.2 * LEAST(a.reputation_score / 100.0, 1.0))::DECIMAL(5,4),
        1.0
    );
    
    -- 4. Calculate Network Contribution Score
    -- Connector score (placeholder - would be based on betweenness centrality)
    connector_score := COALESCE(
        (SELECT 0.3 * COUNT(*) FROM ubec_recipro.agent_contribution_history ach
         WHERE ach.agent_id = agent_id_param) / 
        NULLIF((SELECT COUNT(*) FROM ubec_recipro.agents), 0),
        0.1
    );
    
    -- Calculate network score
    network := LEAST(
        (0.4 * LEAST(connector_score / 0.3, 1.0) +
         0.3 * LEAST(transaction_count / 10.0, 1.0) +
         0.2 * LEAST(a.reciprocity_credits / 1000.0, 1.0) +
         0.1 * LEAST(a.reputation_score / 100.0, 1.0))::DECIMAL(5,4),
        1.0
    );
    
    -- 5. Calculate Ubuntu Alignment Score
    -- Calculate reciprocity ratio
    SELECT 
        CASE 
            WHEN COUNT(*) FILTER (WHERE transaction_type = 'CREDIT') > 0 AND 
                 COUNT(*) FILTER (WHERE transaction_type = 'DEBIT') > 0 
            THEN 
                LEAST(
                    COUNT(*) FILTER (WHERE transaction_type = 'CREDIT'),
                    COUNT(*) FILTER (WHERE transaction_type = 'DEBIT')
                )::DECIMAL / 
                GREATEST(
                    COUNT(*) FILTER (WHERE transaction_type = 'CREDIT'),
                    COUNT(*) FILTER (WHERE transaction_type = 'DEBIT')
                )::DECIMAL
            ELSE 0.5
        END
    INTO reciprocity_ratio
    FROM ubec_recipro.rc_ledger rcl
    WHERE rcl.agent_id = agent_id_param;
    
    -- Calculate community support (placeholder - would be based on actual data)
    community_support := COALESCE(
        (SELECT SUM(amount) FROM ubec_recipro.agent_contribution_history
         WHERE agent_id = agent_id_param) / 
        NULLIF(a.reciprocity_credits, 0),
        0.1
    );
    
    -- Calculate ubuntu score
    ubuntu := LEAST(
        (0.4 * LEAST(reciprocity_ratio / 0.8, 1.0) +
         0.4 * LEAST(community_support / 0.1, 1.0) +
         0.2 * LEAST(a.reciprocity_score / 100.0, 1.0))::DECIMAL(5,4),
        1.0
    );
    
    -- Calculate composite score
    composite := ((autonomy + multi_scale + regenerative + network + ubuntu) / 5.0)::DECIMAL(5,4);
    
    -- Determine category
    category := CASE
        WHEN composite >= 0.8 THEN 'Exemplar'
        WHEN composite >= 0.6 THEN 'Integrator'
        WHEN composite >= 0.4 THEN 'Contributor'
        WHEN composite >= 0.2 THEN 'Participant'
        ELSE 'Observer'
    END;
    
    -- Store the results
    INSERT INTO ubec_recipro.holonic_metrics (
        agent_id, 
        autonomy_integration_score, 
        multi_scale_score,
        regenerative_impact_score,
        network_contribution_score,
        ubuntu_alignment_score,
        composite_score,
        holonic_category,
        raw_metrics
    ) VALUES (
        agent_id_param,
        autonomy,
        multi_scale,
        regenerative,
        network,
        ubuntu,
        composite,
        category,
        jsonb_build_object(
            'transaction_count', transaction_count,
            'balance_stability', balance_stability,
            'network_integration', network_integration,
            'local_participation', local_participation,
            'regional_participation', regional_participation,
            'global_participation', global_participation,
            'impact_project_count', impact_project_count,
            'connector_score', connector_score,
            'reciprocity_ratio', reciprocity_ratio,
            'community_support', community_support
        )
    );
    
    -- Return the calculated values
    RETURN QUERY 
        SELECT 
            agent_id_param,
            autonomy,
            multi_scale,
            regenerative,
            network,
            ubuntu,
            composite,
            category;
END;
$$;


ALTER FUNCTION ubec_recipro.calculate_holonic_scores(agent_id_param integer) OWNER TO recipro;

--
-- Name: FUNCTION calculate_holonic_scores(agent_id_param integer); Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON FUNCTION ubec_recipro.calculate_holonic_scores(agent_id_param integer) IS 'Calculates holonic evaluation scores for an agent based on the five holonic principles';


--
-- Name: calculate_reciprocity_weight(character varying, character varying); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.calculate_reciprocity_weight(agent_id_param character varying, action_type character varying DEFAULT 'order'::character varying) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    rc_score DECIMAL(18,8);
    rc_credits DECIMAL(18,8);
    tier_bonus DECIMAL(5,2);
    weight DECIMAL(10,8);
BEGIN
    -- Get agent's reciprocity score and credits
    SELECT 
        a.reciprocity_score,
        a.reciprocity_credits,
        COALESCE(lt.rc_multiplier, 1.0)
    INTO rc_score, rc_credits, tier_bonus
    FROM agents a
    LEFT JOIN loyalty_tiers lt ON a.tier = lt.tier_name
    WHERE a.agent_id = agent_id_param;
    
    IF NOT FOUND THEN
        RETURN 1.0; -- Default weight for unknown agents
    END IF;
    
    -- Calculate base weight based on reciprocity score
    weight := 1.0 + (LEAST(rc_score / 100, 1.0) * 0.5); -- Max 50% boost from score
    
    -- Apply bonus from reciprocity credits - diminishing returns
    weight := weight + (LEAST(SQRT(rc_credits) / 10, 0.5)); -- Max 50% boost from credits
    
    -- Apply tier bonus
    weight := weight * tier_bonus;
    
    -- Apply action-specific adjustments
    CASE action_type
        WHEN 'market_making' THEN
            weight := weight * 1.2; -- Market making gets 20% extra boost
        WHEN 'arbitrage' THEN
            weight := weight * 0.9; -- Arbitrage gets 10% reduction
        WHEN 'rebalance' THEN
            weight := weight * 1.1; -- Rebalancing gets 10% boost
        ELSE
            -- Default case (orders) - no adjustment
    END CASE;
    
    -- Ensure weight is at least 1.0
    RETURN GREATEST(weight, 1.0);
END;
$$;


ALTER FUNCTION ubec_recipro.calculate_reciprocity_weight(agent_id_param character varying, action_type character varying) OWNER TO recipro;

--
-- Name: calculate_token_allocation(numeric, numeric, character varying); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.calculate_token_allocation(base_amount numeric, reciprocity_score numeric, tier character varying DEFAULT 'STANDARD'::character varying) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    multiplier DECIMAL(5,4);
    tier_multiplier DECIMAL(5,2);
    result DECIMAL(18,8);
BEGIN
    -- Get tier multiplier
    SELECT COALESCE(rc_multiplier, 1.0) INTO tier_multiplier
    FROM loyalty_tiers
    WHERE tier_name = tier;
    
    -- Calculate multiplier based on reciprocity score
    -- 1.0 is baseline, can go up to 2.0 for high scores
    multiplier := 1.0 + (LEAST(reciprocity_score / 1000, 1.0) * 0.5); -- Max 50% boost from score
    
    -- Calculate final allocation
    result := base_amount * multiplier;
    
    RETURN result;
END;
$$;


ALTER FUNCTION ubec_recipro.calculate_token_allocation(base_amount numeric, reciprocity_score numeric, tier character varying) OWNER TO recipro;

--
-- Name: calculate_vesting_period(integer); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.calculate_vesting_period(participant_id integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    vesting_days INTEGER;
BEGIN
    -- Get vesting period from loyalty tier
    SELECT lt.vesting_period_days INTO vesting_days
    FROM participant_tiers pt
    JOIN loyalty_tiers lt ON pt.tier_id = lt.id
    WHERE pt.participant_id = calculate_vesting_period.participant_id
    AND (pt.valid_until IS NULL OR pt.valid_until > NOW())
    ORDER BY pt.assigned_at DESC
    LIMIT 1;
    
    -- Default to 90 days if no tier found
    IF vesting_days IS NULL THEN
        vesting_days := 90;
    END IF;
    
    RETURN vesting_days;
END;
$$;


ALTER FUNCTION ubec_recipro.calculate_vesting_period(participant_id integer) OWNER TO recipro;

--
-- Name: check_api_rate_limit(character varying, integer, integer, integer); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.check_api_rate_limit(endpoint_name character varying, header_limit integer, header_remaining integer, header_reset integer) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
    can_proceed BOOLEAN;
    current_reset TIMESTAMP WITHOUT TIME ZONE;
BEGIN
    -- Get current reset time
    SELECT reset_time INTO current_reset
    FROM ubec_recipro.api_rate_limits
    WHERE endpoint = endpoint_name;
    
    -- Update rate limit information if reset time has passed or new information is provided
    IF current_reset IS NULL OR current_reset <= now() OR header_remaining IS NOT NULL THEN
        UPDATE ubec_recipro.api_rate_limits 
        SET 
            hourly_limit = COALESCE(header_limit, hourly_limit),
            remaining_calls = COALESCE(header_remaining, hourly_limit),
            reset_time = CASE 
                WHEN header_reset IS NOT NULL THEN now() + (header_reset * INTERVAL '1 second')
                WHEN current_reset <= now() THEN now() + INTERVAL '1 hour'
                ELSE reset_time
            END,
            last_updated = now()
        WHERE endpoint = endpoint_name;
    END IF;
    
    -- Check if we can proceed
    SELECT remaining_calls > 5 INTO can_proceed
    FROM ubec_recipro.api_rate_limits
    WHERE endpoint = endpoint_name;
    
    RETURN can_proceed;
END;
$$;


ALTER FUNCTION ubec_recipro.check_api_rate_limit(endpoint_name character varying, header_limit integer, header_remaining integer, header_reset integer) OWNER TO recipro;

--
-- Name: FUNCTION check_api_rate_limit(endpoint_name character varying, header_limit integer, header_remaining integer, header_reset integer); Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON FUNCTION ubec_recipro.check_api_rate_limit(endpoint_name character varying, header_limit integer, header_remaining integer, header_reset integer) IS 'Checks and updates API rate limits, returning true if API calls can proceed';


--
-- Name: check_distribution_balance(character varying, character varying); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.check_distribution_balance(asset_code_param character varying, asset_issuer_param character varying) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
        DECLARE
            needs_rebalance BOOLEAN;
            general_address VARCHAR;
            admin_address VARCHAR;
            general_balance DECIMAL(18,8);
            admin_balance DECIMAL(18,8);
            steward_balance DECIMAL(18,8);
            admin_target DECIMAL(18,8);
            steward_target DECIMAL(18,8);
            admin_diff DECIMAL(18,8);
            steward_diff DECIMAL(18,8);
            threshold DECIMAL(5,4) := 0.01; -- 1% threshold
            total_supply DECIMAL(18,8);
        BEGIN
            -- Get addresses from system configuration
            SELECT parameter_value INTO general_address
            FROM system_configuration 
            WHERE parameter_name = 'general_distribution_address';
            
            SELECT parameter_value INTO admin_address
            FROM system_configuration 
            WHERE parameter_name = 'administration_address';
            
            -- Get total supply
            SELECT total_supply INTO total_supply
            FROM asset_holder_analysis
            WHERE asset_code = asset_code_param 
            AND asset_issuer = asset_issuer_param
            ORDER BY analysis_date DESC
            LIMIT 1;
            
            -- Get current balances
            SELECT balance INTO general_balance
            FROM asset_holders
            WHERE account_id = general_address
            AND asset_code = asset_code_param
            AND asset_issuer = asset_issuer_param;
            
            SELECT balance INTO admin_balance
            FROM asset_holders
            WHERE account_id = admin_address
            AND asset_code = asset_code_param
            AND asset_issuer = asset_issuer_param;
            
            -- Get stewardship balance (multiple accounts)
            SELECT SUM(balance) INTO steward_balance
            FROM asset_holders ah
            JOIN participants p ON ah.account_id = p.account_id
            WHERE p.account_type = 'stewardship'
            AND ah.asset_code = asset_code_param
            AND ah.asset_issuer = asset_issuer_param;
            
            -- Get target percentages
            SELECT CAST(parameter_value AS DECIMAL(5,4)) INTO admin_target
            FROM system_configuration 
            WHERE parameter_name = 'admin_target_percentage';
            
            SELECT CAST(parameter_value AS DECIMAL(5,4)) INTO steward_target
            FROM system_configuration 
            WHERE parameter_name = 'stewardship_target_percentage';
            
            -- Calculate differences
            admin_diff := ABS(admin_balance / total_supply - admin_target);
            steward_diff := ABS(steward_balance / total_supply - steward_target);
            
            -- Determine if rebalance is needed
            needs_rebalance := (admin_diff > threshold OR steward_diff > threshold);
            
            -- Record check in history
            INSERT INTO distribution_history (
                check_date, asset_code, asset_issuer,
                general_balance, admin_balance, stewardship_balance,
                rebalance_needed, details
            ) VALUES (
                NOW(), asset_code_param, asset_issuer_param,
                general_balance, admin_balance, steward_balance,
                needs_rebalance,
                jsonb_build_object(
                    'admin_percentage', admin_balance / total_supply,
                    'steward_percentage', steward_balance / total_supply,
                    'admin_target', admin_target,
                    'steward_target', steward_target,
                    'admin_diff', admin_diff,
                    'steward_diff', steward_diff,
                    'threshold', threshold
                )
            );
            
            RETURN needs_rebalance;
        END;
        $$;


ALTER FUNCTION ubec_recipro.check_distribution_balance(asset_code_param character varying, asset_issuer_param character varying) OWNER TO recipro;

--
-- Name: create_scheduler_tables(); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.create_scheduler_tables() RETURNS void
    LANGUAGE plpgsql
    AS $_$
BEGIN
    -- Create scheduler tables if they don't exist
    CREATE TABLE IF NOT EXISTS scheduler_jobs (
        id SERIAL PRIMARY KEY,
        job_name VARCHAR(100) NOT NULL,
        schedule_interval INTERVAL NOT NULL,
        last_run TIMESTAMP,
        next_run TIMESTAMP NOT NULL,
        enabled BOOLEAN DEFAULT TRUE,
        job_function TEXT NOT NULL,
        parameters JSONB,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        UNIQUE(job_name)
    );
    
    CREATE TABLE IF NOT EXISTS scheduler_job_history (
        id SERIAL PRIMARY KEY,
        job_id INTEGER REFERENCES scheduler_jobs(id),
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP,
        status VARCHAR(20) NOT NULL, -- scheduled, running, completed, failed
        error_message TEXT,
        result TEXT
    );
    
    -- Create default scheduled jobs
    INSERT INTO scheduler_jobs (
        job_name, 
        schedule_interval, 
        next_run, 
        job_function,
        parameters
    ) VALUES 
    (
        'daily_reciprocity_decay', 
        INTERVAL '1 day', 
        NOW() + INTERVAL '1 day', 
        'SELECT apply_daily_reciprocity_decay()',
        NULL
    ),
    (
        'daily_health_metrics', 
        INTERVAL '1 day', 
        NOW() + INTERVAL '1 day', 
        'SELECT generate_reciprocity_health_metrics()',
        NULL
    ),
    (
        'weekly_asset_holder_analysis', 
        INTERVAL '7 days', 
        NOW() + INTERVAL '7 days', 
        'SELECT analyze_asset_holders($1, $2)',
        '{"parameters": ["UBEC", "GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCSIKELEH7ORUCX5UB2VN"]}'
    )
    ON CONFLICT (job_name) DO NOTHING;
END;
$_$;


ALTER FUNCTION ubec_recipro.create_scheduler_tables() OWNER TO recipro;

--
-- Name: generate_reciprocity_health_metrics(); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.generate_reciprocity_health_metrics() RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    health_score DECIMAL(10,2);
    fairness_idx DECIMAL(10,2);
    part_rate DECIMAL(5,2);
    avg_score DECIMAL(10,2);
    circulation_rate DECIMAL(10,2);
    active_agents INTEGER;
    total_agents INTEGER;
    credit_txns_30d INTEGER;
    total_credits DECIMAL(18,8);
    total_score DECIMAL(18,8);
    score_rec RECORD;
    pos INTEGER := 0;
    cumulative_scores DECIMAL(18,8) := 0;
BEGIN
    -- Get total agents count
    SELECT COUNT(*) INTO total_agents FROM agents;
    
    -- Determine active agents (agents with positive reciprocity score)
    SELECT COUNT(*) INTO active_agents FROM agents WHERE reciprocity_score > 0;
    
    -- Calculate participation rate
    part_rate := CASE WHEN total_agents > 0 THEN (active_agents::DECIMAL / total_agents) * 100 ELSE 0 END;
    
    -- Calculate average agent score
    SELECT COALESCE(AVG(reciprocity_score), 0) INTO avg_score FROM agents WHERE reciprocity_score > 0;
    
    -- Get total RC in circulation
    SELECT COALESCE(SUM(reciprocity_credits), 0) INTO total_credits FROM agents;
    
    -- Get RC transactions in last 30 days
    SELECT COUNT(*) INTO credit_txns_30d 
    FROM rc_ledger 
    WHERE timestamp > extract(epoch from (NOW() - INTERVAL '30 days'));
    
    -- Calculate credit circulation rate
    circulation_rate := CASE WHEN total_credits > 0 THEN (credit_txns_30d::DECIMAL / total_credits) * 100 ELSE 0 END;
    
    -- Gini coefficient approximation for fairness index using cursor approach
    IF active_agents > 1 THEN
        -- Calculate total score
        SELECT SUM(reciprocity_score) INTO total_score
        FROM agents 
        WHERE reciprocity_score > 0;
        
        -- Compute using a cursor
        pos := 0;
        FOR score_rec IN
            SELECT reciprocity_score 
            FROM agents 
            WHERE reciprocity_score > 0 
            ORDER BY reciprocity_score
        LOOP
            pos := pos + 1;
            cumulative_scores := cumulative_scores + (pos - 0.5) * score_rec.reciprocity_score;
        END LOOP;
        
        -- Calculate fair distribution index (1 - Gini coefficient)
        fairness_idx := 1 - (1 - (2 * cumulative_scores / (active_agents * total_score)));
    ELSE
        fairness_idx := 1; -- If there's only one active agent or none, fairness is perfect
    END IF;
    
    -- Calculate overall health score - weighted average of components
    health_score := (
        part_rate * 0.25 +
        fairness_idx * 100 * 0.25 + -- Scale to 0-100 range
        LEAST(avg_score, 100) * 0.25 + -- Cap at 100
        circulation_rate * 0.25
    );
    
    -- Insert the metrics
    INSERT INTO reciprocity_health (
        metric_date,
        overall_health_score,
        fairness_index,
        participation_rate,
        average_agent_score,
        credit_circulation_rate,
        metric_details
    ) VALUES (
        NOW(),
        health_score,
        fairness_idx,
        part_rate,
        avg_score,
        circulation_rate,
        jsonb_build_object(
            'active_agents', active_agents,
            'total_agents', total_agents,
            'total_credits', total_credits,
            'credit_transactions_30d', credit_txns_30d
        )
    );
    
    RETURN 1;
END;
$$;


ALTER FUNCTION ubec_recipro.generate_reciprocity_health_metrics() OWNER TO recipro;

--
-- Name: import_asset_holders_from_json(jsonb); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.import_asset_holders_from_json(asset_holders_json jsonb) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    holder_count INTEGER := 0;
    holder_record JSONB;
    account_id VARCHAR(56);
    asset_code VARCHAR(12);
    asset_issuer VARCHAR(56);
BEGIN
    -- Process each holder in the JSON
    FOR i IN 0..jsonb_array_length(asset_holders_json)-1 LOOP
        holder_record := jsonb_array_element(asset_holders_json, i);
        account_id := holder_record->>'account_id';
        asset_code := holder_record->>'asset_code';
        asset_issuer := holder_record->>'asset_issuer';
        holder_count := holder_count + 1;
        
        -- Create or update asset holder
        INSERT INTO asset_holders (
            account_id,
            asset_code,
            asset_issuer,
            balance,
            classification,
            holding_duration_days,
            is_active,
            metrics,
            last_updated_at
        ) VALUES (
            account_id,
            asset_code,
            asset_issuer,
            COALESCE((holder_record->>'balance')::DECIMAL, 0),
            COALESCE(holder_record->>'classification', 
                CASE 
                    WHEN (holder_record->>'balance')::DECIMAL > 1000 THEN 'whale'
                    ELSE 'retail'
                END
            ),
            COALESCE((holder_record->>'holding_duration_days')::INTEGER, 0),
            COALESCE((holder_record->>'is_active')::BOOLEAN, TRUE),
            COALESCE(holder_record->'metrics', '{}'::JSONB),
            NOW()
        )
        ON CONFLICT (account_id, asset_code, asset_issuer) 
        DO UPDATE SET
            balance = COALESCE((holder_record->>'balance')::DECIMAL, asset_holders.balance),
            classification = COALESCE(holder_record->>'classification', 
                CASE 
                    WHEN (holder_record->>'balance')::DECIMAL > 1000 THEN 'whale'
                    ELSE 'retail'
                END
            ),
            holding_duration_days = COALESCE((holder_record->>'holding_duration_days')::INTEGER, asset_holders.holding_duration_days),
            is_active = COALESCE((holder_record->>'is_active')::BOOLEAN, asset_holders.is_active),
            metrics = COALESCE(holder_record->'metrics', asset_holders.metrics),
            last_updated_at = NOW();
        
        -- Create participant record if doesn't exist
        INSERT INTO participants (account_id, joined_at, account_type)
        VALUES (account_id, NOW(), 'holder')
        ON CONFLICT (account_id) DO NOTHING;
    END LOOP;
    
    RETURN holder_count;
END;
$$;


ALTER FUNCTION ubec_recipro.import_asset_holders_from_json(asset_holders_json jsonb) OWNER TO recipro;

--
-- Name: issue_reciprocity_credits(character varying, numeric, character varying, jsonb); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.issue_reciprocity_credits(agent_id_param character varying, amount numeric, reason character varying, details jsonb DEFAULT NULL::jsonb) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    agent_record RECORD;
    new_balance DECIMAL(18,8);
BEGIN
    -- Get the agent record
    SELECT id, reciprocity_credits, tier 
    INTO agent_record 
    FROM agents 
    WHERE agent_id = agent_id_param;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Agent with ID % not found', agent_id_param;
    END IF;
    
    -- Apply tier multiplier to amount
    SELECT amount * COALESCE(rc_multiplier, 1.0) INTO amount
    FROM loyalty_tiers
    WHERE tier_name = agent_record.tier;
    
    -- Update agent's reciprocity credits
    UPDATE agents
    SET reciprocity_credits = reciprocity_credits + amount
    WHERE id = agent_record.id
    RETURNING reciprocity_credits INTO new_balance;
    
    -- Record the transaction in RC ledger
    INSERT INTO rc_ledger (
        agent_id,
        transaction_type,
        amount,
        balance_after,
        timestamp,
        details
    ) VALUES (
        agent_record.id,
        'CREDIT',
        amount,
        new_balance,
        extract(epoch from now()),
        COALESCE(details, jsonb_build_object('reason', reason))
    );
    
    RETURN new_balance;
END;
$$;


ALTER FUNCTION ubec_recipro.issue_reciprocity_credits(agent_id_param character varying, amount numeric, reason character varying, details jsonb) OWNER TO recipro;

--
-- Name: process_asset_transfer(character varying, character varying, character varying, character varying, numeric, character varying); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.process_asset_transfer(asset_code_param character varying, asset_issuer_param character varying, from_account character varying, to_account character varying, amount numeric, transaction_hash character varying) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
    from_exists BOOLEAN;
    to_exists BOOLEAN;
    from_balance DECIMAL(18,8);
    to_balance DECIMAL(18,8);
    transfer_date TIMESTAMP := NOW();
BEGIN
    -- Check if sender exists in asset_holders
    SELECT EXISTS(SELECT 1 FROM asset_holders 
                  WHERE account_id = from_account 
                  AND asset_code = asset_code_param 
                  AND asset_issuer = asset_issuer_param) INTO from_exists;
    
    -- Check if recipient exists in asset_holders
    SELECT EXISTS(SELECT 1 FROM asset_holders 
                  WHERE account_id = to_account 
                  AND asset_code = asset_code_param 
                  AND asset_issuer = asset_issuer_param) INTO to_exists;
    
    -- Get current balances if they exist
    IF from_exists THEN
        SELECT balance INTO from_balance
        FROM asset_holders
        WHERE account_id = from_account
        AND asset_code = asset_code_param
        AND asset_issuer = asset_issuer_param;
    ELSE
        from_balance := 0;
    END IF;
    
    IF to_exists THEN
        SELECT balance INTO to_balance
        FROM asset_holders
        WHERE account_id = to_account
        AND asset_code = asset_code_param
        AND asset_issuer = asset_issuer_param;
    ELSE
        to_balance := 0;
    END IF;
    
    -- Update sender's balance (deduct)
    IF from_exists AND from_account != 'ISSUER' THEN
        UPDATE asset_holders
        SET balance = GREATEST(balance - amount, 0),
            last_updated_at = transfer_date
        WHERE account_id = from_account
        AND asset_code = asset_code_param
        AND asset_issuer = asset_issuer_param;
    END IF;
    
    -- Update or create recipient's balance (add)
    IF to_exists THEN
        UPDATE asset_holders
        SET balance = balance + amount,
            is_active = TRUE,
            last_updated_at = transfer_date
        WHERE account_id = to_account
        AND asset_code = asset_code_param
        AND asset_issuer = asset_issuer_param;
    ELSE
        -- Create recipient record
        INSERT INTO asset_holders (
            account_id,
            asset_code,
            asset_issuer,
            balance,
            classification,
            is_active,
            last_updated_at
        ) VALUES (
            to_account,
            asset_code_param,
            asset_issuer_param,
            amount,
            'new', -- New holder classification
            TRUE,
            transfer_date
        );
        
        -- Create participant record if doesn't exist
        INSERT INTO participants (account_id, joined_at, account_type)
        VALUES (to_account, transfer_date, 'holder')
        ON CONFLICT (account_id) DO NOTHING;
    END IF;
    
    -- Record activity for both accounts
    IF from_account != 'ISSUER' THEN
        -- Record activity for sender
        INSERT INTO participant_activities (
            participant_id,
            activity_type,
            amount,
            details,
            points_earned,
            transaction_hash,
            recorded_at
        )
        SELECT 
            p.id,
            'TRANSFER_OUT',
            amount,
            jsonb_build_object(
                'asset_code', asset_code_param,
                'asset_issuer', asset_issuer_param,
                'recipient', to_account,
                'previous_balance', from_balance,
                'new_balance', GREATEST(from_balance - amount, 0)
            ),
            0, -- No points for sending
            transaction_hash,
            transfer_date
        FROM participants p
        WHERE p.account_id = from_account;
    END IF;
    
    -- Record activity for recipient
    INSERT INTO participant_activities (
        participant_id,
        activity_type,
        amount,
        details,
        points_earned,
        transaction_hash,
        recorded_at
    )
    SELECT 
        p.id,
        'TRANSFER_IN',
        amount,
        jsonb_build_object(
            'asset_code', asset_code_param,
            'asset_issuer', asset_issuer_param,
            'sender', from_account,
            'previous_balance', to_balance,
            'new_balance', to_balance + amount
        ),
        CASE WHEN to_exists THEN 5 ELSE 10 END, -- Extra points for new holders
        transaction_hash,
        transfer_date
    FROM participants p
    WHERE p.account_id = to_account;
    
    -- Update participant last activity timestamps
    UPDATE participants
    SET last_activity_at = transfer_date,
        total_activity_count = total_activity_count + 1
    WHERE account_id IN (from_account, to_account);
    
    RETURN TRUE;
END;
$$;


ALTER FUNCTION ubec_recipro.process_asset_transfer(asset_code_param character varying, asset_issuer_param character varying, from_account character varying, to_account character varying, amount numeric, transaction_hash character varying) OWNER TO recipro;

--
-- Name: process_evaluation_queue(integer); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.process_evaluation_queue(max_evaluations integer DEFAULT 50) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    processed INTEGER := 0;
    agent_record RECORD;
BEGIN
    -- Process agents in need of evaluation
    FOR agent_record IN
        SELECT 
            a.id AS agent_id
        FROM 
            ubec_recipro.agents a
        LEFT JOIN 
            (SELECT DISTINCT ON (agent_id) agent_id, evaluation_date 
             FROM ubec_recipro.holonic_metrics 
             ORDER BY agent_id, evaluation_date DESC) hm 
            ON a.id = hm.agent_id
        WHERE
            (hm.agent_id IS NULL OR  -- Never evaluated
             a.last_activity_timestamp > EXTRACT(EPOCH FROM hm.evaluation_date) OR  -- New activity
             (EXTRACT(EPOCH FROM now()) - EXTRACT(EPOCH FROM hm.evaluation_date)) > 2592000)  -- Outdated (30 days)
            AND (a.reciprocity_score > 0 OR a.reciprocity_credits > 0)  -- Only active agents
        ORDER BY 
            a.reciprocity_score DESC  -- Prioritize highly reciprocal agents
        LIMIT max_evaluations
    LOOP
        -- Calculate scores for this agent
        PERFORM ubec_recipro.calculate_holonic_scores(agent_record.agent_id);
        processed := processed + 1;
    END LOOP;
    
    RETURN processed;
END;
$$;


ALTER FUNCTION ubec_recipro.process_evaluation_queue(max_evaluations integer) OWNER TO recipro;

--
-- Name: FUNCTION process_evaluation_queue(max_evaluations integer); Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON FUNCTION ubec_recipro.process_evaluation_queue(max_evaluations integer) IS 'Processes agents in need of holonic evaluation';


--
-- Name: process_transaction_queue(integer, integer); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.process_transaction_queue(max_transactions integer DEFAULT 100, max_api_calls integer DEFAULT 2500) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    processed INTEGER := 0;
    can_proceed BOOLEAN;
    api_calls_used INTEGER := 0;
    tx_record RECORD;
BEGIN
    -- Check if we can proceed with API calls
    SELECT ubec_recipro.check_api_rate_limit('operations', NULL, NULL, NULL) INTO can_proceed;
    
    -- If we can't proceed, exit early
    IF NOT can_proceed THEN
        RAISE NOTICE 'API rate limit reached, skipping processing';
        RETURN 0;
    END IF;
    
    -- Process transactions in priority order
    FOR tx_record IN 
        SELECT transaction_id, account_id 
        FROM ubec_recipro.transaction_queue
        WHERE operations_fetched = FALSE 
          AND status = 'pending'
          AND (next_attempt IS NULL OR next_attempt <= now())
        ORDER BY priority DESC, next_attempt ASC
        LIMIT max_transactions
    LOOP
        -- Update attempt count
        UPDATE ubec_recipro.transaction_queue
        SET 
            fetch_attempts = fetch_attempts + 1,
            last_attempt = now(),
            next_attempt = now() + (POWER(2, fetch_attempts) * INTERVAL '1 minute'), -- Exponential backoff
            status = 'processing'
        WHERE transaction_id = tx_record.transaction_id;
        
        -- This is a placeholder for the actual API call and processing
        -- In a real implementation, this would call the Stellar API and store operations
        
        -- IMPORTANT: In your implementation, replace this with actual API call logic
        -- Keep track of API calls used and respect the limit
        api_calls_used := api_calls_used + 1;
        
        -- Update transaction as processed
        UPDATE ubec_recipro.transaction_queue
        SET 
            operations_fetched = TRUE,
            status = 'completed'
        WHERE transaction_id = tx_record.transaction_id;
        
        processed := processed + 1;
        
        -- Check if we've hit the API call limit
        IF api_calls_used >= max_api_calls THEN
            EXIT;
        END IF;
    END LOOP;
    
    RETURN processed;
END;
$$;


ALTER FUNCTION ubec_recipro.process_transaction_queue(max_transactions integer, max_api_calls integer) OWNER TO recipro;

--
-- Name: FUNCTION process_transaction_queue(max_transactions integer, max_api_calls integer); Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON FUNCTION ubec_recipro.process_transaction_queue(max_transactions integer, max_api_calls integer) IS 'Processes the transaction queue while respecting API rate limits';


--
-- Name: queue_transaction(character varying, character varying, timestamp without time zone, integer); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.queue_transaction(tx_id character varying, acct_id character varying, tx_created timestamp without time zone, priority_level integer DEFAULT 5) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO ubec_recipro.transaction_queue 
        (transaction_id, account_id, created_at, priority, next_attempt)
    VALUES 
        (tx_id, acct_id, tx_created, priority_level, now())
    ON CONFLICT (transaction_id) 
    DO UPDATE SET
        priority = GREATEST(ubec_recipro.transaction_queue.priority, priority_level),
        next_attempt = CASE 
            WHEN ubec_recipro.transaction_queue.status = 'error' THEN now() 
            ELSE ubec_recipro.transaction_queue.next_attempt
        END;
    
    RETURN TRUE;
END;
$$;


ALTER FUNCTION ubec_recipro.queue_transaction(tx_id character varying, acct_id character varying, tx_created timestamp without time zone, priority_level integer) OWNER TO recipro;

--
-- Name: FUNCTION queue_transaction(tx_id character varying, acct_id character varying, tx_created timestamp without time zone, priority_level integer); Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON FUNCTION ubec_recipro.queue_transaction(tx_id character varying, acct_id character varying, tx_created timestamp without time zone, priority_level integer) IS 'Adds a transaction to the processing queue';


--
-- Name: record_agent_activity(character varying, character varying, numeric, jsonb); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.record_agent_activity(agent_id_param character varying, activity_type character varying, score_impact numeric DEFAULT 0, details jsonb DEFAULT NULL::jsonb) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    agent_db_id INTEGER;
    activity_id INTEGER;
BEGIN
    -- Get the agent's database ID
    SELECT id INTO agent_db_id 
    FROM agents 
    WHERE agent_id = agent_id_param;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Agent with ID % not found', agent_id_param;
    END IF;
    
    -- Insert the activity record
    INSERT INTO agent_activity_history (
        agent_id,
        activity_type,
        timestamp,
        details,
        score_impact
    ) VALUES (
        agent_db_id,
        activity_type,
        extract(epoch from now()),
        details,
        score_impact
    ) RETURNING id INTO activity_id;
    
    -- Update the agent's last activity timestamp
    UPDATE agents
    SET last_activity_timestamp = extract(epoch from now())
    WHERE id = agent_db_id;
    
    RETURN activity_id;
END;
$$;


ALTER FUNCTION ubec_recipro.record_agent_activity(agent_id_param character varying, activity_type character varying, score_impact numeric, details jsonb) OWNER TO recipro;

--
-- Name: record_agent_contribution(character varying, character varying, numeric, boolean, jsonb); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.record_agent_contribution(agent_id_param character varying, contribution_type character varying, amount numeric, auto_issue_rc boolean DEFAULT true, details jsonb DEFAULT NULL::jsonb) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    agent_db_id INTEGER;
    contribution_id INTEGER;
    rc_issuance_rate DECIMAL(10,2);
BEGIN
    -- Get the agent's database ID
    SELECT id INTO agent_db_id 
    FROM agents 
    WHERE agent_id = agent_id_param;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Agent with ID % not found', agent_id_param;
    END IF;
    
    -- Get RC issuance rate
    SELECT CAST(parameter_value AS DECIMAL(10,2)) INTO rc_issuance_rate
    FROM system_configuration 
    WHERE parameter_name = 'rc_issuance_rate';
    
    -- Insert the contribution record
    INSERT INTO agent_contribution_history (
        agent_id,
        contribution_type,
        amount,
        timestamp,
        details
    ) VALUES (
        agent_db_id,
        contribution_type,
        amount,
        extract(epoch from now()),
        details
    ) RETURNING id INTO contribution_id;
    
    -- Update the agent's last activity timestamp
    UPDATE agents
    SET last_activity_timestamp = extract(epoch from now())
    WHERE id = agent_db_id;
    
    -- Automatically issue reciprocity credits if requested
    IF auto_issue_rc AND rc_issuance_rate > 0 THEN
        PERFORM issue_reciprocity_credits(
            agent_id_param, 
            amount * rc_issuance_rate,
            'Contribution: ' || contribution_type,
            jsonb_build_object(
                'contribution_id', contribution_id,
                'contribution_type', contribution_type,
                'issuance_rate', rc_issuance_rate
            )
        );
    END IF;
    
    RETURN contribution_id;
END;
$$;


ALTER FUNCTION ubec_recipro.record_agent_contribution(agent_id_param character varying, contribution_type character varying, amount numeric, auto_issue_rc boolean, details jsonb) OWNER TO recipro;

--
-- Name: run_scheduled_jobs(); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.run_scheduled_jobs() RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    jobs_run INTEGER := 0;
    job_record RECORD;
    history_id INTEGER;
    result_text TEXT;
    error_msg TEXT;
BEGIN
    -- Find jobs that need to be run
    FOR job_record IN
        SELECT id, job_name, job_function, parameters
        FROM scheduler_jobs
        WHERE next_run <= NOW()
        AND enabled = TRUE
        FOR UPDATE SKIP LOCKED
    LOOP
        -- Create history record
        INSERT INTO scheduler_job_history (
            job_id, 
            start_time, 
            status
        ) VALUES (
            job_record.id,
            NOW(),
            'running'
        ) RETURNING id INTO history_id;
        
        -- Run the job
        BEGIN
            IF job_record.parameters IS NOT NULL AND job_record.parameters ? 'parameters' THEN
                -- Extract parameters array
                EXECUTE job_record.job_function 
                    USING json_array_elements_text(job_record.parameters->'parameters')
                    INTO result_text;
            ELSE
                -- No parameters
                EXECUTE job_record.job_function INTO result_text;
            END IF;
            
            -- Update job history with success
            UPDATE scheduler_job_history
            SET 
                end_time = NOW(),
                status = 'completed',
                result = result_text
            WHERE id = history_id;
            
        EXCEPTION WHEN OTHERS THEN
            -- Capture error
            GET STACKED DIAGNOSTICS error_msg = MESSAGE_TEXT;
            
            -- Update job history with failure
            UPDATE scheduler_job_history
            SET 
                end_time = NOW(),
                status = 'failed',
                error_message = error_msg
            WHERE id = history_id;
        END;
        
        -- Update job schedule
        UPDATE scheduler_jobs
        SET 
            last_run = NOW(),
            next_run = NOW() + schedule_interval
        WHERE id = job_record.id;
        
        jobs_run := jobs_run + 1;
    END LOOP;
    
    RETURN jobs_run;
END;
$$;


ALTER FUNCTION ubec_recipro.run_scheduled_jobs() OWNER TO recipro;

--
-- Name: spend_reciprocity_credits(character varying, numeric, character varying, jsonb); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.spend_reciprocity_credits(agent_id_param character varying, amount numeric, benefit_type character varying, details jsonb DEFAULT NULL::jsonb) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    agent_record RECORD;
    new_balance DECIMAL(18,8);
BEGIN
    -- Get the agent record
    SELECT id, reciprocity_credits 
    INTO agent_record 
    FROM agents 
    WHERE agent_id = agent_id_param;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Agent with ID % not found', agent_id_param;
    END IF;
    
    -- Check if agent has enough credits
    IF agent_record.reciprocity_credits < amount THEN
        RAISE EXCEPTION 'Insufficient reciprocity credits. Available: %, Required: %', 
            agent_record.reciprocity_credits, amount;
    END IF;
    
    -- Update agent's reciprocity credits
    UPDATE agents
    SET reciprocity_credits = reciprocity_credits - amount
    WHERE id = agent_record.id
    RETURNING reciprocity_credits INTO new_balance;
    
    -- Record the transaction in RC ledger
    INSERT INTO rc_ledger (
        agent_id,
        transaction_type,
        amount,
        balance_after,
        timestamp,
        details
    ) VALUES (
        agent_record.id,
        'DEBIT',
        amount,
        new_balance,
        extract(epoch from now()),
        COALESCE(details, jsonb_build_object('benefit_type', benefit_type))
    );
    
    -- Record the benefit
    INSERT INTO agent_benefit_history (
        agent_id,
        benefit_type,
        amount,
        timestamp,
        details
    ) VALUES (
        agent_record.id,
        benefit_type,
        amount,
        extract(epoch from now()),
        details
    );
    
    RETURN new_balance;
END;
$$;


ALTER FUNCTION ubec_recipro.spend_reciprocity_credits(agent_id_param character varying, amount numeric, benefit_type character varying, details jsonb) OWNER TO recipro;

--
-- Name: update_agent_reciprocity_from_activity(); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.update_agent_reciprocity_from_activity() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    agent_rec RECORD;
BEGIN
    -- Get the agent
    SELECT * INTO agent_rec FROM agents WHERE id = NEW.agent_id;
    
    -- Update the reciprocity score based on the activity impact
    UPDATE agents
    SET 
        reciprocity_score = reciprocity_score + COALESCE(NEW.score_impact, 0)
    WHERE id = NEW.agent_id;
    
    -- Add an entry to the reciprocity_scores table
    INSERT INTO reciprocity_scores (
        agent_id,
        participant_id,
        score_value,
        previous_score,
        reason,
        score_component
    ) VALUES (
        NEW.agent_id,
        agent_rec.participant_id,
        agent_rec.reciprocity_score + COALESCE(NEW.score_impact, 0),
        agent_rec.reciprocity_score,
        'Activity: ' || NEW.activity_type,
        json_build_object(
            'activity_id', NEW.id,
            'activity_type', NEW.activity_type,
            'impact', NEW.score_impact
        )
    );
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION ubec_recipro.update_agent_reciprocity_from_activity() OWNER TO recipro;

--
-- Name: update_agent_registry_from_json(jsonb); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.update_agent_registry_from_json(registry_json jsonb) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    agent_count INTEGER := 0;
    agent_record JSONB;
    agent_id VARCHAR(56);
    participant_id INTEGER;
    holon_id VARCHAR(56);
    holon_db_id INTEGER;
    agent_db_id INTEGER;
    asset_key TEXT;
    asset_data JSONB;
    holon_data JSONB;
    asset_code VARCHAR(100);
    analysis_data JSONB;
BEGIN
    -- Process each agent in the JSON
    FOR agent_id, agent_record IN SELECT * FROM jsonb_each(registry_json->'agents')
    LOOP
        agent_count := agent_count + 1;
        
        -- Create participant first if doesn't exist
        INSERT INTO participants (account_id, joined_at, account_type, metadata)
        VALUES (
            agent_id, 
            NOW(), 
            COALESCE((agent_record->>'role')::VARCHAR, 'regular'),
            agent_record->'metadata'
        )
        ON CONFLICT (account_id) 
        DO UPDATE SET 
            account_type = COALESCE((agent_record->>'role')::VARCHAR, participants.account_type),
            last_activity_at = NOW(),
            metadata = COALESCE(agent_record->'metadata', participants.metadata)
        RETURNING id INTO participant_id;
        
        -- Then create or update agent
        INSERT INTO agents (
            participant_id,
            agent_id,
            role,
            reputation_score,
            reciprocity_score,
            reciprocity_credits,
            influence,
            base_spread,
            base_order_size,
            base_asset,
            quote_asset,
            score_decay_rate,
            last_activity_timestamp,
            behavior_pattern,
            loyalty_score,
            tier,
            metadata
        ) VALUES (
            participant_id,
            agent_id,
            COALESCE((agent_record->>'role')::VARCHAR, 'regular'),
            COALESCE((agent_record->>'reputation_score')::DECIMAL, 0),
            COALESCE((agent_record->>'reciprocity_score')::DECIMAL, 0),
            COALESCE((agent_record->>'reciprocity_credits')::DECIMAL, 0),
            COALESCE((agent_record->>'influence')::DECIMAL, 0),
            COALESCE((agent_record->>'base_spread')::DECIMAL, 0.01),
            COALESCE((agent_record->>'base_order_size')::DECIMAL, 10),
            (agent_record->>'base_asset')::VARCHAR,
            (agent_record->>'quote_asset')::VARCHAR,
            COALESCE((agent_record->>'score_decay_rate')::DECIMAL, 0.01),
            COALESCE((agent_record->>'last_activity_timestamp')::BIGINT, extract(epoch from now())::BIGINT),
            (agent_record->>'behavior_pattern')::VARCHAR,
            COALESCE((agent_record->>'loyalty_score')::DECIMAL, 0),
            COALESCE((agent_record->>'tier')::VARCHAR, 'STANDARD'),
            COALESCE(agent_record->'metadata', '{}'::JSONB)
        )
        ON CONFLICT (agent_id)
        DO UPDATE SET
            role = COALESCE((agent_record->>'role')::VARCHAR, agents.role),
            reputation_score = COALESCE((agent_record->>'reputation_score')::DECIMAL, agents.reputation_score),
            reciprocity_score = COALESCE((agent_record->>'reciprocity_score')::DECIMAL, agents.reciprocity_score),
            reciprocity_credits = COALESCE((agent_record->>'reciprocity_credits')::DECIMAL, agents.reciprocity_credits),
            influence = COALESCE((agent_record->>'influence')::DECIMAL, agents.influence),
            base_spread = COALESCE((agent_record->>'base_spread')::DECIMAL, agents.base_spread),
            base_order_size = COALESCE((agent_record->>'base_order_size')::DECIMAL, agents.base_order_size),
            base_asset = COALESCE((agent_record->>'base_asset')::VARCHAR, agents.base_asset),
            quote_asset = COALESCE((agent_record->>'quote_asset')::VARCHAR, agents.quote_asset),
            score_decay_rate = COALESCE((agent_record->>'score_decay_rate')::DECIMAL, agents.score_decay_rate),
            last_activity_timestamp = COALESCE((agent_record->>'last_activity_timestamp')::BIGINT, agents.last_activity_timestamp),
            behavior_pattern = COALESCE((agent_record->>'behavior_pattern')::VARCHAR, agents.behavior_pattern),
            loyalty_score = COALESCE((agent_record->>'loyalty_score')::DECIMAL, agents.loyalty_score),
            tier = COALESCE((agent_record->>'tier')::VARCHAR, agents.tier),
            metadata = COALESCE(agent_record->'metadata', agents.metadata)
        RETURNING id INTO agent_db_id;
        
        -- Process asset holdings
        IF agent_record ? 'assets' THEN
            FOR asset_key, asset_data IN SELECT * FROM jsonb_each(agent_record->'assets')
            LOOP
                -- Insert asset holder record
                INSERT INTO asset_holders (
                    account_id,
                    asset_code,
                    asset_issuer,
                    balance,
                    classification,
                    holding_duration_days,
                    is_active,
                    metrics,
                    last_updated_at
                ) VALUES (
                    agent_id,
                    split_part(asset_key, ':', 1),
                    split_part(asset_key, ':', 2),
                    COALESCE((asset_data->>'balance')::DECIMAL, 0),
                    COALESCE(asset_data->>'classification', 'retail'),
                    COALESCE((asset_data->>'holding_duration_days')::INTEGER, 0),
                    COALESCE((asset_data->>'is_active')::BOOLEAN, TRUE),
                    COALESCE(asset_data->'metrics', '{}'::JSONB),
                    NOW()
                )
                ON CONFLICT (account_id, asset_code, asset_issuer)
                DO UPDATE SET
                    balance = COALESCE((asset_data->>'balance')::DECIMAL, asset_holders.balance),
                    classification = COALESCE(asset_data->>'classification', asset_holders.classification),
                    holding_duration_days = COALESCE((asset_data->>'holding_duration_days')::INTEGER, asset_holders.holding_duration_days),
                    is_active = COALESCE((asset_data->>'is_active')::BOOLEAN, asset_holders.is_active),
                    metrics = COALESCE(asset_data->'metrics', asset_holders.metrics),
                    last_updated_at = NOW();
            END LOOP;
        END IF;
       
        -- Process holon memberships
        IF agent_record ? 'holon_memberships' AND jsonb_array_length(agent_record->'holon_memberships') > 0 THEN
            FOR i IN 0..jsonb_array_length(agent_record->'holon_memberships')-1 LOOP
                -- Check if the element is a string or an object
                IF jsonb_typeof(jsonb_array_element(agent_record->'holon_memberships', i)) = 'string' THEN
                    holon_id := jsonb_array_element_text(agent_record->'holon_memberships', i);
                    
                    -- Ensure holon exists
                    INSERT INTO holons (holon_id, holon_name, holon_type)
                    VALUES (holon_id, holon_id, 'default')
                    ON CONFLICT (holon_id) DO NOTHING
                    RETURNING id INTO holon_db_id;
                    
                    -- Add membership if not exists
                    INSERT INTO agent_holon_memberships (agent_id, holon_id, joined_at)
                    VALUES (agent_db_id, holon_db_id, NOW())
                    ON CONFLICT (agent_id, holon_id) DO NOTHING;
                ELSE
                    -- It's an object with more details
                    holon_id := jsonb_array_element(agent_record->'holon_memberships', i)->>'holon_id';
                    
                    -- Ensure holon exists with more details
                    INSERT INTO holons (
                        holon_id, 
                        holon_name, 
                        holon_type, 
                        description,
                        health_score,
                        metadata
                    )
                    VALUES (
                        holon_id,
                        COALESCE(jsonb_array_element(agent_record->'holon_memberships', i)->>'holon_name', holon_id),
                        COALESCE(jsonb_array_element(agent_record->'holon_memberships', i)->>'holon_type', 'default'),
                        jsonb_array_element(agent_record->'holon_memberships', i)->>'description',
                        COALESCE((jsonb_array_element(agent_record->'holon_memberships', i)->>'health_score')::DECIMAL, 0),
                        jsonb_array_element(agent_record->'holon_memberships', i)->'metadata'
                    )
                    ON CONFLICT (holon_id) 
                    DO UPDATE SET
                        holon_name = COALESCE(jsonb_array_element(agent_record->'holon_memberships', i)->>'holon_name', holons.holon_name),
                        holon_type = COALESCE(jsonb_array_element(agent_record->'holon_memberships', i)->>'holon_type', holons.holon_type),
                        description = COALESCE(jsonb_array_element(agent_record->'holon_memberships', i)->>'description', holons.description),
                        health_score = COALESCE((jsonb_array_element(agent_record->'holon_memberships', i)->>'health_score')::DECIMAL, holons.health_score),
                        metadata = COALESCE(jsonb_array_element(agent_record->'holon_memberships', i)->'metadata', holons.metadata)
                    RETURNING id INTO holon_db_id;
                    
                    -- Add membership with more details
                    INSERT INTO agent_holon_memberships (
                        agent_id, 
                        holon_id, 
                        joined_at,
                        role_in_holon,
                        contribution_score,
                        status
                    )
                    VALUES (
                        agent_db_id,
                        holon_db_id,
                        COALESCE(
                            to_timestamp((jsonb_array_element(agent_record->'holon_memberships', i)->>'joined_at')::VARCHAR, 'YYYY-MM-DD"T"HH24:MI:SS.US'),
                            NOW()
                        ),
                        jsonb_array_element(agent_record->'holon_memberships', i)->>'role_in_holon',
                        COALESCE((jsonb_array_element(agent_record->'holon_memberships', i)->>'contribution_score')::DECIMAL, 0),
                        COALESCE(jsonb_array_element(agent_record->'holon_memberships', i)->>'status', 'active')
                    )
                    ON CONFLICT (agent_id, holon_id) 
                    DO UPDATE SET
                        role_in_holon = COALESCE(jsonb_array_element(agent_record->'holon_memberships', i)->>'role_in_holon', agent_holon_memberships.role_in_holon),
                        contribution_score = COALESCE((jsonb_array_element(agent_record->'holon_memberships', i)->>'contribution_score')::DECIMAL, agent_holon_memberships.contribution_score),
                        status = COALESCE(jsonb_array_element(agent_record->'holon_memberships', i)->>'status', agent_holon_memberships.status);
                END IF;
            END LOOP;
        END IF;
        
        -- Process activity history if present
        IF agent_record ? 'activity_history' AND jsonb_array_length(agent_record->'activity_history') > 0 THEN
            FOR i IN 0..jsonb_array_length(agent_record->'activity_history')-1 LOOP
                INSERT INTO agent_activity_history (
                    agent_id,
                    activity_type,
                    timestamp,
                    details,
                    score_impact
                ) VALUES (
                    agent_db_id,
                    jsonb_array_element(agent_record->'activity_history', i)->>'type',
                    COALESCE((jsonb_array_element(agent_record->'activity_history', i)->>'timestamp')::BIGINT, extract(epoch from now())::BIGINT),
                    jsonb_array_element(agent_record->'activity_history', i)->'details',
                    COALESCE((jsonb_array_element(agent_record->'activity_history', i)->>'score_impact')::DECIMAL, 0)
                );
            END LOOP;
        END IF;
        
        -- Process contribution history if present
        IF agent_record ? 'contribution_history' AND jsonb_array_length(agent_record->'contribution_history') > 0 THEN
            FOR i IN 0..jsonb_array_length(agent_record->'contribution_history')-1 LOOP
                INSERT INTO agent_contribution_history (
                    agent_id,
                    contribution_type,
                    amount,
                    timestamp,
                    details
                ) VALUES (
                    agent_db_id,
                    jsonb_array_element(agent_record->'contribution_history', i)->>'type',
                    COALESCE((jsonb_array_element(agent_record->'contribution_history', i)->>'amount')::DECIMAL, 0),
                    COALESCE((jsonb_array_element(agent_record->'contribution_history', i)->>'timestamp')::BIGINT, extract(epoch from now())::BIGINT),
                    jsonb_array_element(agent_record->'contribution_history', i)->'details'
                );
            END LOOP;
        END IF;
        
        -- Process benefit history if present
        IF agent_record ? 'benefit_history' AND jsonb_array_length(agent_record->'benefit_history') > 0 THEN
            FOR i IN 0..jsonb_array_length(agent_record->'benefit_history')-1 LOOP
                INSERT INTO agent_benefit_history (
                    agent_id,
                    benefit_type,
                    amount,
                    timestamp,
                    details
                ) VALUES (
                    agent_db_id,
                    jsonb_array_element(agent_record->'benefit_history', i)->>'type',
                    COALESCE((jsonb_array_element(agent_record->'benefit_history', i)->>'amount')::DECIMAL, 0),
                    COALESCE((jsonb_array_element(agent_record->'benefit_history', i)->>'timestamp')::BIGINT, extract(epoch from now())::BIGINT),
                    jsonb_array_element(agent_record->'benefit_history', i)->'details'
                );
            END LOOP;
        END IF;
        
        -- Process RC ledger entries if present
        IF agent_record ? 'rc_ledger' AND jsonb_array_length(agent_record->'rc_ledger') > 0 THEN
            FOR i IN 0..jsonb_array_length(agent_record->'rc_ledger')-1 LOOP
                INSERT INTO rc_ledger (
                    agent_id,
                    transaction_type,
                    amount,
                    balance_after,
                    timestamp,
                    reference_id,
                    details
                ) VALUES (
                    agent_db_id,
                    jsonb_array_element(agent_record->'rc_ledger', i)->>'transaction_type',
                    COALESCE((jsonb_array_element(agent_record->'rc_ledger', i)->>'amount')::DECIMAL, 0),
                    COALESCE((jsonb_array_element(agent_record->'rc_ledger', i)->>'balance_after')::DECIMAL, 0),
                    COALESCE((jsonb_array_element(agent_record->'rc_ledger', i)->>'timestamp')::BIGINT, extract(epoch from now())::BIGINT),
                    jsonb_array_element(agent_record->'rc_ledger', i)->>'reference_id',
                    jsonb_array_element(agent_record->'rc_ledger', i)->'details'
                );
            END LOOP;
        END IF;
    END LOOP;
    
    -- Process holons separately if present at the top level
    IF registry_json ? 'holons' THEN
        FOR holon_id, holon_data IN SELECT * FROM jsonb_each(registry_json->'holons')
        LOOP
            -- Ensure holon exists with all details
            INSERT INTO holons (
                holon_id, 
                holon_name, 
                holon_type, 
                description,
                total_members,
                total_liquidity,
                health_score,
                metadata
            )
            VALUES (
                holon_id,
                COALESCE((holon_data->>'holon_name')::VARCHAR, holon_id),
                COALESCE((holon_data->>'holon_type')::VARCHAR, 'default'),
                (holon_data->>'description')::VARCHAR,
                COALESCE((holon_data->>'total_members')::INTEGER, 0),
                COALESCE((holon_data->>'total_liquidity')::DECIMAL, 0),
                COALESCE((holon_data->>'health_score')::DECIMAL, 0),
                holon_data->'metadata'
            )
            ON CONFLICT (holon_id) 
            DO UPDATE SET
                holon_name = COALESCE((holon_data->>'holon_name')::VARCHAR, holons.holon_name),
                holon_type = COALESCE((holon_data->>'holon_type')::VARCHAR, holons.holon_type),
                description = COALESCE((holon_data->>'description')::VARCHAR, holons.description),
                total_members = COALESCE((holon_data->>'total_members')::INTEGER, holons.total_members),
                total_liquidity = COALESCE((holon_data->>'total_liquidity')::DECIMAL, holons.total_liquidity),
                health_score = COALESCE((holon_data->>'health_score')::DECIMAL, holons.health_score),
                metadata = COALESCE(holon_data->'metadata', holons.metadata);
        END LOOP;
    END IF;
    
    -- Process reciprocity_health if present
    IF registry_json ? 'reciprocity_health' THEN
        INSERT INTO reciprocity_health (
            metric_date,
            overall_health_score,
            fairness_index,
            participation_rate,
            average_agent_score,
            credit_circulation_rate,
            metric_details
        )
        VALUES (
            COALESCE(
                to_timestamp((registry_json->'reciprocity_health'->>'metric_date')::VARCHAR, 'YYYY-MM-DD"T"HH24:MI:SS.US'),
                NOW()
            ),
            COALESCE((registry_json->'reciprocity_health'->>'overall_health_score')::DECIMAL, 0),
            COALESCE((registry_json->'reciprocity_health'->>'fairness_index')::DECIMAL, 0),
            COALESCE((registry_json->'reciprocity_health'->>'participation_rate')::DECIMAL, 0),
            COALESCE((registry_json->'reciprocity_health'->>'average_agent_score')::DECIMAL, 0),
            COALESCE((registry_json->'reciprocity_health'->>'credit_circulation_rate')::DECIMAL, 0),
            registry_json->'reciprocity_health'->'metric_details'
        );
    END IF;
    
    -- Process exchange_metrics if present
    IF registry_json ? 'exchange_metrics' THEN
        INSERT INTO exchange_metrics (
            metric_date,
            total_volume,
            unique_traders,
            average_order_size,
            reciprocity_influenced_volume,
            agent_participation_percentage,
            metric_details
        )
        VALUES (
            COALESCE(
                to_timestamp((registry_json->'exchange_metrics'->>'metric_date')::VARCHAR, 'YYYY-MM-DD"T"HH24:MI:SS.US'),
                NOW()
            ),
            COALESCE((registry_json->'exchange_metrics'->>'total_volume')::DECIMAL, 0),
            COALESCE((registry_json->'exchange_metrics'->>'unique_traders')::INTEGER, 0),
            COALESCE((registry_json->'exchange_metrics'->>'average_order_size')::DECIMAL, 0),
            COALESCE((registry_json->'exchange_metrics'->>'reciprocity_influenced_volume')::DECIMAL, 0),
            COALESCE((registry_json->'exchange_metrics'->>'agent_participation_percentage')::DECIMAL, 0),
            registry_json->'exchange_metrics'->'metric_details'
        );
    END IF;
    
    -- Process asset_holder_analysis if present
    IF registry_json ? 'asset_holder_analysis' THEN
        FOR asset_code, analysis_data IN SELECT * FROM jsonb_each(registry_json->'asset_holder_analysis')
        LOOP
            -- Split asset code and issuer
            INSERT INTO asset_holder_analysis (
                analysis_date,
                asset_code,
                asset_issuer,
                total_holders,
                total_supply,
                active_holders,
                new_holders_last_30_days,
                whale_concentration_percent,
                gini_coefficient,
                distribution_metrics
            )
            VALUES (
                COALESCE(
                    to_timestamp((analysis_data->>'analysis_date')::VARCHAR, 'YYYY-MM-DD"T"HH24:MI:SS.US'),
                    NOW()
                ),
                split_part(asset_code, ':', 1),
                split_part(asset_code, ':', 2),
COALESCE((analysis_data->>'total_holders')::INTEGER, 0),
                COALESCE((analysis_data->>'total_supply')::DECIMAL, 0),
                COALESCE((analysis_data->>'active_holders')::INTEGER, 0),
                COALESCE((analysis_data->>'new_holders_last_30_days')::INTEGER, 0),
                COALESCE((analysis_data->>'whale_concentration_percent')::DECIMAL, 0),
                COALESCE((analysis_data->>'gini_coefficient')::DECIMAL, 0),
                analysis_data->'distribution_metrics'
            );
        END LOOP;
    END IF;
    
    RETURN agent_count;
END;
$$;


ALTER FUNCTION ubec_recipro.update_agent_registry_from_json(registry_json jsonb) OWNER TO recipro;

--
-- Name: update_agent_tier(character varying); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.update_agent_tier(agent_id_param character varying) RETURNS character varying
    LANGUAGE plpgsql
    AS $$
DECLARE
    participant_id INTEGER;
    current_tier VARCHAR(20);
    new_tier VARCHAR(20);
    loyalty_score DECIMAL(10,2);
    tier_id INTEGER;
BEGIN
    -- Get agent's participant ID, current tier and loyalty score
    SELECT a.participant_id, a.tier, a.loyalty_score
    INTO participant_id, current_tier, loyalty_score
    FROM agents a
    WHERE a.agent_id = agent_id_param;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Agent with ID % not found', agent_id_param;
    END IF;
    
    -- Determine appropriate tier based on loyalty score
    SELECT tier_name INTO new_tier
    FROM loyalty_tiers
    WHERE min_score <= loyalty_score
    ORDER BY min_score DESC
    LIMIT 1;
    
    -- If no tier found or score is below minimum, set to STANDARD
    IF new_tier IS NULL THEN
        new_tier := 'STANDARD';
    END IF;
    
    -- If tier changed, update agent and add tier assignment record
    IF new_tier != current_tier THEN
        -- Update agent's tier
        UPDATE agents
        SET tier = new_tier
        WHERE agent_id = agent_id_param;
        
        -- Get tier ID
        SELECT id INTO tier_id
        FROM loyalty_tiers
        WHERE tier_name = new_tier;
        
        -- Expire old tier assignment
        UPDATE participant_tiers
        SET valid_until = NOW()
        WHERE participant_id = participant_id
        AND valid_until IS NULL;
        
        -- Create new tier assignment
        INSERT INTO participant_tiers (
            participant_id,
            tier_id,
            assigned_at
        ) VALUES (
            participant_id,
            tier_id,
            NOW()
        );
        
        -- Record activity
        PERFORM record_agent_activity(
            agent_id_param,
            'TIER_CHANGE',
            10, -- Small positive impact for tier progression
            jsonb_build_object(
                'previous_tier', current_tier,
                'new_tier', new_tier,
                'loyalty_score', loyalty_score
            )
        );
    END IF;
    
    RETURN new_tier;
END;
$$;


ALTER FUNCTION ubec_recipro.update_agent_tier(agent_id_param character varying) OWNER TO recipro;

--
-- Name: update_gpiac_price(numeric, date, character varying); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.update_gpiac_price(new_gpiac_value numeric, effective_date date, transaction_hash character varying DEFAULT NULL::character varying) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    index_id INTEGER;
    reference_value DECIMAL(18,8);
    base_token_value DECIMAL(18,8);
    history_id INTEGER;
    new_price DECIMAL(18,8);
BEGIN
    -- Get the GPIAC index ID
    SELECT id INTO index_id FROM price_indices WHERE index_code = 'GPIAC';
    
    -- Get reference value and base token value from configuration
    SELECT 
        CAST(parameter_value AS DECIMAL(18,8)) INTO reference_value 
    FROM system_configuration 
    WHERE parameter_name = 'reference_gpiac';
    
    SELECT 
        CAST(parameter_value AS DECIMAL(18,8)) INTO base_token_value 
    FROM system_configuration 
    WHERE parameter_name = 'base_token_value';
    
    -- Insert new price history record
    INSERT INTO price_history (
        index_id, 
        value, 
        reference_value, 
        effective_date, 
        transaction_hash
    )
    VALUES (
        index_id, 
        new_gpiac_value, 
        reference_value, 
        effective_date, 
        transaction_hash
    )
    RETURNING id INTO history_id;
    
    -- Calculate new token price
    new_price := base_token_value * (new_gpiac_value / reference_value);
    
    -- Insert token price record
    INSERT INTO token_prices (
        price_history_id, 
        base_token_value, 
        calculated_price, 
        effective_date, 
        transaction_hash
    )
    VALUES (
        history_id, 
        base_token_value, 
        new_price, 
        effective_date, 
        transaction_hash
    );
    
    -- Return the new history ID for reference
    RETURN history_id;
END;
$$;


ALTER FUNCTION ubec_recipro.update_gpiac_price(new_gpiac_value numeric, effective_date date, transaction_hash character varying) OWNER TO recipro;

--
-- Name: update_holding_period(); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.update_holding_period() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.holding_period_days = EXTRACT(DAY FROM (NOW() - NEW.first_acquired))::INTEGER;
    RETURN NEW;
END;
$$;


ALTER FUNCTION ubec_recipro.update_holding_period() OWNER TO recipro;

--
-- Name: update_holon_metrics(); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.update_holon_metrics() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Update total members count
    UPDATE holons
    SET total_members = (
        SELECT COUNT(*) 
        FROM agent_holon_memberships 
        WHERE holon_id = NEW.holon_id
        AND status = 'active'
    )
    WHERE id = NEW.holon_id;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION ubec_recipro.update_holon_metrics() OWNER TO recipro;

--
-- Name: update_participant_activity_timestamp(); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.update_participant_activity_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE participants
    SET 
        last_activity_at = NOW(),
        total_activity_count = total_activity_count + 1
    WHERE id = NEW.participant_id;
    RETURN NEW;
END;
$$;


ALTER FUNCTION ubec_recipro.update_participant_activity_timestamp() OWNER TO recipro;

--
-- Name: update_rc_ledger_on_credit_change(); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.update_rc_ledger_on_credit_change() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF OLD.reciprocity_credits IS DISTINCT FROM NEW.reciprocity_credits THEN
        INSERT INTO ubec_recipro.rc_ledger (
            agent_id,
            transaction_type,
            amount,
            balance_after,
            timestamp,
            details
        ) VALUES (
            NEW.id,
            CASE
                WHEN NEW.reciprocity_credits > OLD.reciprocity_credits THEN 'CREDIT'
                ELSE 'DEBIT'
            END,
            ABS(NEW.reciprocity_credits - OLD.reciprocity_credits),
            NEW.reciprocity_credits,
            extract(epoch from now())::BIGINT,
            jsonb_build_object(
                'reason', 'Agent reciprocity credit update',
                'old_value', OLD.reciprocity_credits,
                'new_value', NEW.reciprocity_credits
            )
        );
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION ubec_recipro.update_rc_ledger_on_credit_change() OWNER TO recipro;

--
-- Name: update_reward_token_holder_stats(); Type: FUNCTION; Schema: ubec_recipro; Owner: recipro
--

CREATE FUNCTION ubec_recipro.update_reward_token_holder_stats() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Update last_balance_change timestamp
    IF (TG_OP = 'UPDATE' AND OLD.balance IS DISTINCT FROM NEW.balance) OR TG_OP = 'INSERT' THEN
        NEW.last_balance_change = NOW();
    END IF;
    
    -- Set first_acquired if this is a new record
    IF TG_OP = 'INSERT' THEN
        NEW.first_acquired = NOW();
    END IF;
    
    -- Update holding_period_days
    NEW.holding_period_days = EXTRACT(DAY FROM (NOW() - NEW.first_acquired))::INTEGER;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION ubec_recipro.update_reward_token_holder_stats() OWNER TO recipro;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: audit_reports; Type: TABLE; Schema: public; Owner: recipro
--

CREATE TABLE public.audit_reports (
    id integer NOT NULL,
    report_date timestamp without time zone DEFAULT now() NOT NULL,
    report_type character varying(50) NOT NULL,
    asset_code character varying(12) NOT NULL,
    asset_issuer character varying(56) NOT NULL,
    report_data jsonb NOT NULL,
    compliance_status boolean,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_reports OWNER TO recipro;

--
-- Name: audit_reports_id_seq; Type: SEQUENCE; Schema: public; Owner: recipro
--

CREATE SEQUENCE public.audit_reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audit_reports_id_seq OWNER TO recipro;

--
-- Name: audit_reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: recipro
--

ALTER SEQUENCE public.audit_reports_id_seq OWNED BY public.audit_reports.id;


--
-- Name: liquidity_pools; Type: TABLE; Schema: public; Owner: recipro
--

CREATE TABLE public.liquidity_pools (
    id character varying(64) NOT NULL,
    asset_code character varying(12) NOT NULL,
    asset_issuer character varying(56) NOT NULL,
    pair character varying(100),
    balance numeric(18,8) DEFAULT 0,
    source character varying(50) DEFAULT 'database'::character varying,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    last_updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.liquidity_pools OWNER TO recipro;

--
-- Name: transfer_recommendations; Type: TABLE; Schema: public; Owner: recipro
--

CREATE TABLE public.transfer_recommendations (
    id integer NOT NULL,
    recommendation_date timestamp without time zone DEFAULT now() NOT NULL,
    asset_code character varying(12) NOT NULL,
    asset_issuer character varying(56) NOT NULL,
    from_account_type character varying(50) NOT NULL,
    to_account_type character varying(50) NOT NULL,
    amount numeric(18,8) NOT NULL,
    status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    status_message text,
    transaction_hash character varying(64),
    actual_amount numeric(18,8),
    priority integer DEFAULT 5,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    completed_at timestamp without time zone
);


ALTER TABLE public.transfer_recommendations OWNER TO recipro;

--
-- Name: transfer_recommendations_id_seq; Type: SEQUENCE; Schema: public; Owner: recipro
--

CREATE SEQUENCE public.transfer_recommendations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.transfer_recommendations_id_seq OWNER TO recipro;

--
-- Name: transfer_recommendations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: recipro
--

ALTER SEQUENCE public.transfer_recommendations_id_seq OWNED BY public.transfer_recommendations.id;


--
-- Name: agent_activity_history; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.agent_activity_history (
    id integer NOT NULL,
    agent_id integer,
    activity_type character varying(50) NOT NULL,
    "timestamp" bigint NOT NULL,
    details jsonb,
    score_impact numeric(18,8),
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ubec_recipro.agent_activity_history OWNER TO recipro;

--
-- Name: TABLE agent_activity_history; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON TABLE ubec_recipro.agent_activity_history IS 'Record of agent activities that impact reciprocity scores';


--
-- Name: agent_activity_history_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.agent_activity_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.agent_activity_history_id_seq OWNER TO recipro;

--
-- Name: agent_activity_history_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.agent_activity_history_id_seq OWNED BY ubec_recipro.agent_activity_history.id;


--
-- Name: agent_benefit_history; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.agent_benefit_history (
    id integer NOT NULL,
    agent_id integer,
    benefit_type character varying(50) NOT NULL,
    amount numeric(18,8) NOT NULL,
    "timestamp" bigint NOT NULL,
    details jsonb,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ubec_recipro.agent_benefit_history OWNER TO recipro;

--
-- Name: TABLE agent_benefit_history; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON TABLE ubec_recipro.agent_benefit_history IS 'Record of benefits received by agents from the system';


--
-- Name: agent_benefit_history_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.agent_benefit_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.agent_benefit_history_id_seq OWNER TO recipro;

--
-- Name: agent_benefit_history_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.agent_benefit_history_id_seq OWNED BY ubec_recipro.agent_benefit_history.id;


--
-- Name: agent_contribution_history; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.agent_contribution_history (
    id integer NOT NULL,
    agent_id integer,
    contribution_type character varying(50) NOT NULL,
    amount numeric(18,8) NOT NULL,
    "timestamp" bigint NOT NULL,
    details jsonb,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ubec_recipro.agent_contribution_history OWNER TO recipro;

--
-- Name: TABLE agent_contribution_history; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON TABLE ubec_recipro.agent_contribution_history IS 'Record of positive contributions made by agents to the system';


--
-- Name: agent_contribution_history_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.agent_contribution_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.agent_contribution_history_id_seq OWNER TO recipro;

--
-- Name: agent_contribution_history_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.agent_contribution_history_id_seq OWNED BY ubec_recipro.agent_contribution_history.id;


--
-- Name: agent_holon_memberships; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.agent_holon_memberships (
    id integer NOT NULL,
    agent_id integer,
    holon_id integer,
    joined_at timestamp without time zone DEFAULT now() NOT NULL,
    role_in_holon character varying(50),
    contribution_score numeric(10,2) DEFAULT 0,
    status character varying(20) DEFAULT 'active'::character varying NOT NULL
);


ALTER TABLE ubec_recipro.agent_holon_memberships OWNER TO recipro;

--
-- Name: TABLE agent_holon_memberships; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON TABLE ubec_recipro.agent_holon_memberships IS 'Many-to-many relationship between agents and holons';


--
-- Name: agent_holon_memberships_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.agent_holon_memberships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.agent_holon_memberships_id_seq OWNER TO recipro;

--
-- Name: agent_holon_memberships_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.agent_holon_memberships_id_seq OWNED BY ubec_recipro.agent_holon_memberships.id;


--
-- Name: agents; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.agents (
    id integer NOT NULL,
    participant_id integer,
    agent_id character varying(56) NOT NULL,
    role character varying(50) NOT NULL,
    reputation_score numeric(18,8) DEFAULT 0 NOT NULL,
    reciprocity_score numeric(18,8) DEFAULT 0 NOT NULL,
    reciprocity_credits numeric(18,8) DEFAULT 0 NOT NULL,
    influence numeric(18,8) DEFAULT 0 NOT NULL,
    base_spread numeric(10,8),
    base_order_size numeric(18,8),
    base_asset character varying(56),
    quote_asset character varying(56),
    score_decay_rate numeric(10,8),
    last_activity_timestamp bigint,
    behavior_pattern character varying(50),
    loyalty_score numeric(10,2) DEFAULT 0,
    tier character varying(20) DEFAULT 'STANDARD'::character varying,
    metadata jsonb
);


ALTER TABLE ubec_recipro.agents OWNER TO recipro;

--
-- Name: TABLE agents; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON TABLE ubec_recipro.agents IS 'Represents participants in the reciprocity system with specific roles and metrics';


--
-- Name: holons; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.holons (
    id integer NOT NULL,
    holon_id character varying(56) NOT NULL,
    holon_name character varying(100),
    holon_type character varying(50) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    total_members integer DEFAULT 0,
    total_liquidity numeric(18,8) DEFAULT 0,
    health_score numeric(10,2) DEFAULT 0,
    metadata jsonb
);


ALTER TABLE ubec_recipro.holons OWNER TO recipro;

--
-- Name: TABLE holons; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON TABLE ubec_recipro.holons IS 'Groups of agents that form semi-autonomous collectives with shared governance';


--
-- Name: agent_holon_view; Type: VIEW; Schema: ubec_recipro; Owner: recipro
--

CREATE VIEW ubec_recipro.agent_holon_view AS
 SELECT a.id AS agent_id,
    a.agent_id AS agent_public_key,
    a.role,
    a.reputation_score,
    a.reciprocity_score,
    a.reciprocity_credits,
    a.influence,
    a.behavior_pattern,
    a.loyalty_score,
    a.tier,
    h.id AS holon_id,
    h.holon_name,
    h.holon_type,
    h.health_score AS holon_health_score,
    ahm.role_in_holon,
    ahm.contribution_score,
    ahm.joined_at AS joined_holon_at
   FROM ((ubec_recipro.agents a
     LEFT JOIN ubec_recipro.agent_holon_memberships ahm ON ((a.id = ahm.agent_id)))
     LEFT JOIN ubec_recipro.holons h ON ((ahm.holon_id = h.id)));


ALTER TABLE ubec_recipro.agent_holon_view OWNER TO recipro;

--
-- Name: agents_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.agents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.agents_id_seq OWNER TO recipro;

--
-- Name: agents_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.agents_id_seq OWNED BY ubec_recipro.agents.id;


--
-- Name: api_rate_limits; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.api_rate_limits (
    endpoint character varying(255) NOT NULL,
    hourly_limit integer NOT NULL,
    remaining_calls integer NOT NULL,
    reset_time timestamp without time zone NOT NULL,
    last_updated timestamp without time zone DEFAULT now()
);


ALTER TABLE ubec_recipro.api_rate_limits OWNER TO recipro;

--
-- Name: TABLE api_rate_limits; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON TABLE ubec_recipro.api_rate_limits IS 'Tracks API rate limits to prevent exceeding allowed calls';


--
-- Name: asset_holder_analysis; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.asset_holder_analysis (
    id integer NOT NULL,
    analysis_date timestamp without time zone DEFAULT now() NOT NULL,
    asset_code character varying(12) NOT NULL,
    asset_issuer character varying(56) NOT NULL,
    total_holders integer NOT NULL,
    total_supply numeric(30,8) NOT NULL,
    active_holders integer NOT NULL,
    new_holders_last_30_days integer NOT NULL,
    whale_concentration_percent numeric(10,2) NOT NULL,
    gini_coefficient numeric(5,4),
    distribution_metrics jsonb,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ubec_recipro.asset_holder_analysis OWNER TO recipro;

--
-- Name: TABLE asset_holder_analysis; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON TABLE ubec_recipro.asset_holder_analysis IS 'Analysis of asset holder distribution and metrics';


--
-- Name: asset_holder_analysis_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.asset_holder_analysis_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.asset_holder_analysis_id_seq OWNER TO recipro;

--
-- Name: asset_holder_analysis_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.asset_holder_analysis_id_seq OWNED BY ubec_recipro.asset_holder_analysis.id;


--
-- Name: asset_holders; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.asset_holders (
    id integer NOT NULL,
    account_id character varying(56) NOT NULL,
    asset_code character varying(12) NOT NULL,
    asset_issuer character varying(56) NOT NULL,
    balance numeric(18,8) NOT NULL,
    classification character varying(20),
    holding_duration_days integer,
    is_active boolean DEFAULT true,
    last_updated_at timestamp without time zone DEFAULT now() NOT NULL,
    metrics jsonb
);


ALTER TABLE ubec_recipro.asset_holders OWNER TO recipro;

--
-- Name: asset_holder_analysis_view; Type: VIEW; Schema: ubec_recipro; Owner: recipro
--

CREATE VIEW ubec_recipro.asset_holder_analysis_view AS
 SELECT aha.id,
    aha.analysis_date,
    aha.asset_code,
    aha.asset_issuer,
    aha.total_holders,
    aha.total_supply,
    aha.active_holders,
    aha.new_holders_last_30_days,
    aha.whale_concentration_percent,
    aha.gini_coefficient,
    ( SELECT count(*) AS count
           FROM ubec_recipro.asset_holders
          WHERE (((asset_holders.asset_code)::text = (aha.asset_code)::text) AND ((asset_holders.asset_issuer)::text = (aha.asset_issuer)::text) AND ((asset_holders.classification)::text = 'whale'::text))) AS whale_count,
    ( SELECT count(*) AS count
           FROM ubec_recipro.asset_holders
          WHERE (((asset_holders.asset_code)::text = (aha.asset_code)::text) AND ((asset_holders.asset_issuer)::text = (aha.asset_issuer)::text) AND ((asset_holders.classification)::text = 'retail'::text))) AS retail_count,
    ( SELECT avg(asset_holders.holding_duration_days) AS avg
           FROM ubec_recipro.asset_holders
          WHERE (((asset_holders.asset_code)::text = (aha.asset_code)::text) AND ((asset_holders.asset_issuer)::text = (aha.asset_issuer)::text))) AS average_holding_period,
    aha.distribution_metrics
   FROM ubec_recipro.asset_holder_analysis aha
  ORDER BY aha.analysis_date DESC;


ALTER TABLE ubec_recipro.asset_holder_analysis_view OWNER TO recipro;

--
-- Name: asset_holders_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.asset_holders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.asset_holders_id_seq OWNER TO recipro;

--
-- Name: asset_holders_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.asset_holders_id_seq OWNED BY ubec_recipro.asset_holders.id;


--
-- Name: audit_log; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.audit_log (
    id integer NOT NULL,
    operation_type character varying(50) NOT NULL,
    performed_by character varying(56) NOT NULL,
    details jsonb,
    ip_address character varying(45),
    user_agent text,
    performed_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ubec_recipro.audit_log OWNER TO recipro;

--
-- Name: audit_log_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.audit_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.audit_log_id_seq OWNER TO recipro;

--
-- Name: audit_log_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.audit_log_id_seq OWNED BY ubec_recipro.audit_log.id;


--
-- Name: claimable_balances; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.claimable_balances (
    id integer NOT NULL,
    stellar_claimable_id character varying(64) NOT NULL,
    participant_id integer,
    asset_code character varying(12) NOT NULL,
    asset_issuer character varying(56) NOT NULL,
    amount numeric(18,8) NOT NULL,
    distribution_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    claimable_from timestamp without time zone NOT NULL,
    claimable_to timestamp without time zone,
    claimed_at timestamp without time zone,
    claim_transaction_hash character varying(64),
    status character varying(20) DEFAULT 'active'::character varying NOT NULL
);


ALTER TABLE ubec_recipro.claimable_balances OWNER TO recipro;

--
-- Name: claimable_balances_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.claimable_balances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.claimable_balances_id_seq OWNER TO recipro;

--
-- Name: claimable_balances_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.claimable_balances_id_seq OWNED BY ubec_recipro.claimable_balances.id;


--
-- Name: distribution_history; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.distribution_history (
    id integer NOT NULL,
    check_date timestamp without time zone DEFAULT now() NOT NULL,
    asset_code character varying(12) NOT NULL,
    asset_issuer character varying(56) NOT NULL,
    general_balance numeric(18,8) NOT NULL,
    admin_balance numeric(18,8) NOT NULL,
    stewardship_balance numeric(18,8) NOT NULL,
    rebalance_needed boolean NOT NULL,
    transfers_initiated integer DEFAULT 0,
    total_transfer_amount numeric(18,8) DEFAULT 0,
    details jsonb
);


ALTER TABLE ubec_recipro.distribution_history OWNER TO recipro;

--
-- Name: distribution_history_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.distribution_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.distribution_history_id_seq OWNER TO recipro;

--
-- Name: distribution_history_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.distribution_history_id_seq OWNED BY ubec_recipro.distribution_history.id;


--
-- Name: evaluation_queue; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.evaluation_queue (
    id integer NOT NULL,
    agent_id integer,
    priority integer DEFAULT 5,
    status character varying(20) DEFAULT 'pending'::character varying,
    last_evaluation timestamp without time zone,
    next_scheduled timestamp without time zone DEFAULT now()
);


ALTER TABLE ubec_recipro.evaluation_queue OWNER TO recipro;

--
-- Name: TABLE evaluation_queue; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON TABLE ubec_recipro.evaluation_queue IS 'Queue for scheduling holonic evaluations';


--
-- Name: evaluation_queue_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.evaluation_queue_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.evaluation_queue_id_seq OWNER TO recipro;

--
-- Name: evaluation_queue_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.evaluation_queue_id_seq OWNED BY ubec_recipro.evaluation_queue.id;


--
-- Name: holonic_metrics; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.holonic_metrics (
    id integer NOT NULL,
    agent_id integer,
    evaluation_date timestamp without time zone DEFAULT now(),
    autonomy_integration_score numeric(5,4) DEFAULT 0,
    multi_scale_score numeric(5,4) DEFAULT 0,
    regenerative_impact_score numeric(5,4) DEFAULT 0,
    network_contribution_score numeric(5,4) DEFAULT 0,
    ubuntu_alignment_score numeric(5,4) DEFAULT 0,
    composite_score numeric(5,4) DEFAULT 0,
    holonic_category character varying(50),
    raw_metrics jsonb
);


ALTER TABLE ubec_recipro.holonic_metrics OWNER TO recipro;

--
-- Name: TABLE holonic_metrics; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON TABLE ubec_recipro.holonic_metrics IS 'Stores holonic evaluation metrics for UBEC token holders based on the five holonic principles';


--
-- Name: participants; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.participants (
    id integer NOT NULL,
    account_id character varying(56) NOT NULL,
    joined_at timestamp without time zone DEFAULT now() NOT NULL,
    account_type character varying(20) DEFAULT 'regular'::character varying NOT NULL,
    last_activity_at timestamp without time zone,
    total_activity_count integer DEFAULT 0 NOT NULL,
    status character varying(20) DEFAULT 'active'::character varying NOT NULL,
    metadata jsonb,
    name character varying(100),
    role character varying(50) DEFAULT 'regular'::character varying,
    reciprocity_score numeric(18,8) DEFAULT 0,
    reputation_score numeric DEFAULT 0,
    reciprocity_credits numeric DEFAULT 0.0,
    last_score_update timestamp with time zone
);


ALTER TABLE ubec_recipro.participants OWNER TO recipro;

--
-- Name: evaluation_queue_view; Type: VIEW; Schema: ubec_recipro; Owner: recipro
--

CREATE VIEW ubec_recipro.evaluation_queue_view AS
 SELECT a.id AS agent_id,
    a.agent_id AS public_key,
    p.account_id,
    a.last_activity_timestamp,
    COALESCE(hm.evaluation_date, '1970-01-01 00:00:00'::timestamp without time zone) AS last_evaluation,
        CASE
            WHEN (hm.agent_id IS NULL) THEN 'never_evaluated'::text
            WHEN ((a.last_activity_timestamp)::numeric > EXTRACT(epoch FROM hm.evaluation_date)) THEN 'new_activity'::text
            WHEN ((EXTRACT(epoch FROM now()) - EXTRACT(epoch FROM hm.evaluation_date)) > (2592000)::numeric) THEN 'outdated'::text
            ELSE 'current'::text
        END AS evaluation_status
   FROM ((ubec_recipro.agents a
     JOIN ubec_recipro.participants p ON ((a.participant_id = p.id)))
     LEFT JOIN ( SELECT DISTINCT ON (holonic_metrics.agent_id) holonic_metrics.id,
            holonic_metrics.agent_id,
            holonic_metrics.evaluation_date,
            holonic_metrics.autonomy_integration_score,
            holonic_metrics.multi_scale_score,
            holonic_metrics.regenerative_impact_score,
            holonic_metrics.network_contribution_score,
            holonic_metrics.ubuntu_alignment_score,
            holonic_metrics.composite_score,
            holonic_metrics.holonic_category,
            holonic_metrics.raw_metrics
           FROM ubec_recipro.holonic_metrics
          ORDER BY holonic_metrics.agent_id, holonic_metrics.evaluation_date DESC) hm ON ((a.id = hm.agent_id)))
  WHERE ((a.reciprocity_score > (0)::numeric) OR (a.reciprocity_credits > (0)::numeric));


ALTER TABLE ubec_recipro.evaluation_queue_view OWNER TO recipro;

--
-- Name: VIEW evaluation_queue_view; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON VIEW ubec_recipro.evaluation_queue_view IS 'Identifies accounts that need holonic evaluation based on activity or outdated metrics';


--
-- Name: exchange_metrics; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.exchange_metrics (
    id integer NOT NULL,
    metric_date timestamp without time zone DEFAULT now() NOT NULL,
    total_volume numeric(18,8) DEFAULT 0,
    unique_traders integer DEFAULT 0,
    average_order_size numeric(18,8) DEFAULT 0,
    reciprocity_influenced_volume numeric(18,8) DEFAULT 0,
    agent_participation_percentage numeric(5,2) DEFAULT 0,
    metric_details jsonb,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ubec_recipro.exchange_metrics OWNER TO recipro;

--
-- Name: TABLE exchange_metrics; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON TABLE ubec_recipro.exchange_metrics IS 'Metrics about exchange activity and reciprocity influence';


--
-- Name: exchange_metrics_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.exchange_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.exchange_metrics_id_seq OWNER TO recipro;

--
-- Name: exchange_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.exchange_metrics_id_seq OWNED BY ubec_recipro.exchange_metrics.id;


--
-- Name: exchange_metrics_view; Type: VIEW; Schema: ubec_recipro; Owner: recipro
--

CREATE VIEW ubec_recipro.exchange_metrics_view AS
 SELECT em.id,
    em.metric_date,
    em.total_volume,
    em.unique_traders,
    em.average_order_size,
    em.reciprocity_influenced_volume,
    em.agent_participation_percentage,
    ( SELECT count(*) AS count
           FROM ubec_recipro.agent_activity_history
          WHERE (((agent_activity_history.activity_type)::text = 'TRADE'::text) AND (agent_activity_history."timestamp" > (EXTRACT(epoch FROM (em.metric_date - '24:00:00'::interval)))::bigint) AND (agent_activity_history."timestamp" <= (EXTRACT(epoch FROM em.metric_date))::bigint))) AS daily_trades_count,
    ( SELECT avg(aa.score_impact) AS avg
           FROM ubec_recipro.agent_activity_history aa
          WHERE (((aa.activity_type)::text = 'TRADE'::text) AND (aa."timestamp" > (EXTRACT(epoch FROM (em.metric_date - '24:00:00'::interval)))::bigint) AND (aa."timestamp" <= (EXTRACT(epoch FROM em.metric_date))::bigint))) AS average_trade_impact,
    em.metric_details
   FROM ubec_recipro.exchange_metrics em
  ORDER BY em.metric_date DESC;


ALTER TABLE ubec_recipro.exchange_metrics_view OWNER TO recipro;

--
-- Name: transaction_operations; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.transaction_operations (
    operation_id character varying(64) NOT NULL,
    transaction_id character varying(64),
    created_at timestamp without time zone NOT NULL,
    operation_type character varying(50) NOT NULL,
    source_account character varying(56),
    destination_account character varying(56),
    asset_code character varying(12),
    asset_issuer character varying(56),
    amount numeric(20,7),
    operation_data jsonb,
    exchange_source_asset character varying(12),
    exchange_source_amount numeric(18,8),
    exchange_dest_asset character varying(12),
    exchange_dest_amount numeric(18,8)
);


ALTER TABLE ubec_recipro.transaction_operations OWNER TO recipro;

--
-- Name: TABLE transaction_operations; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON TABLE ubec_recipro.transaction_operations IS 'Cached operations for Stellar transactions to avoid re-fetching from API';


--
-- Name: exchange_operations; Type: VIEW; Schema: ubec_recipro; Owner: recipro
--

CREATE VIEW ubec_recipro.exchange_operations AS
 SELECT transaction_operations.operation_id,
    transaction_operations.transaction_id,
    transaction_operations.created_at,
    transaction_operations.operation_type,
    transaction_operations.source_account,
    transaction_operations.destination_account,
    transaction_operations.asset_code,
    transaction_operations.amount,
    transaction_operations.exchange_source_asset,
    transaction_operations.exchange_source_amount,
    transaction_operations.exchange_dest_asset,
    transaction_operations.exchange_dest_amount,
        CASE
            WHEN ((transaction_operations.exchange_source_amount > (0)::numeric) AND (transaction_operations.exchange_dest_amount > (0)::numeric)) THEN (transaction_operations.exchange_dest_amount / transaction_operations.exchange_source_amount)
            ELSE NULL::numeric
        END AS exchange_rate
   FROM ubec_recipro.transaction_operations
  WHERE ((transaction_operations.operation_type)::text = ANY ((ARRAY['exchange_in'::character varying, 'exchange_out'::character varying, 'dex_offer_buy'::character varying, 'dex_offer_sell'::character varying, 'dex_passive_buy'::character varying, 'dex_passive_sell'::character varying])::text[]));


ALTER TABLE ubec_recipro.exchange_operations OWNER TO recipro;

--
-- Name: holder_discovery_history; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.holder_discovery_history (
    id integer NOT NULL,
    discovery_date timestamp without time zone DEFAULT now() NOT NULL,
    account_id character varying(56) NOT NULL,
    discovery_source character varying(50) NOT NULL,
    source_transaction_id character varying(64),
    initial_balance numeric(18,8) DEFAULT 0,
    is_new boolean DEFAULT true,
    added_to_tracking boolean DEFAULT false,
    metadata jsonb
);


ALTER TABLE ubec_recipro.holder_discovery_history OWNER TO recipro;

--
-- Name: holder_discovery_history_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.holder_discovery_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.holder_discovery_history_id_seq OWNER TO recipro;

--
-- Name: holder_discovery_history_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.holder_discovery_history_id_seq OWNED BY ubec_recipro.holder_discovery_history.id;


--
-- Name: holonic_category_distribution; Type: VIEW; Schema: ubec_recipro; Owner: recipro
--

CREATE VIEW ubec_recipro.holonic_category_distribution AS
 SELECT holonic_metrics.holonic_category,
    count(*) AS account_count,
    round((((count(*))::numeric * 100.0) / (NULLIF(( SELECT count(*) AS count
           FROM ubec_recipro.holonic_metrics holonic_metrics_1), 0))::numeric), 2) AS percentage
   FROM ubec_recipro.holonic_metrics
  WHERE (holonic_metrics.holonic_category IS NOT NULL)
  GROUP BY holonic_metrics.holonic_category
  ORDER BY (count(*)) DESC;


ALTER TABLE ubec_recipro.holonic_category_distribution OWNER TO recipro;

--
-- Name: VIEW holonic_category_distribution; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON VIEW ubec_recipro.holonic_category_distribution IS 'Distribution of accounts across holonic categories';


--
-- Name: holonic_evaluation_view; Type: VIEW; Schema: ubec_recipro; Owner: recipro
--

CREATE VIEW ubec_recipro.holonic_evaluation_view AS
 SELECT a.id AS agent_id,
    a.agent_id AS public_key,
    p.account_id,
    p.name,
    p.account_type,
    a.role,
    a.reciprocity_credits AS balance,
    hm.evaluation_date,
    hm.autonomy_integration_score,
    hm.multi_scale_score,
    hm.regenerative_impact_score,
    hm.network_contribution_score,
    hm.ubuntu_alignment_score,
    hm.composite_score,
    hm.holonic_category,
    a.reciprocity_score,
    a.reciprocity_credits
   FROM ((ubec_recipro.agents a
     JOIN ubec_recipro.participants p ON ((a.participant_id = p.id)))
     LEFT JOIN ( SELECT DISTINCT ON (holonic_metrics.agent_id) holonic_metrics.id,
            holonic_metrics.agent_id,
            holonic_metrics.evaluation_date,
            holonic_metrics.autonomy_integration_score,
            holonic_metrics.multi_scale_score,
            holonic_metrics.regenerative_impact_score,
            holonic_metrics.network_contribution_score,
            holonic_metrics.ubuntu_alignment_score,
            holonic_metrics.composite_score,
            holonic_metrics.holonic_category,
            holonic_metrics.raw_metrics
           FROM ubec_recipro.holonic_metrics
          ORDER BY holonic_metrics.agent_id, holonic_metrics.evaluation_date DESC) hm ON ((a.id = hm.agent_id)));


ALTER TABLE ubec_recipro.holonic_evaluation_view OWNER TO recipro;

--
-- Name: VIEW holonic_evaluation_view; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON VIEW ubec_recipro.holonic_evaluation_view IS 'Comprehensive view of agents with their latest holonic evaluation metrics';


--
-- Name: holonic_metrics_history; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.holonic_metrics_history (
    id integer NOT NULL,
    agent_id integer,
    evaluation_date timestamp without time zone DEFAULT now(),
    metric_type character varying(50) NOT NULL,
    previous_score numeric(5,4),
    new_score numeric(5,4),
    change_reason text,
    change_details jsonb
);


ALTER TABLE ubec_recipro.holonic_metrics_history OWNER TO recipro;

--
-- Name: TABLE holonic_metrics_history; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON TABLE ubec_recipro.holonic_metrics_history IS 'Tracks changes in holonic metrics over time for trend analysis';


--
-- Name: holonic_metrics_history_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.holonic_metrics_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.holonic_metrics_history_id_seq OWNER TO recipro;

--
-- Name: holonic_metrics_history_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.holonic_metrics_history_id_seq OWNED BY ubec_recipro.holonic_metrics_history.id;


--
-- Name: holonic_metrics_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.holonic_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.holonic_metrics_id_seq OWNER TO recipro;

--
-- Name: holonic_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.holonic_metrics_id_seq OWNED BY ubec_recipro.holonic_metrics.id;


--
-- Name: holons_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.holons_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.holons_id_seq OWNER TO recipro;

--
-- Name: holons_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.holons_id_seq OWNED BY ubec_recipro.holons.id;


--
-- Name: liquidity_pool_owners; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.liquidity_pool_owners (
    id integer NOT NULL,
    liquidity_pool_id character varying(64) NOT NULL,
    account_id character varying(56) NOT NULL,
    ownership_percentage numeric(10,5) NOT NULL,
    last_updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ubec_recipro.liquidity_pool_owners OWNER TO recipro;

--
-- Name: liquidity_pool_owners_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.liquidity_pool_owners_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.liquidity_pool_owners_id_seq OWNER TO recipro;

--
-- Name: liquidity_pool_owners_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.liquidity_pool_owners_id_seq OWNED BY ubec_recipro.liquidity_pool_owners.id;


--
-- Name: liquidity_pools; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.liquidity_pools (
    id character varying(64) NOT NULL,
    asset_code character varying(12) NOT NULL,
    asset_issuer character varying(56) NOT NULL,
    pair character varying(50),
    balance numeric(18,8) NOT NULL,
    source character varying(20) DEFAULT 'horizon'::character varying,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    last_updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ubec_recipro.liquidity_pools OWNER TO recipro;

--
-- Name: loyalty_tiers; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.loyalty_tiers (
    id integer NOT NULL,
    tier_name character varying(50) NOT NULL,
    min_score numeric(10,2) NOT NULL,
    vesting_period_days integer NOT NULL,
    benefits text,
    rc_multiplier numeric(5,2) DEFAULT 1.0,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ubec_recipro.loyalty_tiers OWNER TO recipro;

--
-- Name: loyalty_tiers_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.loyalty_tiers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.loyalty_tiers_id_seq OWNER TO recipro;

--
-- Name: loyalty_tiers_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.loyalty_tiers_id_seq OWNED BY ubec_recipro.loyalty_tiers.id;


--
-- Name: participant_activities; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.participant_activities (
    id integer NOT NULL,
    participant_id integer,
    activity_type character varying(50) NOT NULL,
    amount numeric(18,8),
    details jsonb,
    points_earned numeric(10,2),
    transaction_hash character varying(64),
    recorded_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ubec_recipro.participant_activities OWNER TO recipro;

--
-- Name: participant_activities_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.participant_activities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.participant_activities_id_seq OWNER TO recipro;

--
-- Name: participant_activities_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.participant_activities_id_seq OWNED BY ubec_recipro.participant_activities.id;


--
-- Name: participant_relationships; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.participant_relationships (
    id integer NOT NULL,
    agent_id character varying(56) NOT NULL,
    holon_id character varying(56) NOT NULL,
    relationship_type character varying(50) NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    metadata jsonb
);


ALTER TABLE ubec_recipro.participant_relationships OWNER TO recipro;

--
-- Name: participant_relationships_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.participant_relationships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.participant_relationships_id_seq OWNER TO recipro;

--
-- Name: participant_relationships_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.participant_relationships_id_seq OWNED BY ubec_recipro.participant_relationships.id;


--
-- Name: participant_tiers; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.participant_tiers (
    id integer NOT NULL,
    participant_id integer,
    tier_id integer,
    assigned_at timestamp without time zone DEFAULT now() NOT NULL,
    valid_until timestamp without time zone
);


ALTER TABLE ubec_recipro.participant_tiers OWNER TO recipro;

--
-- Name: reciprocity_scores; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.reciprocity_scores (
    id integer NOT NULL,
    participant_id integer,
    agent_id integer,
    score_value numeric(10,2) NOT NULL,
    previous_score numeric(10,2),
    score_component json,
    reason text,
    recorded_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ubec_recipro.reciprocity_scores OWNER TO recipro;

--
-- Name: system_configuration; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.system_configuration (
    parameter_name character varying(100) NOT NULL,
    parameter_value text NOT NULL,
    description text,
    last_updated timestamp without time zone DEFAULT now() NOT NULL,
    updated_by character varying(56)
);


ALTER TABLE ubec_recipro.system_configuration OWNER TO recipro;

--
-- Name: token_distributions; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.token_distributions (
    id integer NOT NULL,
    participant_id integer,
    base_amount numeric(18,8) NOT NULL,
    multiplier numeric(5,4) NOT NULL,
    final_amount numeric(18,8) NOT NULL,
    reciprocity_score numeric(10,2) NOT NULL,
    vesting_date timestamp without time zone NOT NULL,
    expiration_date timestamp without time zone NOT NULL,
    distribution_date timestamp without time zone DEFAULT now() NOT NULL,
    transaction_hash character varying(64),
    claimable_balance_id character varying(64),
    status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    claimed_at timestamp without time zone
);


ALTER TABLE ubec_recipro.token_distributions OWNER TO recipro;

--
-- Name: participant_status_view; Type: VIEW; Schema: ubec_recipro; Owner: recipro
--

CREATE VIEW ubec_recipro.participant_status_view AS
 SELECT p.id,
    p.account_id,
    p.joined_at,
    p.account_type,
    p.last_activity_at,
    p.total_activity_count,
    p.status,
    rs.score_value AS current_reciprocity_score,
    lt.tier_name AS current_tier,
    lt.vesting_period_days,
    ( SELECT sum(td.final_amount) AS sum
           FROM ubec_recipro.token_distributions td
          WHERE (td.participant_id = p.id)) AS total_distributed,
    ( SELECT count(*) AS count
           FROM ubec_recipro.token_distributions td
          WHERE ((td.participant_id = p.id) AND ((td.status)::text = 'claimed'::text))) AS total_claimed_distributions,
    ( SELECT sum(ah.balance) AS sum
           FROM ubec_recipro.asset_holders ah
          WHERE (((ah.account_id)::text = (p.account_id)::text) AND ((ah.asset_code)::text = ( SELECT system_configuration.parameter_value
                   FROM ubec_recipro.system_configuration
                  WHERE ((system_configuration.parameter_name)::text = 'reward_asset_code'::text))) AND ((ah.asset_issuer)::text = ( SELECT system_configuration.parameter_value
                   FROM ubec_recipro.system_configuration
                  WHERE ((system_configuration.parameter_name)::text = 'reward_asset_issuer'::text))))) AS current_balance,
    a.reciprocity_credits AS rc_balance,
    p.metadata
   FROM (((ubec_recipro.participants p
     LEFT JOIN ubec_recipro.agents a ON ((p.id = a.participant_id)))
     LEFT JOIN ( SELECT rs_1.participant_id,
            rs_1.score_value
           FROM ubec_recipro.reciprocity_scores rs_1
          WHERE (rs_1.id = ( SELECT max(reciprocity_scores.id) AS max
                   FROM ubec_recipro.reciprocity_scores
                  WHERE (reciprocity_scores.participant_id = rs_1.participant_id)))) rs ON ((p.id = rs.participant_id)))
     LEFT JOIN ( SELECT pt.participant_id,
            lt_1.tier_name,
            lt_1.vesting_period_days
           FROM (ubec_recipro.participant_tiers pt
             JOIN ubec_recipro.loyalty_tiers lt_1 ON ((pt.tier_id = lt_1.id)))
          WHERE ((pt.valid_until IS NULL) OR ((pt.valid_until > now()) AND (pt.id = ( SELECT max(participant_tiers.id) AS max
                   FROM ubec_recipro.participant_tiers
                  WHERE ((participant_tiers.participant_id = pt.participant_id) AND ((participant_tiers.valid_until IS NULL) OR (participant_tiers.valid_until > now())))))))) lt ON ((p.id = lt.participant_id)));


ALTER TABLE ubec_recipro.participant_status_view OWNER TO recipro;

--
-- Name: participant_tiers_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.participant_tiers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.participant_tiers_id_seq OWNER TO recipro;

--
-- Name: participant_tiers_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.participant_tiers_id_seq OWNED BY ubec_recipro.participant_tiers.id;


--
-- Name: participants_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.participants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.participants_id_seq OWNER TO recipro;

--
-- Name: participants_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.participants_id_seq OWNED BY ubec_recipro.participants.id;


--
-- Name: price_history; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.price_history (
    id integer NOT NULL,
    index_id integer,
    value numeric(18,8) NOT NULL,
    reference_value numeric(18,8) NOT NULL,
    effective_date date NOT NULL,
    recorded_at timestamp without time zone DEFAULT now() NOT NULL,
    transaction_hash character varying(64)
);


ALTER TABLE ubec_recipro.price_history OWNER TO recipro;

--
-- Name: price_history_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.price_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.price_history_id_seq OWNER TO recipro;

--
-- Name: price_history_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.price_history_id_seq OWNED BY ubec_recipro.price_history.id;


--
-- Name: price_indices; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.price_indices (
    id integer NOT NULL,
    index_code character varying(50) NOT NULL,
    index_name character varying(100) NOT NULL,
    source character varying(100) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ubec_recipro.price_indices OWNER TO recipro;

--
-- Name: token_prices; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.token_prices (
    id integer NOT NULL,
    price_history_id integer,
    base_token_value numeric(18,8) NOT NULL,
    calculated_price numeric(18,8) NOT NULL,
    effective_date date NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    transaction_hash character varying(64)
);


ALTER TABLE ubec_recipro.token_prices OWNER TO recipro;

--
-- Name: price_history_view; Type: VIEW; Schema: ubec_recipro; Owner: recipro
--

CREATE VIEW ubec_recipro.price_history_view AS
 SELECT ph.id AS history_id,
    pi.index_code,
    pi.index_name,
    ph.effective_date,
    ph.value AS gpiac_value,
    ph.reference_value,
    tp.base_token_value,
    tp.calculated_price AS token_price,
    tp.transaction_hash
   FROM ((ubec_recipro.price_history ph
     JOIN ubec_recipro.price_indices pi ON ((ph.index_id = pi.id)))
     LEFT JOIN ubec_recipro.token_prices tp ON ((ph.id = tp.price_history_id)))
  ORDER BY ph.effective_date DESC;


ALTER TABLE ubec_recipro.price_history_view OWNER TO recipro;

--
-- Name: price_indices_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.price_indices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.price_indices_id_seq OWNER TO recipro;

--
-- Name: price_indices_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.price_indices_id_seq OWNED BY ubec_recipro.price_indices.id;


--
-- Name: rc_ledger; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.rc_ledger (
    id integer NOT NULL,
    agent_id integer,
    transaction_type character varying(50) NOT NULL,
    amount numeric(18,8) NOT NULL,
    balance_after numeric(18,8) NOT NULL,
    "timestamp" bigint NOT NULL,
    reference_id character varying(100),
    details jsonb,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ubec_recipro.rc_ledger OWNER TO recipro;

--
-- Name: TABLE rc_ledger; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON TABLE ubec_recipro.rc_ledger IS 'Transaction ledger for Reciprocity Credits (RCs)';


--
-- Name: rc_ledger_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.rc_ledger_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.rc_ledger_id_seq OWNER TO recipro;

--
-- Name: rc_ledger_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.rc_ledger_id_seq OWNED BY ubec_recipro.rc_ledger.id;


--
-- Name: rc_ledger_summary; Type: VIEW; Schema: ubec_recipro; Owner: recipro
--

CREATE VIEW ubec_recipro.rc_ledger_summary AS
 SELECT a.agent_id AS agent_public_key,
    a.role,
    a.reciprocity_score,
    a.reciprocity_credits AS current_balance,
    ( SELECT count(*) AS count
           FROM ubec_recipro.rc_ledger rl
          WHERE (rl.agent_id = a.id)) AS total_transactions,
    ( SELECT sum(
                CASE
                    WHEN ((rl.transaction_type)::text = 'CREDIT'::text) THEN rl.amount
                    ELSE (0)::numeric
                END) AS sum
           FROM ubec_recipro.rc_ledger rl
          WHERE (rl.agent_id = a.id)) AS total_credits,
    ( SELECT sum(
                CASE
                    WHEN ((rl.transaction_type)::text = 'DEBIT'::text) THEN rl.amount
                    ELSE (0)::numeric
                END) AS sum
           FROM ubec_recipro.rc_ledger rl
          WHERE (rl.agent_id = a.id)) AS total_debits,
    ( SELECT count(*) AS count
           FROM ubec_recipro.rc_ledger rl
          WHERE ((rl.agent_id = a.id) AND (rl."timestamp" > (EXTRACT(epoch FROM (now() - '30 days'::interval)))::bigint))) AS transactions_last_30_days
   FROM ubec_recipro.agents a
  WHERE ((a.reciprocity_credits > (0)::numeric) OR (EXISTS ( SELECT 1
           FROM ubec_recipro.rc_ledger rl
          WHERE (rl.agent_id = a.id))));


ALTER TABLE ubec_recipro.rc_ledger_summary OWNER TO recipro;

--
-- Name: reciprocity_health; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.reciprocity_health (
    id integer NOT NULL,
    metric_date timestamp without time zone DEFAULT now() NOT NULL,
    overall_health_score numeric(10,2) NOT NULL,
    fairness_index numeric(10,2) NOT NULL,
    participation_rate numeric(5,2) NOT NULL,
    average_agent_score numeric(10,2) NOT NULL,
    credit_circulation_rate numeric(10,2) NOT NULL,
    metric_details jsonb,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ubec_recipro.reciprocity_health OWNER TO recipro;

--
-- Name: TABLE reciprocity_health; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON TABLE ubec_recipro.reciprocity_health IS 'System-wide health metrics for the reciprocity ecosystem';


--
-- Name: reciprocity_health_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.reciprocity_health_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.reciprocity_health_id_seq OWNER TO recipro;

--
-- Name: reciprocity_health_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.reciprocity_health_id_seq OWNED BY ubec_recipro.reciprocity_health.id;


--
-- Name: reciprocity_health_view; Type: VIEW; Schema: ubec_recipro; Owner: recipro
--

CREATE VIEW ubec_recipro.reciprocity_health_view AS
 SELECT rh.id,
    rh.metric_date,
    rh.overall_health_score,
    rh.fairness_index,
    rh.participation_rate,
    rh.average_agent_score,
    rh.credit_circulation_rate,
    ( SELECT count(*) AS count
           FROM ubec_recipro.agents
          WHERE (agents.reciprocity_score > (0)::numeric)) AS active_agents_count,
    ( SELECT avg(agents.reciprocity_credits) AS avg
           FROM ubec_recipro.agents
          WHERE (agents.reciprocity_credits > (0)::numeric)) AS average_rc_balance,
    ( SELECT sum(agents.reciprocity_credits) AS sum
           FROM ubec_recipro.agents) AS total_rc_in_circulation,
    ( SELECT count(*) AS count
           FROM ubec_recipro.rc_ledger
          WHERE (rc_ledger."timestamp" > (EXTRACT(epoch FROM (now() - '30 days'::interval)))::bigint)) AS rc_transactions_30d,
    rh.metric_details
   FROM ubec_recipro.reciprocity_health rh
  ORDER BY rh.metric_date DESC;


ALTER TABLE ubec_recipro.reciprocity_health_view OWNER TO recipro;

--
-- Name: reciprocity_scores_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.reciprocity_scores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.reciprocity_scores_id_seq OWNER TO recipro;

--
-- Name: reciprocity_scores_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.reciprocity_scores_id_seq OWNED BY ubec_recipro.reciprocity_scores.id;


--
-- Name: reciprocity_transactions; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.reciprocity_transactions (
    id integer NOT NULL,
    account_id character varying(56) NOT NULL,
    transaction_type character varying(20) NOT NULL,
    amount numeric NOT NULL,
    reason character varying(100),
    source character varying(50),
    context jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE ubec_recipro.reciprocity_transactions OWNER TO recipro;

--
-- Name: reciprocity_transactions_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.reciprocity_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.reciprocity_transactions_id_seq OWNER TO recipro;

--
-- Name: reciprocity_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.reciprocity_transactions_id_seq OWNED BY ubec_recipro.reciprocity_transactions.id;


--
-- Name: regenerative_projects; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.regenerative_projects (
    id integer NOT NULL,
    agent_id integer,
    project_name character varying(255),
    description text,
    project_type character varying(50),
    location_data jsonb,
    verification_status character varying(50) DEFAULT 'unverified'::character varying,
    verification_date timestamp without time zone,
    impact_metrics jsonb,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE ubec_recipro.regenerative_projects OWNER TO recipro;

--
-- Name: TABLE regenerative_projects; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON TABLE ubec_recipro.regenerative_projects IS 'Tracks regenerative projects for evaluating environmental and social impact';


--
-- Name: regenerative_projects_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.regenerative_projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.regenerative_projects_id_seq OWNER TO recipro;

--
-- Name: regenerative_projects_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.regenerative_projects_id_seq OWNED BY ubec_recipro.regenerative_projects.id;


--
-- Name: reward_token_holders; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.reward_token_holders (
    id integer NOT NULL,
    account_id character varying(56) NOT NULL,
    asset_code character varying(12) NOT NULL,
    asset_issuer character varying(56) NOT NULL,
    balance numeric(18,8) NOT NULL,
    last_balance_change timestamp without time zone DEFAULT now() NOT NULL,
    first_acquired timestamp without time zone DEFAULT now() NOT NULL,
    holding_period_days integer,
    is_active boolean DEFAULT true,
    tier character varying(20) DEFAULT 'STANDARD'::character varying,
    metadata jsonb
);


ALTER TABLE ubec_recipro.reward_token_holders OWNER TO recipro;

--
-- Name: reward_token_holder_view; Type: VIEW; Schema: ubec_recipro; Owner: recipro
--

CREATE VIEW ubec_recipro.reward_token_holder_view AS
 SELECT rth.id,
    rth.account_id,
    rth.asset_code,
    rth.asset_issuer,
    rth.balance,
    rth.last_balance_change,
    rth.first_acquired,
    rth.holding_period_days,
    rth.tier,
    p.account_type,
    p.last_activity_at,
    p.status AS account_status,
    a.reciprocity_score,
    a.reciprocity_credits
   FROM ((ubec_recipro.reward_token_holders rth
     LEFT JOIN ubec_recipro.participants p ON (((rth.account_id)::text = (p.account_id)::text)))
     LEFT JOIN ubec_recipro.agents a ON ((p.id = a.participant_id)))
  WHERE (rth.balance > (0)::numeric)
  ORDER BY rth.balance DESC;


ALTER TABLE ubec_recipro.reward_token_holder_view OWNER TO recipro;

--
-- Name: reward_token_holders_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.reward_token_holders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.reward_token_holders_id_seq OWNER TO recipro;

--
-- Name: reward_token_holders_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.reward_token_holders_id_seq OWNED BY ubec_recipro.reward_token_holders.id;


--
-- Name: scheduler_job_history; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.scheduler_job_history (
    id integer NOT NULL,
    job_id integer,
    start_time timestamp without time zone NOT NULL,
    end_time timestamp without time zone,
    status character varying(20) NOT NULL,
    error_message text,
    result text
);


ALTER TABLE ubec_recipro.scheduler_job_history OWNER TO recipro;

--
-- Name: scheduler_job_history_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.scheduler_job_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.scheduler_job_history_id_seq OWNER TO recipro;

--
-- Name: scheduler_job_history_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.scheduler_job_history_id_seq OWNED BY ubec_recipro.scheduler_job_history.id;


--
-- Name: scheduler_jobs; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.scheduler_jobs (
    id integer NOT NULL,
    job_name character varying(100) NOT NULL,
    schedule_interval interval NOT NULL,
    last_run timestamp without time zone,
    next_run timestamp without time zone NOT NULL,
    enabled boolean DEFAULT true,
    job_function text NOT NULL,
    parameters jsonb,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ubec_recipro.scheduler_jobs OWNER TO recipro;

--
-- Name: scheduler_jobs_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.scheduler_jobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.scheduler_jobs_id_seq OWNER TO recipro;

--
-- Name: scheduler_jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.scheduler_jobs_id_seq OWNED BY ubec_recipro.scheduler_jobs.id;


--
-- Name: setup_tracking; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.setup_tracking (
    module_name character varying(100) NOT NULL,
    executed_at timestamp without time zone DEFAULT now() NOT NULL,
    executed_by character varying(100) NOT NULL,
    version character varying(20) DEFAULT '1.0'::character varying NOT NULL,
    status character varying(20) DEFAULT 'success'::character varying NOT NULL,
    details text
);


ALTER TABLE ubec_recipro.setup_tracking OWNER TO recipro;

--
-- Name: sync_jobs; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.sync_jobs (
    id integer NOT NULL,
    job_type character varying(50) NOT NULL,
    schedule_interval interval NOT NULL,
    last_run timestamp without time zone,
    next_run timestamp without time zone NOT NULL,
    enabled boolean DEFAULT true,
    parameters jsonb,
    last_status character varying(20),
    error_message text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE ubec_recipro.sync_jobs OWNER TO recipro;

--
-- Name: sync_jobs_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.sync_jobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.sync_jobs_id_seq OWNER TO recipro;

--
-- Name: sync_jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.sync_jobs_id_seq OWNED BY ubec_recipro.sync_jobs.id;


--
-- Name: sync_status; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.sync_status (
    account_id character varying(56) NOT NULL,
    last_sync timestamp without time zone DEFAULT now() NOT NULL,
    last_block_height bigint,
    last_ledger_sequence bigint,
    last_transaction_id character varying(64),
    sync_count integer DEFAULT 0,
    status character varying(20) DEFAULT 'active'::character varying,
    error_count integer DEFAULT 0,
    last_error text,
    last_error_at timestamp without time zone
);


ALTER TABLE ubec_recipro.sync_status OWNER TO recipro;

--
-- Name: token_distributions_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.token_distributions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.token_distributions_id_seq OWNER TO recipro;

--
-- Name: token_distributions_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.token_distributions_id_seq OWNED BY ubec_recipro.token_distributions.id;


--
-- Name: token_prices_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.token_prices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.token_prices_id_seq OWNER TO recipro;

--
-- Name: token_prices_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.token_prices_id_seq OWNED BY ubec_recipro.token_prices.id;


--
-- Name: transaction_queue; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.transaction_queue (
    transaction_id character varying(64) NOT NULL,
    account_id character varying(56) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    fetch_attempts integer DEFAULT 0,
    operations_fetched boolean DEFAULT false,
    last_attempt timestamp without time zone,
    next_attempt timestamp without time zone,
    priority integer DEFAULT 5,
    status character varying(20) DEFAULT 'pending'::character varying,
    error_message text
);


ALTER TABLE ubec_recipro.transaction_queue OWNER TO recipro;

--
-- Name: TABLE transaction_queue; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON TABLE ubec_recipro.transaction_queue IS 'Queue for processing Stellar transactions incrementally to respect API rate limits';


--
-- Name: transaction_queue_status; Type: VIEW; Schema: ubec_recipro; Owner: recipro
--

CREATE VIEW ubec_recipro.transaction_queue_status AS
 SELECT tq.transaction_id,
    tq.account_id,
    tq.created_at,
    tq.status,
    tq.fetch_attempts,
    tq.operations_fetched,
    count(op.operation_id) AS operation_count,
    tq.error_message
   FROM (ubec_recipro.transaction_queue tq
     LEFT JOIN ubec_recipro.transaction_operations op ON (((tq.transaction_id)::text = (op.transaction_id)::text)))
  GROUP BY tq.transaction_id, tq.account_id, tq.created_at, tq.status, tq.fetch_attempts, tq.operations_fetched, tq.error_message;


ALTER TABLE ubec_recipro.transaction_queue_status OWNER TO recipro;

--
-- Name: VIEW transaction_queue_status; Type: COMMENT; Schema: ubec_recipro; Owner: recipro
--

COMMENT ON VIEW ubec_recipro.transaction_queue_status IS 'Status overview of the transaction processing queue';


--
-- Name: transfer_recommendations; Type: TABLE; Schema: ubec_recipro; Owner: recipro
--

CREATE TABLE ubec_recipro.transfer_recommendations (
    id integer NOT NULL,
    recommendation_date timestamp without time zone DEFAULT now() NOT NULL,
    asset_code character varying(12) NOT NULL,
    asset_issuer character varying(56) NOT NULL,
    from_account_type character varying(50) NOT NULL,
    to_account_type character varying(50) NOT NULL,
    amount numeric(38,8) NOT NULL,
    status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    priority integer DEFAULT 5 NOT NULL,
    executed_at timestamp without time zone,
    transaction_hash character varying(64),
    execution_details jsonb,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    status_message text,
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE ubec_recipro.transfer_recommendations OWNER TO recipro;

--
-- Name: transfer_recommendations_id_seq; Type: SEQUENCE; Schema: ubec_recipro; Owner: recipro
--

CREATE SEQUENCE ubec_recipro.transfer_recommendations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ubec_recipro.transfer_recommendations_id_seq OWNER TO recipro;

--
-- Name: transfer_recommendations_id_seq; Type: SEQUENCE OWNED BY; Schema: ubec_recipro; Owner: recipro
--

ALTER SEQUENCE ubec_recipro.transfer_recommendations_id_seq OWNED BY ubec_recipro.transfer_recommendations.id;


--
-- Name: transfer_recommendations_view; Type: VIEW; Schema: ubec_recipro; Owner: recipro
--

CREATE VIEW ubec_recipro.transfer_recommendations_view AS
 SELECT tr.id,
    tr.recommendation_date,
    tr.asset_code,
    tr.asset_issuer,
    tr.from_account_type,
    tr.to_account_type,
    tr.amount,
    tr.status,
    tr.priority,
    tr.executed_at,
    tr.transaction_hash,
    count(ah1.id) AS from_accounts_count,
    count(ah2.id) AS to_accounts_count,
    tr.execution_details
   FROM ((ubec_recipro.transfer_recommendations tr
     LEFT JOIN ubec_recipro.asset_holders ah1 ON ((((tr.asset_code)::text = (ah1.asset_code)::text) AND ((tr.asset_issuer)::text = (ah1.asset_issuer)::text) AND ((ah1.classification)::text = (tr.from_account_type)::text))))
     LEFT JOIN ubec_recipro.asset_holders ah2 ON ((((tr.asset_code)::text = (ah2.asset_code)::text) AND ((tr.asset_issuer)::text = (ah2.asset_issuer)::text) AND ((ah2.classification)::text = (tr.to_account_type)::text))))
  GROUP BY tr.id, tr.recommendation_date, tr.asset_code, tr.asset_issuer, tr.from_account_type, tr.to_account_type, tr.amount, tr.status, tr.priority, tr.executed_at, tr.transaction_hash, tr.execution_details
  ORDER BY tr.recommendation_date DESC;


ALTER TABLE ubec_recipro.transfer_recommendations_view OWNER TO recipro;

--
-- Name: audit_reports id; Type: DEFAULT; Schema: public; Owner: recipro
--

ALTER TABLE ONLY public.audit_reports ALTER COLUMN id SET DEFAULT nextval('public.audit_reports_id_seq'::regclass);


--
-- Name: transfer_recommendations id; Type: DEFAULT; Schema: public; Owner: recipro
--

ALTER TABLE ONLY public.transfer_recommendations ALTER COLUMN id SET DEFAULT nextval('public.transfer_recommendations_id_seq'::regclass);


--
-- Name: agent_activity_history id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agent_activity_history ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.agent_activity_history_id_seq'::regclass);


--
-- Name: agent_benefit_history id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agent_benefit_history ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.agent_benefit_history_id_seq'::regclass);


--
-- Name: agent_contribution_history id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agent_contribution_history ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.agent_contribution_history_id_seq'::regclass);


--
-- Name: agent_holon_memberships id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agent_holon_memberships ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.agent_holon_memberships_id_seq'::regclass);


--
-- Name: agents id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agents ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.agents_id_seq'::regclass);


--
-- Name: asset_holder_analysis id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.asset_holder_analysis ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.asset_holder_analysis_id_seq'::regclass);


--
-- Name: asset_holders id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.asset_holders ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.asset_holders_id_seq'::regclass);


--
-- Name: audit_log id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.audit_log ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.audit_log_id_seq'::regclass);


--
-- Name: claimable_balances id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.claimable_balances ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.claimable_balances_id_seq'::regclass);


--
-- Name: distribution_history id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.distribution_history ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.distribution_history_id_seq'::regclass);


--
-- Name: evaluation_queue id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.evaluation_queue ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.evaluation_queue_id_seq'::regclass);


--
-- Name: exchange_metrics id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.exchange_metrics ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.exchange_metrics_id_seq'::regclass);


--
-- Name: holder_discovery_history id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.holder_discovery_history ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.holder_discovery_history_id_seq'::regclass);


--
-- Name: holonic_metrics id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.holonic_metrics ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.holonic_metrics_id_seq'::regclass);


--
-- Name: holonic_metrics_history id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.holonic_metrics_history ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.holonic_metrics_history_id_seq'::regclass);


--
-- Name: holons id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.holons ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.holons_id_seq'::regclass);


--
-- Name: liquidity_pool_owners id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.liquidity_pool_owners ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.liquidity_pool_owners_id_seq'::regclass);


--
-- Name: loyalty_tiers id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.loyalty_tiers ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.loyalty_tiers_id_seq'::regclass);


--
-- Name: participant_activities id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.participant_activities ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.participant_activities_id_seq'::regclass);


--
-- Name: participant_relationships id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.participant_relationships ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.participant_relationships_id_seq'::regclass);


--
-- Name: participant_tiers id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.participant_tiers ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.participant_tiers_id_seq'::regclass);


--
-- Name: participants id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.participants ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.participants_id_seq'::regclass);


--
-- Name: price_history id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.price_history ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.price_history_id_seq'::regclass);


--
-- Name: price_indices id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.price_indices ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.price_indices_id_seq'::regclass);


--
-- Name: rc_ledger id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.rc_ledger ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.rc_ledger_id_seq'::regclass);


--
-- Name: reciprocity_health id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.reciprocity_health ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.reciprocity_health_id_seq'::regclass);


--
-- Name: reciprocity_scores id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.reciprocity_scores ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.reciprocity_scores_id_seq'::regclass);


--
-- Name: reciprocity_transactions id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.reciprocity_transactions ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.reciprocity_transactions_id_seq'::regclass);


--
-- Name: regenerative_projects id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.regenerative_projects ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.regenerative_projects_id_seq'::regclass);


--
-- Name: reward_token_holders id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.reward_token_holders ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.reward_token_holders_id_seq'::regclass);


--
-- Name: scheduler_job_history id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.scheduler_job_history ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.scheduler_job_history_id_seq'::regclass);


--
-- Name: scheduler_jobs id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.scheduler_jobs ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.scheduler_jobs_id_seq'::regclass);


--
-- Name: sync_jobs id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.sync_jobs ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.sync_jobs_id_seq'::regclass);


--
-- Name: token_distributions id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.token_distributions ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.token_distributions_id_seq'::regclass);


--
-- Name: token_prices id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.token_prices ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.token_prices_id_seq'::regclass);


--
-- Name: transfer_recommendations id; Type: DEFAULT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.transfer_recommendations ALTER COLUMN id SET DEFAULT nextval('ubec_recipro.transfer_recommendations_id_seq'::regclass);


--
-- Name: audit_reports audit_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: recipro
--

ALTER TABLE ONLY public.audit_reports
    ADD CONSTRAINT audit_reports_pkey PRIMARY KEY (id);


--
-- Name: liquidity_pools liquidity_pools_pkey; Type: CONSTRAINT; Schema: public; Owner: recipro
--

ALTER TABLE ONLY public.liquidity_pools
    ADD CONSTRAINT liquidity_pools_pkey PRIMARY KEY (id);


--
-- Name: transfer_recommendations transfer_recommendations_pkey; Type: CONSTRAINT; Schema: public; Owner: recipro
--

ALTER TABLE ONLY public.transfer_recommendations
    ADD CONSTRAINT transfer_recommendations_pkey PRIMARY KEY (id);


--
-- Name: agent_activity_history agent_activity_history_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agent_activity_history
    ADD CONSTRAINT agent_activity_history_pkey PRIMARY KEY (id);


--
-- Name: agent_benefit_history agent_benefit_history_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agent_benefit_history
    ADD CONSTRAINT agent_benefit_history_pkey PRIMARY KEY (id);


--
-- Name: agent_contribution_history agent_contribution_history_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agent_contribution_history
    ADD CONSTRAINT agent_contribution_history_pkey PRIMARY KEY (id);


--
-- Name: agent_holon_memberships agent_holon_memberships_agent_id_holon_id_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agent_holon_memberships
    ADD CONSTRAINT agent_holon_memberships_agent_id_holon_id_key UNIQUE (agent_id, holon_id);


--
-- Name: agent_holon_memberships agent_holon_memberships_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agent_holon_memberships
    ADD CONSTRAINT agent_holon_memberships_pkey PRIMARY KEY (id);


--
-- Name: agents agents_agent_id_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agents
    ADD CONSTRAINT agents_agent_id_key UNIQUE (agent_id);


--
-- Name: agents agents_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agents
    ADD CONSTRAINT agents_pkey PRIMARY KEY (id);


--
-- Name: api_rate_limits api_rate_limits_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.api_rate_limits
    ADD CONSTRAINT api_rate_limits_pkey PRIMARY KEY (endpoint);


--
-- Name: asset_holder_analysis asset_holder_analysis_analysis_date_asset_code_asset_issuer_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.asset_holder_analysis
    ADD CONSTRAINT asset_holder_analysis_analysis_date_asset_code_asset_issuer_key UNIQUE (analysis_date, asset_code, asset_issuer);


--
-- Name: asset_holder_analysis asset_holder_analysis_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.asset_holder_analysis
    ADD CONSTRAINT asset_holder_analysis_pkey PRIMARY KEY (id);


--
-- Name: asset_holders asset_holders_account_id_asset_code_asset_issuer_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.asset_holders
    ADD CONSTRAINT asset_holders_account_id_asset_code_asset_issuer_key UNIQUE (account_id, asset_code, asset_issuer);


--
-- Name: asset_holders asset_holders_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.asset_holders
    ADD CONSTRAINT asset_holders_pkey PRIMARY KEY (id);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id);


--
-- Name: claimable_balances claimable_balances_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.claimable_balances
    ADD CONSTRAINT claimable_balances_pkey PRIMARY KEY (id);


--
-- Name: claimable_balances claimable_balances_stellar_claimable_id_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.claimable_balances
    ADD CONSTRAINT claimable_balances_stellar_claimable_id_key UNIQUE (stellar_claimable_id);


--
-- Name: distribution_history distribution_history_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.distribution_history
    ADD CONSTRAINT distribution_history_pkey PRIMARY KEY (id);


--
-- Name: evaluation_queue evaluation_queue_agent_id_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.evaluation_queue
    ADD CONSTRAINT evaluation_queue_agent_id_key UNIQUE (agent_id);


--
-- Name: evaluation_queue evaluation_queue_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.evaluation_queue
    ADD CONSTRAINT evaluation_queue_pkey PRIMARY KEY (id);


--
-- Name: exchange_metrics exchange_metrics_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.exchange_metrics
    ADD CONSTRAINT exchange_metrics_pkey PRIMARY KEY (id);


--
-- Name: holder_discovery_history holder_discovery_history_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.holder_discovery_history
    ADD CONSTRAINT holder_discovery_history_pkey PRIMARY KEY (id);


--
-- Name: holonic_metrics holonic_metrics_agent_id_evaluation_date_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.holonic_metrics
    ADD CONSTRAINT holonic_metrics_agent_id_evaluation_date_key UNIQUE (agent_id, evaluation_date);


--
-- Name: holonic_metrics_history holonic_metrics_history_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.holonic_metrics_history
    ADD CONSTRAINT holonic_metrics_history_pkey PRIMARY KEY (id);


--
-- Name: holonic_metrics holonic_metrics_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.holonic_metrics
    ADD CONSTRAINT holonic_metrics_pkey PRIMARY KEY (id);


--
-- Name: holons holons_holon_id_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.holons
    ADD CONSTRAINT holons_holon_id_key UNIQUE (holon_id);


--
-- Name: holons holons_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.holons
    ADD CONSTRAINT holons_pkey PRIMARY KEY (id);


--
-- Name: liquidity_pool_owners liquidity_pool_owners_liquidity_pool_id_account_id_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.liquidity_pool_owners
    ADD CONSTRAINT liquidity_pool_owners_liquidity_pool_id_account_id_key UNIQUE (liquidity_pool_id, account_id);


--
-- Name: liquidity_pool_owners liquidity_pool_owners_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.liquidity_pool_owners
    ADD CONSTRAINT liquidity_pool_owners_pkey PRIMARY KEY (id);


--
-- Name: liquidity_pools liquidity_pools_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.liquidity_pools
    ADD CONSTRAINT liquidity_pools_pkey PRIMARY KEY (id, asset_code, asset_issuer);


--
-- Name: loyalty_tiers loyalty_tiers_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.loyalty_tiers
    ADD CONSTRAINT loyalty_tiers_pkey PRIMARY KEY (id);


--
-- Name: loyalty_tiers loyalty_tiers_tier_name_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.loyalty_tiers
    ADD CONSTRAINT loyalty_tiers_tier_name_key UNIQUE (tier_name);


--
-- Name: participant_activities participant_activities_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.participant_activities
    ADD CONSTRAINT participant_activities_pkey PRIMARY KEY (id);


--
-- Name: participant_relationships participant_relationships_agent_id_holon_id_relationship_ty_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.participant_relationships
    ADD CONSTRAINT participant_relationships_agent_id_holon_id_relationship_ty_key UNIQUE (agent_id, holon_id, relationship_type);


--
-- Name: participant_relationships participant_relationships_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.participant_relationships
    ADD CONSTRAINT participant_relationships_pkey PRIMARY KEY (id);


--
-- Name: participant_tiers participant_tiers_participant_id_assigned_at_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.participant_tiers
    ADD CONSTRAINT participant_tiers_participant_id_assigned_at_key UNIQUE (participant_id, assigned_at);


--
-- Name: participant_tiers participant_tiers_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.participant_tiers
    ADD CONSTRAINT participant_tiers_pkey PRIMARY KEY (id);


--
-- Name: participants participants_account_id_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.participants
    ADD CONSTRAINT participants_account_id_key UNIQUE (account_id);


--
-- Name: participants participants_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.participants
    ADD CONSTRAINT participants_pkey PRIMARY KEY (id);


--
-- Name: price_history price_history_index_id_effective_date_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.price_history
    ADD CONSTRAINT price_history_index_id_effective_date_key UNIQUE (index_id, effective_date);


--
-- Name: price_history price_history_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.price_history
    ADD CONSTRAINT price_history_pkey PRIMARY KEY (id);


--
-- Name: price_indices price_indices_index_code_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.price_indices
    ADD CONSTRAINT price_indices_index_code_key UNIQUE (index_code);


--
-- Name: price_indices price_indices_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.price_indices
    ADD CONSTRAINT price_indices_pkey PRIMARY KEY (id);


--
-- Name: rc_ledger rc_ledger_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.rc_ledger
    ADD CONSTRAINT rc_ledger_pkey PRIMARY KEY (id);


--
-- Name: reciprocity_health reciprocity_health_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.reciprocity_health
    ADD CONSTRAINT reciprocity_health_pkey PRIMARY KEY (id);


--
-- Name: reciprocity_scores reciprocity_scores_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.reciprocity_scores
    ADD CONSTRAINT reciprocity_scores_pkey PRIMARY KEY (id);


--
-- Name: reciprocity_transactions reciprocity_transactions_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.reciprocity_transactions
    ADD CONSTRAINT reciprocity_transactions_pkey PRIMARY KEY (id);


--
-- Name: regenerative_projects regenerative_projects_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.regenerative_projects
    ADD CONSTRAINT regenerative_projects_pkey PRIMARY KEY (id);


--
-- Name: reward_token_holders reward_token_holders_account_id_asset_code_asset_issuer_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.reward_token_holders
    ADD CONSTRAINT reward_token_holders_account_id_asset_code_asset_issuer_key UNIQUE (account_id, asset_code, asset_issuer);


--
-- Name: reward_token_holders reward_token_holders_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.reward_token_holders
    ADD CONSTRAINT reward_token_holders_pkey PRIMARY KEY (id);


--
-- Name: scheduler_job_history scheduler_job_history_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.scheduler_job_history
    ADD CONSTRAINT scheduler_job_history_pkey PRIMARY KEY (id);


--
-- Name: scheduler_jobs scheduler_jobs_job_name_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.scheduler_jobs
    ADD CONSTRAINT scheduler_jobs_job_name_key UNIQUE (job_name);


--
-- Name: scheduler_jobs scheduler_jobs_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.scheduler_jobs
    ADD CONSTRAINT scheduler_jobs_pkey PRIMARY KEY (id);


--
-- Name: setup_tracking setup_tracking_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.setup_tracking
    ADD CONSTRAINT setup_tracking_pkey PRIMARY KEY (module_name);


--
-- Name: sync_jobs sync_jobs_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.sync_jobs
    ADD CONSTRAINT sync_jobs_pkey PRIMARY KEY (id);


--
-- Name: sync_status sync_status_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.sync_status
    ADD CONSTRAINT sync_status_pkey PRIMARY KEY (account_id);


--
-- Name: system_configuration system_configuration_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.system_configuration
    ADD CONSTRAINT system_configuration_pkey PRIMARY KEY (parameter_name);


--
-- Name: token_distributions token_distributions_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.token_distributions
    ADD CONSTRAINT token_distributions_pkey PRIMARY KEY (id);


--
-- Name: token_prices token_prices_effective_date_key; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.token_prices
    ADD CONSTRAINT token_prices_effective_date_key UNIQUE (effective_date);


--
-- Name: token_prices token_prices_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.token_prices
    ADD CONSTRAINT token_prices_pkey PRIMARY KEY (id);


--
-- Name: transaction_operations transaction_operations_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.transaction_operations
    ADD CONSTRAINT transaction_operations_pkey PRIMARY KEY (operation_id);


--
-- Name: transaction_queue transaction_queue_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.transaction_queue
    ADD CONSTRAINT transaction_queue_pkey PRIMARY KEY (transaction_id);


--
-- Name: transfer_recommendations transfer_recommendations_pkey; Type: CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.transfer_recommendations
    ADD CONSTRAINT transfer_recommendations_pkey PRIMARY KEY (id);


--
-- Name: idx_agent_activity_history_agent_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_agent_activity_history_agent_id ON ubec_recipro.agent_activity_history USING btree (agent_id);


--
-- Name: idx_agent_benefit_history_agent_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_agent_benefit_history_agent_id ON ubec_recipro.agent_benefit_history USING btree (agent_id);


--
-- Name: idx_agent_contribution_history_agent_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_agent_contribution_history_agent_id ON ubec_recipro.agent_contribution_history USING btree (agent_id);


--
-- Name: idx_agent_holon_memberships_agent_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_agent_holon_memberships_agent_id ON ubec_recipro.agent_holon_memberships USING btree (agent_id);


--
-- Name: idx_agent_holon_memberships_holon_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_agent_holon_memberships_holon_id ON ubec_recipro.agent_holon_memberships USING btree (holon_id);


--
-- Name: idx_agents_agent_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_agents_agent_id ON ubec_recipro.agents USING btree (agent_id);


--
-- Name: idx_agents_behavior_pattern; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_agents_behavior_pattern ON ubec_recipro.agents USING btree (behavior_pattern);


--
-- Name: idx_agents_participant_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_agents_participant_id ON ubec_recipro.agents USING btree (participant_id);


--
-- Name: idx_agents_role; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_agents_role ON ubec_recipro.agents USING btree (role);


--
-- Name: idx_agents_tier; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_agents_tier ON ubec_recipro.agents USING btree (tier);


--
-- Name: idx_asset_holder_analysis_analysis_date; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_asset_holder_analysis_analysis_date ON ubec_recipro.asset_holder_analysis USING btree (analysis_date);


--
-- Name: idx_asset_holder_analysis_asset_code; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_asset_holder_analysis_asset_code ON ubec_recipro.asset_holder_analysis USING btree (asset_code, asset_issuer);


--
-- Name: idx_asset_holders_account_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_asset_holders_account_id ON ubec_recipro.asset_holders USING btree (account_id);


--
-- Name: idx_asset_holders_asset_code; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_asset_holders_asset_code ON ubec_recipro.asset_holders USING btree (asset_code, asset_issuer);


--
-- Name: idx_asset_holders_classification; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_asset_holders_classification ON ubec_recipro.asset_holders USING btree (classification);


--
-- Name: idx_claimable_balances_participant_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_claimable_balances_participant_id ON ubec_recipro.claimable_balances USING btree (participant_id);


--
-- Name: idx_claimable_balances_status; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_claimable_balances_status ON ubec_recipro.claimable_balances USING btree (status);


--
-- Name: idx_exchange_metrics_metric_date; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_exchange_metrics_metric_date ON ubec_recipro.exchange_metrics USING btree (metric_date);


--
-- Name: idx_holonic_metrics_agent; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_holonic_metrics_agent ON ubec_recipro.holonic_metrics USING btree (agent_id);


--
-- Name: idx_holonic_metrics_category; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_holonic_metrics_category ON ubec_recipro.holonic_metrics USING btree (holonic_category);


--
-- Name: idx_holonic_metrics_date; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_holonic_metrics_date ON ubec_recipro.holonic_metrics USING btree (evaluation_date DESC);


--
-- Name: idx_holonic_metrics_score; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_holonic_metrics_score ON ubec_recipro.holonic_metrics USING btree (composite_score DESC);


--
-- Name: idx_lp_owners_account; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_lp_owners_account ON ubec_recipro.liquidity_pool_owners USING btree (account_id);


--
-- Name: idx_participant_activities_activity_type; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_participant_activities_activity_type ON ubec_recipro.participant_activities USING btree (activity_type);


--
-- Name: idx_participant_activities_participant_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_participant_activities_participant_id ON ubec_recipro.participant_activities USING btree (participant_id);


--
-- Name: idx_participant_activities_recorded_at; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_participant_activities_recorded_at ON ubec_recipro.participant_activities USING btree (recorded_at);


--
-- Name: idx_participant_relationships_agent_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_participant_relationships_agent_id ON ubec_recipro.participant_relationships USING btree (agent_id);


--
-- Name: idx_participant_relationships_holon_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_participant_relationships_holon_id ON ubec_recipro.participant_relationships USING btree (holon_id);


--
-- Name: idx_price_history_effective_date; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_price_history_effective_date ON ubec_recipro.price_history USING btree (effective_date);


--
-- Name: idx_rc_ledger_agent_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_rc_ledger_agent_id ON ubec_recipro.rc_ledger USING btree (agent_id);


--
-- Name: idx_rc_ledger_timestamp; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_rc_ledger_timestamp ON ubec_recipro.rc_ledger USING btree ("timestamp");


--
-- Name: idx_rc_ledger_transaction_type; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_rc_ledger_transaction_type ON ubec_recipro.rc_ledger USING btree (transaction_type);


--
-- Name: idx_reciprocity_health_metric_date; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_reciprocity_health_metric_date ON ubec_recipro.reciprocity_health USING btree (metric_date);


--
-- Name: idx_reciprocity_scores_agent_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_reciprocity_scores_agent_id ON ubec_recipro.reciprocity_scores USING btree (agent_id);


--
-- Name: idx_reciprocity_scores_participant_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_reciprocity_scores_participant_id ON ubec_recipro.reciprocity_scores USING btree (participant_id);


--
-- Name: idx_reciprocity_scores_recorded_at; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_reciprocity_scores_recorded_at ON ubec_recipro.reciprocity_scores USING btree (recorded_at);


--
-- Name: idx_regenerative_projects_agent; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_regenerative_projects_agent ON ubec_recipro.regenerative_projects USING btree (agent_id);


--
-- Name: idx_regenerative_projects_status; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_regenerative_projects_status ON ubec_recipro.regenerative_projects USING btree (verification_status);


--
-- Name: idx_regenerative_projects_type; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_regenerative_projects_type ON ubec_recipro.regenerative_projects USING btree (project_type);


--
-- Name: idx_reward_token_holders_account_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_reward_token_holders_account_id ON ubec_recipro.reward_token_holders USING btree (account_id);


--
-- Name: idx_reward_token_holders_asset_code; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_reward_token_holders_asset_code ON ubec_recipro.reward_token_holders USING btree (asset_code, asset_issuer);


--
-- Name: idx_reward_token_holders_tier; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_reward_token_holders_tier ON ubec_recipro.reward_token_holders USING btree (tier);


--
-- Name: idx_token_distributions_distribution_date; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_token_distributions_distribution_date ON ubec_recipro.token_distributions USING btree (distribution_date);


--
-- Name: idx_token_distributions_participant_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_token_distributions_participant_id ON ubec_recipro.token_distributions USING btree (participant_id);


--
-- Name: idx_token_distributions_status; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_token_distributions_status ON ubec_recipro.token_distributions USING btree (status);


--
-- Name: idx_token_prices_effective_date; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_token_prices_effective_date ON ubec_recipro.token_prices USING btree (effective_date);


--
-- Name: idx_transaction_ops_asset; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_transaction_ops_asset ON ubec_recipro.transaction_operations USING btree (asset_code, asset_issuer);


--
-- Name: idx_transaction_ops_destination; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_transaction_ops_destination ON ubec_recipro.transaction_operations USING btree (destination_account);


--
-- Name: idx_transaction_ops_source; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_transaction_ops_source ON ubec_recipro.transaction_operations USING btree (source_account);


--
-- Name: idx_transaction_ops_tx_id; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_transaction_ops_tx_id ON ubec_recipro.transaction_operations USING btree (transaction_id);


--
-- Name: idx_transaction_queue_next_attempt; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_transaction_queue_next_attempt ON ubec_recipro.transaction_queue USING btree (next_attempt);


--
-- Name: idx_transaction_queue_priority; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_transaction_queue_priority ON ubec_recipro.transaction_queue USING btree (priority DESC);


--
-- Name: idx_transaction_queue_status; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_transaction_queue_status ON ubec_recipro.transaction_queue USING btree (status);


--
-- Name: idx_transfer_recommendations_asset; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_transfer_recommendations_asset ON ubec_recipro.transfer_recommendations USING btree (asset_code, asset_issuer);


--
-- Name: idx_transfer_recommendations_date; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_transfer_recommendations_date ON ubec_recipro.transfer_recommendations USING btree (recommendation_date);


--
-- Name: idx_transfer_recommendations_status; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_transfer_recommendations_status ON ubec_recipro.transfer_recommendations USING btree (status);


--
-- Name: idx_tx_ops_exchange_assets; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_tx_ops_exchange_assets ON ubec_recipro.transaction_operations USING btree (exchange_source_asset, exchange_dest_asset);


--
-- Name: idx_tx_ops_exchange_type; Type: INDEX; Schema: ubec_recipro; Owner: recipro
--

CREATE INDEX idx_tx_ops_exchange_type ON ubec_recipro.transaction_operations USING btree (operation_type) WHERE (((operation_type)::text ~~ 'exchange%'::text) OR ((operation_type)::text ~~ 'dex_%'::text));


--
-- Name: agents audit_agent_changes; Type: TRIGGER; Schema: ubec_recipro; Owner: recipro
--

CREATE TRIGGER audit_agent_changes AFTER INSERT OR DELETE OR UPDATE ON ubec_recipro.agents FOR EACH ROW EXECUTE FUNCTION ubec_recipro.audit_table_change();


--
-- Name: claimable_balances audit_claimable_balance_changes; Type: TRIGGER; Schema: ubec_recipro; Owner: recipro
--

CREATE TRIGGER audit_claimable_balance_changes AFTER INSERT OR DELETE OR UPDATE ON ubec_recipro.claimable_balances FOR EACH ROW EXECUTE FUNCTION ubec_recipro.audit_table_change();


--
-- Name: token_distributions audit_distribution_changes; Type: TRIGGER; Schema: ubec_recipro; Owner: recipro
--

CREATE TRIGGER audit_distribution_changes AFTER INSERT OR DELETE OR UPDATE ON ubec_recipro.token_distributions FOR EACH ROW EXECUTE FUNCTION ubec_recipro.audit_table_change();


--
-- Name: holons audit_holon_changes; Type: TRIGGER; Schema: ubec_recipro; Owner: recipro
--

CREATE TRIGGER audit_holon_changes AFTER INSERT OR DELETE OR UPDATE ON ubec_recipro.holons FOR EACH ROW EXECUTE FUNCTION ubec_recipro.audit_table_change();


--
-- Name: price_history audit_price_changes; Type: TRIGGER; Schema: ubec_recipro; Owner: recipro
--

CREATE TRIGGER audit_price_changes AFTER INSERT OR DELETE OR UPDATE ON ubec_recipro.price_history FOR EACH ROW EXECUTE FUNCTION ubec_recipro.audit_table_change();


--
-- Name: rc_ledger audit_rc_ledger_changes; Type: TRIGGER; Schema: ubec_recipro; Owner: recipro
--

CREATE TRIGGER audit_rc_ledger_changes AFTER INSERT OR DELETE OR UPDATE ON ubec_recipro.rc_ledger FOR EACH ROW EXECUTE FUNCTION ubec_recipro.audit_table_change();


--
-- Name: reciprocity_health audit_reciprocity_health_changes; Type: TRIGGER; Schema: ubec_recipro; Owner: recipro
--

CREATE TRIGGER audit_reciprocity_health_changes AFTER INSERT OR DELETE OR UPDATE ON ubec_recipro.reciprocity_health FOR EACH ROW EXECUTE FUNCTION ubec_recipro.audit_table_change();


--
-- Name: reward_token_holders audit_reward_token_holder_changes; Type: TRIGGER; Schema: ubec_recipro; Owner: recipro
--

CREATE TRIGGER audit_reward_token_holder_changes AFTER INSERT OR DELETE OR UPDATE ON ubec_recipro.reward_token_holders FOR EACH ROW EXECUTE FUNCTION ubec_recipro.audit_table_change();


--
-- Name: token_prices audit_token_price_changes; Type: TRIGGER; Schema: ubec_recipro; Owner: recipro
--

CREATE TRIGGER audit_token_price_changes AFTER INSERT OR DELETE OR UPDATE ON ubec_recipro.token_prices FOR EACH ROW EXECUTE FUNCTION ubec_recipro.audit_table_change();


--
-- Name: agent_activity_history update_agent_reciprocity_score; Type: TRIGGER; Schema: ubec_recipro; Owner: recipro
--

CREATE TRIGGER update_agent_reciprocity_score AFTER INSERT ON ubec_recipro.agent_activity_history FOR EACH ROW EXECUTE FUNCTION ubec_recipro.update_agent_reciprocity_from_activity();


--
-- Name: reward_token_holders update_holding_period_trigger; Type: TRIGGER; Schema: ubec_recipro; Owner: recipro
--

CREATE TRIGGER update_holding_period_trigger BEFORE INSERT OR UPDATE ON ubec_recipro.reward_token_holders FOR EACH ROW EXECUTE FUNCTION ubec_recipro.update_holding_period();


--
-- Name: agent_holon_memberships update_holon_metrics_trigger; Type: TRIGGER; Schema: ubec_recipro; Owner: recipro
--

CREATE TRIGGER update_holon_metrics_trigger AFTER INSERT OR DELETE OR UPDATE ON ubec_recipro.agent_holon_memberships FOR EACH ROW EXECUTE FUNCTION ubec_recipro.update_holon_metrics();


--
-- Name: participant_activities update_participant_timestamp; Type: TRIGGER; Schema: ubec_recipro; Owner: recipro
--

CREATE TRIGGER update_participant_timestamp AFTER INSERT ON ubec_recipro.participant_activities FOR EACH ROW EXECUTE FUNCTION ubec_recipro.update_participant_activity_timestamp();


--
-- Name: agents update_rc_ledger_trigger; Type: TRIGGER; Schema: ubec_recipro; Owner: recipro
--

CREATE TRIGGER update_rc_ledger_trigger AFTER UPDATE ON ubec_recipro.agents FOR EACH ROW WHEN ((old.reciprocity_credits IS DISTINCT FROM new.reciprocity_credits)) EXECUTE FUNCTION ubec_recipro.update_rc_ledger_on_credit_change();


--
-- Name: reward_token_holders update_reward_token_holder_stats_trigger; Type: TRIGGER; Schema: ubec_recipro; Owner: recipro
--

CREATE TRIGGER update_reward_token_holder_stats_trigger BEFORE INSERT OR UPDATE ON ubec_recipro.reward_token_holders FOR EACH ROW EXECUTE FUNCTION ubec_recipro.update_reward_token_holder_stats();


--
-- Name: agent_activity_history agent_activity_history_agent_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agent_activity_history
    ADD CONSTRAINT agent_activity_history_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES ubec_recipro.agents(id);


--
-- Name: agent_benefit_history agent_benefit_history_agent_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agent_benefit_history
    ADD CONSTRAINT agent_benefit_history_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES ubec_recipro.agents(id);


--
-- Name: agent_contribution_history agent_contribution_history_agent_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agent_contribution_history
    ADD CONSTRAINT agent_contribution_history_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES ubec_recipro.agents(id);


--
-- Name: agent_holon_memberships agent_holon_memberships_agent_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agent_holon_memberships
    ADD CONSTRAINT agent_holon_memberships_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES ubec_recipro.agents(id);


--
-- Name: agent_holon_memberships agent_holon_memberships_holon_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agent_holon_memberships
    ADD CONSTRAINT agent_holon_memberships_holon_id_fkey FOREIGN KEY (holon_id) REFERENCES ubec_recipro.holons(id);


--
-- Name: agents agents_participant_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.agents
    ADD CONSTRAINT agents_participant_id_fkey FOREIGN KEY (participant_id) REFERENCES ubec_recipro.participants(id);


--
-- Name: claimable_balances claimable_balances_distribution_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.claimable_balances
    ADD CONSTRAINT claimable_balances_distribution_id_fkey FOREIGN KEY (distribution_id) REFERENCES ubec_recipro.token_distributions(id);


--
-- Name: claimable_balances claimable_balances_participant_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.claimable_balances
    ADD CONSTRAINT claimable_balances_participant_id_fkey FOREIGN KEY (participant_id) REFERENCES ubec_recipro.participants(id);


--
-- Name: evaluation_queue evaluation_queue_agent_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.evaluation_queue
    ADD CONSTRAINT evaluation_queue_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES ubec_recipro.agents(id);


--
-- Name: holonic_metrics holonic_metrics_agent_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.holonic_metrics
    ADD CONSTRAINT holonic_metrics_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES ubec_recipro.agents(id);


--
-- Name: holonic_metrics_history holonic_metrics_history_agent_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.holonic_metrics_history
    ADD CONSTRAINT holonic_metrics_history_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES ubec_recipro.agents(id);


--
-- Name: participant_activities participant_activities_participant_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.participant_activities
    ADD CONSTRAINT participant_activities_participant_id_fkey FOREIGN KEY (participant_id) REFERENCES ubec_recipro.participants(id);


--
-- Name: participant_tiers participant_tiers_participant_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.participant_tiers
    ADD CONSTRAINT participant_tiers_participant_id_fkey FOREIGN KEY (participant_id) REFERENCES ubec_recipro.participants(id);


--
-- Name: participant_tiers participant_tiers_tier_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.participant_tiers
    ADD CONSTRAINT participant_tiers_tier_id_fkey FOREIGN KEY (tier_id) REFERENCES ubec_recipro.loyalty_tiers(id);


--
-- Name: price_history price_history_index_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.price_history
    ADD CONSTRAINT price_history_index_id_fkey FOREIGN KEY (index_id) REFERENCES ubec_recipro.price_indices(id);


--
-- Name: rc_ledger rc_ledger_agent_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.rc_ledger
    ADD CONSTRAINT rc_ledger_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES ubec_recipro.agents(id);


--
-- Name: reciprocity_scores reciprocity_scores_agent_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.reciprocity_scores
    ADD CONSTRAINT reciprocity_scores_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES ubec_recipro.agents(id);


--
-- Name: reciprocity_scores reciprocity_scores_participant_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.reciprocity_scores
    ADD CONSTRAINT reciprocity_scores_participant_id_fkey FOREIGN KEY (participant_id) REFERENCES ubec_recipro.participants(id);


--
-- Name: reciprocity_transactions reciprocity_transactions_account_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.reciprocity_transactions
    ADD CONSTRAINT reciprocity_transactions_account_id_fkey FOREIGN KEY (account_id) REFERENCES ubec_recipro.participants(account_id);


--
-- Name: regenerative_projects regenerative_projects_agent_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.regenerative_projects
    ADD CONSTRAINT regenerative_projects_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES ubec_recipro.agents(id);


--
-- Name: scheduler_job_history scheduler_job_history_job_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.scheduler_job_history
    ADD CONSTRAINT scheduler_job_history_job_id_fkey FOREIGN KEY (job_id) REFERENCES ubec_recipro.scheduler_jobs(id);


--
-- Name: token_distributions token_distributions_participant_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.token_distributions
    ADD CONSTRAINT token_distributions_participant_id_fkey FOREIGN KEY (participant_id) REFERENCES ubec_recipro.participants(id);


--
-- Name: token_prices token_prices_price_history_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.token_prices
    ADD CONSTRAINT token_prices_price_history_id_fkey FOREIGN KEY (price_history_id) REFERENCES ubec_recipro.price_history(id);


--
-- Name: transaction_operations transaction_operations_transaction_id_fkey; Type: FK CONSTRAINT; Schema: ubec_recipro; Owner: recipro
--

ALTER TABLE ONLY ubec_recipro.transaction_operations
    ADD CONSTRAINT transaction_operations_transaction_id_fkey FOREIGN KEY (transaction_id) REFERENCES ubec_recipro.transaction_queue(transaction_id);


--
-- Name: SCHEMA ubec_recipro; Type: ACL; Schema: -; Owner: recipro
--

GRANT ALL ON SCHEMA ubec_recipro TO reward_admin;
GRANT USAGE ON SCHEMA ubec_recipro TO dump_ubec;


--
-- Name: FUNCTION ghstore_in(cstring); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.ghstore_in(cstring) TO recipro;


--
-- Name: FUNCTION ghstore_out(ubec_recipro.ghstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.ghstore_out(ubec_recipro.ghstore) TO recipro;


--
-- Name: FUNCTION hstore_in(cstring); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_in(cstring) TO recipro;


--
-- Name: FUNCTION hstore_out(ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_out(ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hstore_recv(internal); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_recv(internal) TO recipro;


--
-- Name: FUNCTION hstore_send(ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_send(ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hstore_subscript_handler(internal); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_subscript_handler(internal) TO recipro;


--
-- Name: FUNCTION hstore(text[]); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore(text[]) TO recipro;


--
-- Name: FUNCTION hstore_to_json(ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_to_json(ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hstore_to_jsonb(ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_to_jsonb(ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION akeys(ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.akeys(ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION avals(ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.avals(ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION defined(ubec_recipro.hstore, text); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.defined(ubec_recipro.hstore, text) TO recipro;


--
-- Name: FUNCTION delete(ubec_recipro.hstore, text[]); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.delete(ubec_recipro.hstore, text[]) TO recipro;


--
-- Name: FUNCTION delete(ubec_recipro.hstore, text); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.delete(ubec_recipro.hstore, text) TO recipro;


--
-- Name: FUNCTION delete(ubec_recipro.hstore, ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.delete(ubec_recipro.hstore, ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION each(hs ubec_recipro.hstore, OUT key text, OUT value text); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.each(hs ubec_recipro.hstore, OUT key text, OUT value text) TO recipro;


--
-- Name: FUNCTION exist(ubec_recipro.hstore, text); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.exist(ubec_recipro.hstore, text) TO recipro;


--
-- Name: FUNCTION exists_all(ubec_recipro.hstore, text[]); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.exists_all(ubec_recipro.hstore, text[]) TO recipro;


--
-- Name: FUNCTION exists_any(ubec_recipro.hstore, text[]); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.exists_any(ubec_recipro.hstore, text[]) TO recipro;


--
-- Name: FUNCTION fetchval(ubec_recipro.hstore, text); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.fetchval(ubec_recipro.hstore, text) TO recipro;


--
-- Name: FUNCTION ghstore_compress(internal); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.ghstore_compress(internal) TO recipro;


--
-- Name: FUNCTION ghstore_consistent(internal, ubec_recipro.hstore, smallint, oid, internal); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.ghstore_consistent(internal, ubec_recipro.hstore, smallint, oid, internal) TO recipro;


--
-- Name: FUNCTION ghstore_decompress(internal); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.ghstore_decompress(internal) TO recipro;


--
-- Name: FUNCTION ghstore_options(internal); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.ghstore_options(internal) TO recipro;


--
-- Name: FUNCTION ghstore_penalty(internal, internal, internal); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.ghstore_penalty(internal, internal, internal) TO recipro;


--
-- Name: FUNCTION ghstore_picksplit(internal, internal); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.ghstore_picksplit(internal, internal) TO recipro;


--
-- Name: FUNCTION ghstore_same(ubec_recipro.ghstore, ubec_recipro.ghstore, internal); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.ghstore_same(ubec_recipro.ghstore, ubec_recipro.ghstore, internal) TO recipro;


--
-- Name: FUNCTION ghstore_union(internal, internal); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.ghstore_union(internal, internal) TO recipro;


--
-- Name: FUNCTION gin_consistent_hstore(internal, smallint, ubec_recipro.hstore, integer, internal, internal); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.gin_consistent_hstore(internal, smallint, ubec_recipro.hstore, integer, internal, internal) TO recipro;


--
-- Name: FUNCTION gin_extract_hstore(ubec_recipro.hstore, internal); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.gin_extract_hstore(ubec_recipro.hstore, internal) TO recipro;


--
-- Name: FUNCTION gin_extract_hstore_query(ubec_recipro.hstore, internal, smallint, internal, internal); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.gin_extract_hstore_query(ubec_recipro.hstore, internal, smallint, internal, internal) TO recipro;


--
-- Name: FUNCTION hs_concat(ubec_recipro.hstore, ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hs_concat(ubec_recipro.hstore, ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hs_contained(ubec_recipro.hstore, ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hs_contained(ubec_recipro.hstore, ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hs_contains(ubec_recipro.hstore, ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hs_contains(ubec_recipro.hstore, ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hstore(record); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore(record) TO recipro;


--
-- Name: FUNCTION hstore(text[], text[]); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore(text[], text[]) TO recipro;


--
-- Name: FUNCTION hstore(text, text); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore(text, text) TO recipro;


--
-- Name: FUNCTION hstore_cmp(ubec_recipro.hstore, ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_cmp(ubec_recipro.hstore, ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hstore_eq(ubec_recipro.hstore, ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_eq(ubec_recipro.hstore, ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hstore_ge(ubec_recipro.hstore, ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_ge(ubec_recipro.hstore, ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hstore_gt(ubec_recipro.hstore, ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_gt(ubec_recipro.hstore, ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hstore_hash(ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_hash(ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hstore_hash_extended(ubec_recipro.hstore, bigint); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_hash_extended(ubec_recipro.hstore, bigint) TO recipro;


--
-- Name: FUNCTION hstore_le(ubec_recipro.hstore, ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_le(ubec_recipro.hstore, ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hstore_lt(ubec_recipro.hstore, ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_lt(ubec_recipro.hstore, ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hstore_ne(ubec_recipro.hstore, ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_ne(ubec_recipro.hstore, ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hstore_to_array(ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_to_array(ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hstore_to_json_loose(ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_to_json_loose(ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hstore_to_jsonb_loose(ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_to_jsonb_loose(ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hstore_to_matrix(ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_to_matrix(ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION hstore_version_diag(ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.hstore_version_diag(ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION isdefined(ubec_recipro.hstore, text); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.isdefined(ubec_recipro.hstore, text) TO recipro;


--
-- Name: FUNCTION isexists(ubec_recipro.hstore, text); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.isexists(ubec_recipro.hstore, text) TO recipro;


--
-- Name: FUNCTION populate_record(anyelement, ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.populate_record(anyelement, ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION skeys(ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.skeys(ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION slice(ubec_recipro.hstore, text[]); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.slice(ubec_recipro.hstore, text[]) TO recipro;


--
-- Name: FUNCTION slice_array(ubec_recipro.hstore, text[]); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.slice_array(ubec_recipro.hstore, text[]) TO recipro;


--
-- Name: FUNCTION svals(ubec_recipro.hstore); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.svals(ubec_recipro.hstore) TO recipro;


--
-- Name: FUNCTION tconvert(text, text); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.tconvert(text, text) TO recipro;


--
-- Name: FUNCTION uuid_generate_v1(); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.uuid_generate_v1() TO recipro;


--
-- Name: FUNCTION uuid_generate_v1mc(); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.uuid_generate_v1mc() TO recipro;


--
-- Name: FUNCTION uuid_generate_v3(namespace uuid, name text); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.uuid_generate_v3(namespace uuid, name text) TO recipro;


--
-- Name: FUNCTION uuid_generate_v4(); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.uuid_generate_v4() TO recipro;


--
-- Name: FUNCTION uuid_generate_v5(namespace uuid, name text); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.uuid_generate_v5(namespace uuid, name text) TO recipro;


--
-- Name: FUNCTION uuid_nil(); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.uuid_nil() TO recipro;


--
-- Name: FUNCTION uuid_ns_dns(); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.uuid_ns_dns() TO recipro;


--
-- Name: FUNCTION uuid_ns_oid(); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.uuid_ns_oid() TO recipro;


--
-- Name: FUNCTION uuid_ns_url(); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.uuid_ns_url() TO recipro;


--
-- Name: FUNCTION uuid_ns_x500(); Type: ACL; Schema: ubec_recipro; Owner: postgres
--

GRANT ALL ON FUNCTION ubec_recipro.uuid_ns_x500() TO recipro;


--
-- Name: TABLE agent_activity_history; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.agent_activity_history TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.agent_activity_history TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.agent_activity_history TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.agent_activity_history TO dump_ubec;


--
-- Name: SEQUENCE agent_activity_history_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.agent_activity_history_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.agent_activity_history_id_seq TO reward_admin;


--
-- Name: TABLE agent_benefit_history; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.agent_benefit_history TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.agent_benefit_history TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.agent_benefit_history TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.agent_benefit_history TO dump_ubec;


--
-- Name: SEQUENCE agent_benefit_history_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.agent_benefit_history_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.agent_benefit_history_id_seq TO reward_admin;


--
-- Name: TABLE agent_contribution_history; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.agent_contribution_history TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.agent_contribution_history TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.agent_contribution_history TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.agent_contribution_history TO dump_ubec;


--
-- Name: SEQUENCE agent_contribution_history_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.agent_contribution_history_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.agent_contribution_history_id_seq TO reward_admin;


--
-- Name: TABLE agent_holon_memberships; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.agent_holon_memberships TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.agent_holon_memberships TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.agent_holon_memberships TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.agent_holon_memberships TO dump_ubec;


--
-- Name: SEQUENCE agent_holon_memberships_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.agent_holon_memberships_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.agent_holon_memberships_id_seq TO reward_admin;


--
-- Name: TABLE agents; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.agents TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.agents TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.agents TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.agents TO dump_ubec;


--
-- Name: TABLE holons; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.holons TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.holons TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.holons TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.holons TO dump_ubec;


--
-- Name: TABLE agent_holon_view; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.agent_holon_view TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.agent_holon_view TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.agent_holon_view TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.agent_holon_view TO dump_ubec;


--
-- Name: SEQUENCE agents_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.agents_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.agents_id_seq TO reward_admin;


--
-- Name: TABLE api_rate_limits; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.api_rate_limits TO dump_ubec;


--
-- Name: TABLE asset_holder_analysis; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.asset_holder_analysis TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.asset_holder_analysis TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.asset_holder_analysis TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.asset_holder_analysis TO dump_ubec;


--
-- Name: SEQUENCE asset_holder_analysis_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.asset_holder_analysis_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.asset_holder_analysis_id_seq TO reward_admin;


--
-- Name: TABLE asset_holders; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.asset_holders TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.asset_holders TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.asset_holders TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.asset_holders TO dump_ubec;


--
-- Name: TABLE asset_holder_analysis_view; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.asset_holder_analysis_view TO dump_ubec;


--
-- Name: SEQUENCE asset_holders_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.asset_holders_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.asset_holders_id_seq TO reward_admin;


--
-- Name: TABLE audit_log; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.audit_log TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.audit_log TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.audit_log TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.audit_log TO dump_ubec;


--
-- Name: SEQUENCE audit_log_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.audit_log_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.audit_log_id_seq TO reward_admin;


--
-- Name: TABLE claimable_balances; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.claimable_balances TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.claimable_balances TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.claimable_balances TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.claimable_balances TO dump_ubec;


--
-- Name: SEQUENCE claimable_balances_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.claimable_balances_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.claimable_balances_id_seq TO reward_admin;


--
-- Name: TABLE distribution_history; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.distribution_history TO dump_ubec;


--
-- Name: TABLE evaluation_queue; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.evaluation_queue TO dump_ubec;


--
-- Name: TABLE holonic_metrics; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.holonic_metrics TO dump_ubec;


--
-- Name: TABLE participants; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.participants TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.participants TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.participants TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.participants TO dump_ubec;


--
-- Name: TABLE evaluation_queue_view; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.evaluation_queue_view TO dump_ubec;


--
-- Name: TABLE exchange_metrics; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.exchange_metrics TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.exchange_metrics TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.exchange_metrics TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.exchange_metrics TO dump_ubec;


--
-- Name: SEQUENCE exchange_metrics_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.exchange_metrics_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.exchange_metrics_id_seq TO reward_admin;


--
-- Name: TABLE exchange_metrics_view; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.exchange_metrics_view TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.exchange_metrics_view TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.exchange_metrics_view TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.exchange_metrics_view TO dump_ubec;


--
-- Name: TABLE transaction_operations; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.transaction_operations TO dump_ubec;


--
-- Name: TABLE holder_discovery_history; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.holder_discovery_history TO dump_ubec;


--
-- Name: TABLE holonic_category_distribution; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.holonic_category_distribution TO dump_ubec;


--
-- Name: TABLE holonic_evaluation_view; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.holonic_evaluation_view TO dump_ubec;


--
-- Name: TABLE holonic_metrics_history; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.holonic_metrics_history TO dump_ubec;


--
-- Name: SEQUENCE holons_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.holons_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.holons_id_seq TO reward_admin;


--
-- Name: TABLE liquidity_pool_owners; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.liquidity_pool_owners TO dump_ubec;


--
-- Name: TABLE liquidity_pools; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.liquidity_pools TO dump_ubec;


--
-- Name: TABLE loyalty_tiers; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.loyalty_tiers TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.loyalty_tiers TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.loyalty_tiers TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.loyalty_tiers TO dump_ubec;


--
-- Name: SEQUENCE loyalty_tiers_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.loyalty_tiers_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.loyalty_tiers_id_seq TO reward_admin;


--
-- Name: TABLE participant_activities; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.participant_activities TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.participant_activities TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.participant_activities TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.participant_activities TO dump_ubec;


--
-- Name: SEQUENCE participant_activities_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.participant_activities_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.participant_activities_id_seq TO reward_admin;


--
-- Name: TABLE participant_relationships; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.participant_relationships TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.participant_relationships TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.participant_relationships TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.participant_relationships TO dump_ubec;


--
-- Name: SEQUENCE participant_relationships_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.participant_relationships_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.participant_relationships_id_seq TO reward_admin;


--
-- Name: TABLE participant_tiers; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.participant_tiers TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.participant_tiers TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.participant_tiers TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.participant_tiers TO dump_ubec;


--
-- Name: TABLE reciprocity_scores; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.reciprocity_scores TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.reciprocity_scores TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.reciprocity_scores TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.reciprocity_scores TO dump_ubec;


--
-- Name: TABLE system_configuration; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.system_configuration TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.system_configuration TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.system_configuration TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.system_configuration TO dump_ubec;


--
-- Name: TABLE token_distributions; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.token_distributions TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.token_distributions TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.token_distributions TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.token_distributions TO dump_ubec;


--
-- Name: TABLE participant_status_view; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.participant_status_view TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.participant_status_view TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.participant_status_view TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.participant_status_view TO dump_ubec;


--
-- Name: SEQUENCE participant_tiers_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.participant_tiers_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.participant_tiers_id_seq TO reward_admin;


--
-- Name: SEQUENCE participants_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.participants_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.participants_id_seq TO reward_admin;


--
-- Name: TABLE price_history; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.price_history TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.price_history TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.price_history TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.price_history TO dump_ubec;


--
-- Name: SEQUENCE price_history_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.price_history_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.price_history_id_seq TO reward_admin;


--
-- Name: TABLE price_indices; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.price_indices TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.price_indices TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.price_indices TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.price_indices TO dump_ubec;


--
-- Name: TABLE token_prices; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.token_prices TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.token_prices TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.token_prices TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.token_prices TO dump_ubec;


--
-- Name: TABLE price_history_view; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.price_history_view TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.price_history_view TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.price_history_view TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.price_history_view TO dump_ubec;


--
-- Name: SEQUENCE price_indices_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.price_indices_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.price_indices_id_seq TO reward_admin;


--
-- Name: TABLE rc_ledger; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.rc_ledger TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.rc_ledger TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.rc_ledger TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.rc_ledger TO dump_ubec;


--
-- Name: SEQUENCE rc_ledger_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.rc_ledger_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.rc_ledger_id_seq TO reward_admin;


--
-- Name: TABLE rc_ledger_summary; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.rc_ledger_summary TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.rc_ledger_summary TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.rc_ledger_summary TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.rc_ledger_summary TO dump_ubec;


--
-- Name: TABLE reciprocity_health; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.reciprocity_health TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.reciprocity_health TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.reciprocity_health TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.reciprocity_health TO dump_ubec;


--
-- Name: SEQUENCE reciprocity_health_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.reciprocity_health_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.reciprocity_health_id_seq TO reward_admin;


--
-- Name: TABLE reciprocity_health_view; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.reciprocity_health_view TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.reciprocity_health_view TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.reciprocity_health_view TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.reciprocity_health_view TO dump_ubec;


--
-- Name: SEQUENCE reciprocity_scores_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.reciprocity_scores_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.reciprocity_scores_id_seq TO reward_admin;


--
-- Name: TABLE reciprocity_transactions; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.reciprocity_transactions TO dump_ubec;


--
-- Name: TABLE regenerative_projects; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.regenerative_projects TO dump_ubec;


--
-- Name: TABLE reward_token_holders; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.reward_token_holders TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.reward_token_holders TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.reward_token_holders TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.reward_token_holders TO dump_ubec;


--
-- Name: TABLE reward_token_holder_view; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.reward_token_holder_view TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.reward_token_holder_view TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.reward_token_holder_view TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.reward_token_holder_view TO dump_ubec;


--
-- Name: SEQUENCE reward_token_holders_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.reward_token_holders_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.reward_token_holders_id_seq TO reward_admin;


--
-- Name: TABLE scheduler_job_history; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.scheduler_job_history TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.scheduler_job_history TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.scheduler_job_history TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.scheduler_job_history TO dump_ubec;


--
-- Name: SEQUENCE scheduler_job_history_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.scheduler_job_history_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.scheduler_job_history_id_seq TO reward_admin;


--
-- Name: TABLE scheduler_jobs; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.scheduler_jobs TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.scheduler_jobs TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.scheduler_jobs TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.scheduler_jobs TO dump_ubec;


--
-- Name: SEQUENCE scheduler_jobs_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.scheduler_jobs_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.scheduler_jobs_id_seq TO reward_admin;


--
-- Name: TABLE setup_tracking; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.setup_tracking TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.setup_tracking TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.setup_tracking TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.setup_tracking TO dump_ubec;


--
-- Name: TABLE sync_jobs; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.sync_jobs TO dump_ubec;


--
-- Name: TABLE sync_status; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.sync_status TO dump_ubec;


--
-- Name: SEQUENCE token_distributions_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.token_distributions_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.token_distributions_id_seq TO reward_admin;


--
-- Name: SEQUENCE token_prices_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.token_prices_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.token_prices_id_seq TO reward_admin;


--
-- Name: TABLE transaction_queue; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.transaction_queue TO dump_ubec;


--
-- Name: TABLE transaction_queue_status; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.transaction_queue_status TO dump_ubec;


--
-- Name: TABLE transfer_recommendations; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.transfer_recommendations TO reward_read_only;
GRANT SELECT,INSERT,UPDATE ON TABLE ubec_recipro.transfer_recommendations TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.transfer_recommendations TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.transfer_recommendations TO dump_ubec;


--
-- Name: SEQUENCE transfer_recommendations_id_seq; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT,USAGE ON SEQUENCE ubec_recipro.transfer_recommendations_id_seq TO reward_data_writer;
GRANT ALL ON SEQUENCE ubec_recipro.transfer_recommendations_id_seq TO reward_admin;


--
-- Name: TABLE transfer_recommendations_view; Type: ACL; Schema: ubec_recipro; Owner: recipro
--

GRANT SELECT ON TABLE ubec_recipro.transfer_recommendations_view TO reward_read_only;
GRANT SELECT ON TABLE ubec_recipro.transfer_recommendations_view TO reward_data_writer;
GRANT ALL ON TABLE ubec_recipro.transfer_recommendations_view TO reward_admin;
GRANT SELECT ON TABLE ubec_recipro.transfer_recommendations_view TO dump_ubec;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: ubec_recipro; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA ubec_recipro GRANT ALL ON SEQUENCES  TO recipro;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: ubec_recipro; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA ubec_recipro GRANT ALL ON FUNCTIONS  TO recipro;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: ubec_recipro; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA ubec_recipro GRANT ALL ON TABLES  TO recipro;


--
-- PostgreSQL database dump complete
--

