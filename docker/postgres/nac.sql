--
-- PostgreSQL database dump
--

-- Dumped from database version 11.7 (Debian 11.7-1.pgdg90+1)
-- Dumped by pg_dump version 11.7 (Debian 11.7-1.pgdg90+1)

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

SET default_tablespace = '';

SET default_with_oids = false;

--
--
--

CREATE EXTENSION pg_cron;
SELECT cron.schedule('Cleanup raddacct', '0 23 * * *', $$DELETE FROM radacct WHERE acctstoptime < (now() - '30 days'::interval)$$);
SELECT cron.schedule('Reindex racct', '30 23 * * *', 'REINDEX TABLE radacct');

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: cnaas
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO cnaas;

--
-- Name: device_oui_id_seq; Type: SEQUENCE; Schema: public; Owner: cnaas
--

CREATE SEQUENCE public.device_oui_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.device_oui_id_seq OWNER TO cnaas;

--
-- Name: device_oui; Type: TABLE; Schema: public; Owner: cnaas
--

CREATE TABLE public.device_oui (
    id integer DEFAULT nextval('public.device_oui_id_seq'::regclass) NOT NULL,
    oui text NOT NULL,
    vlan text,
    description text
);


ALTER TABLE public.device_oui OWNER TO cnaas;

--
-- Name: device_oui_id_seq1; Type: SEQUENCE; Schema: public; Owner: cnaas
--

CREATE SEQUENCE public.device_oui_id_seq1
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.device_oui_id_seq1 OWNER TO cnaas;

--
-- Name: device_oui_id_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: cnaas
--

ALTER SEQUENCE public.device_oui_id_seq1 OWNED BY public.device_oui.id;


--
-- Name: nas; Type: TABLE; Schema: public; Owner: cnaas
--

CREATE TABLE public.nas (
    id integer NOT NULL,
    nasname text NOT NULL,
    shortname text NOT NULL,
    type text DEFAULT 'other'::text NOT NULL,
    ports integer,
    secret text NOT NULL,
    server text,
    community text,
    description text
);


ALTER TABLE public.nas OWNER TO cnaas;

--
-- Name: nas_id_seq; Type: SEQUENCE; Schema: public; Owner: cnaas
--

CREATE SEQUENCE public.nas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.nas_id_seq OWNER TO cnaas;

--
-- Name: nas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cnaas
--

ALTER SEQUENCE public.nas_id_seq OWNED BY public.nas.id;


--
-- Name: nas_port_id_seq; Type: SEQUENCE; Schema: public; Owner: cnaas
--

CREATE SEQUENCE public.nas_port_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.nas_port_id_seq OWNER TO cnaas;

--
-- Name: nas_port; Type: TABLE; Schema: public; Owner: cnaas
--

CREATE TABLE public.nas_port (
    id integer DEFAULT nextval('public.nas_port_id_seq'::regclass) NOT NULL,
    username character varying(64) NOT NULL,
    nas_identifier character varying(64),
    nas_port_id character varying(64),
    calling_station_id character varying(64),
    called_station_id character varying(64),
    nas_ip_address character varying(64)
);


ALTER TABLE public.nas_port OWNER TO cnaas;

--
-- Name: radacct; Type: TABLE; Schema: public; Owner: cnaas
--

CREATE TABLE public.radacct (
    radacctid bigint NOT NULL,
    acctsessionid text NOT NULL,
    acctuniqueid text NOT NULL,
    username text,
    groupname text,
    realm text,
    nasipaddress inet NOT NULL,
    nasportid text,
    nasporttype text,
    acctstarttime timestamp with time zone,
    acctupdatetime timestamp with time zone,
    acctstoptime timestamp with time zone,
    acctinterval bigint,
    acctsessiontime bigint,
    acctauthentic text,
    connectinfo_start text,
    connectinfo_stop text,
    acctinputoctets bigint,
    acctoutputoctets bigint,
    calledstationid text,
    callingstationid text,
    acctterminatecause text,
    servicetype text,
    framedprotocol text,
    framedipaddress inet
);


ALTER TABLE public.radacct OWNER TO cnaas;

--
-- Name: radacct_radacctid_seq; Type: SEQUENCE; Schema: public; Owner: cnaas
--

CREATE SEQUENCE public.radacct_radacctid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radacct_radacctid_seq OWNER TO cnaas;

--
-- Name: radacct_radacctid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cnaas
--

ALTER SEQUENCE public.radacct_radacctid_seq OWNED BY public.radacct.radacctid;


--
-- Name: radcheck; Type: TABLE; Schema: public; Owner: cnaas
--

CREATE TABLE public.radcheck (
    id integer NOT NULL,
    username text DEFAULT ''::text NOT NULL,
    attribute text DEFAULT ''::text NOT NULL,
    op character varying(2) DEFAULT '=='::character varying NOT NULL,
    value text DEFAULT ''::text NOT NULL
);


ALTER TABLE public.radcheck OWNER TO cnaas;

--
-- Name: radcheck_id_seq; Type: SEQUENCE; Schema: public; Owner: cnaas
--

CREATE SEQUENCE public.radcheck_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radcheck_id_seq OWNER TO cnaas;

--
-- Name: radcheck_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cnaas
--

ALTER SEQUENCE public.radcheck_id_seq OWNED BY public.radcheck.id;


--
-- Name: radgroupcheck; Type: TABLE; Schema: public; Owner: cnaas
--

CREATE TABLE public.radgroupcheck (
    id integer NOT NULL,
    groupname text DEFAULT ''::text NOT NULL,
    attribute text DEFAULT ''::text NOT NULL,
    op character varying(2) DEFAULT '=='::character varying NOT NULL,
    value text DEFAULT ''::text NOT NULL
);


ALTER TABLE public.radgroupcheck OWNER TO cnaas;

--
-- Name: radgroupcheck_id_seq; Type: SEQUENCE; Schema: public; Owner: cnaas
--

CREATE SEQUENCE public.radgroupcheck_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radgroupcheck_id_seq OWNER TO cnaas;

--
-- Name: radgroupcheck_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cnaas
--

ALTER SEQUENCE public.radgroupcheck_id_seq OWNED BY public.radgroupcheck.id;


--
-- Name: radgroupreply; Type: TABLE; Schema: public; Owner: cnaas
--

CREATE TABLE public.radgroupreply (
    id integer NOT NULL,
    groupname text DEFAULT ''::text NOT NULL,
    attribute text DEFAULT ''::text NOT NULL,
    op character varying(2) DEFAULT '='::character varying NOT NULL,
    value text DEFAULT ''::text NOT NULL
);


ALTER TABLE public.radgroupreply OWNER TO cnaas;

--
-- Name: radgroupreply_id_seq; Type: SEQUENCE; Schema: public; Owner: cnaas
--

CREATE SEQUENCE public.radgroupreply_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radgroupreply_id_seq OWNER TO cnaas;

--
-- Name: radgroupreply_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cnaas
--

ALTER SEQUENCE public.radgroupreply_id_seq OWNED BY public.radgroupreply.id;


--
-- Name: radpostauth; Type: TABLE; Schema: public; Owner: cnaas
--

CREATE TABLE public.radpostauth (
    id bigint NOT NULL,
    username text NOT NULL,
    pass text,
    reply text,
    calledstationid text,
    callingstationid text,
    authdate timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.radpostauth OWNER TO cnaas;

--
-- Name: radpostauth_id_seq; Type: SEQUENCE; Schema: public; Owner: cnaas
--

CREATE SEQUENCE public.radpostauth_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radpostauth_id_seq OWNER TO cnaas;

--
-- Name: radpostauth_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cnaas
--

ALTER SEQUENCE public.radpostauth_id_seq OWNED BY public.radpostauth.id;


--
-- Name: radreply; Type: TABLE; Schema: public; Owner: cnaas
--

CREATE TABLE public.radreply (
    id integer NOT NULL,
    username text DEFAULT ''::text NOT NULL,
    attribute text DEFAULT ''::text NOT NULL,
    op character varying(2) DEFAULT '='::character varying NOT NULL,
    value text DEFAULT ''::text NOT NULL
);


ALTER TABLE public.radreply OWNER TO cnaas;

--
-- Name: radreply_id_seq; Type: SEQUENCE; Schema: public; Owner: cnaas
--

CREATE SEQUENCE public.radreply_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radreply_id_seq OWNER TO cnaas;

--
-- Name: radreply_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cnaas
--

ALTER SEQUENCE public.radreply_id_seq OWNED BY public.radreply.id;


--
-- Name: radusergroup; Type: TABLE; Schema: public; Owner: cnaas
--

CREATE TABLE public.radusergroup (
    id integer NOT NULL,
    username text DEFAULT ''::text NOT NULL,
    groupname text DEFAULT ''::text NOT NULL,
    priority integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.radusergroup OWNER TO cnaas;

--
-- Name: radusergroup_id_seq; Type: SEQUENCE; Schema: public; Owner: cnaas
--

CREATE SEQUENCE public.radusergroup_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.radusergroup_id_seq OWNER TO cnaas;

--
-- Name: radusergroup_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cnaas
--

ALTER SEQUENCE public.radusergroup_id_seq OWNED BY public.radusergroup.id;


--
-- Name: nas id; Type: DEFAULT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.nas ALTER COLUMN id SET DEFAULT nextval('public.nas_id_seq'::regclass);


--
-- Name: radacct radacctid; Type: DEFAULT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.radacct ALTER COLUMN radacctid SET DEFAULT nextval('public.radacct_radacctid_seq'::regclass);


--
-- Name: radcheck id; Type: DEFAULT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.radcheck ALTER COLUMN id SET DEFAULT nextval('public.radcheck_id_seq'::regclass);


--
-- Name: radgroupcheck id; Type: DEFAULT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.radgroupcheck ALTER COLUMN id SET DEFAULT nextval('public.radgroupcheck_id_seq'::regclass);


--
-- Name: radgroupreply id; Type: DEFAULT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.radgroupreply ALTER COLUMN id SET DEFAULT nextval('public.radgroupreply_id_seq'::regclass);


--
-- Name: radpostauth id; Type: DEFAULT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.radpostauth ALTER COLUMN id SET DEFAULT nextval('public.radpostauth_id_seq'::regclass);


--
-- Name: radreply id; Type: DEFAULT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.radreply ALTER COLUMN id SET DEFAULT nextval('public.radreply_id_seq'::regclass);


--
-- Name: radusergroup id; Type: DEFAULT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.radusergroup ALTER COLUMN id SET DEFAULT nextval('public.radusergroup_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: cnaas
--

COPY public.alembic_version (version_num) FROM stdin;
1e4142701fbb
\.


--
-- Data for Name: device_oui; Type: TABLE DATA; Schema: public; Owner: cnaas
--

COPY public.device_oui (id, oui, vlan, description) FROM stdin;
\.


--
-- Data for Name: nas; Type: TABLE DATA; Schema: public; Owner: cnaas
--

COPY public.nas (id, nasname, shortname, type, ports, secret, server, community, description) FROM stdin;
\.


--
-- Data for Name: nas_port; Type: TABLE DATA; Schema: public; Owner: cnaas
--

COPY public.nas_port (id, username, nas_identifier, nas_port_id, calling_station_id, called_station_id, nas_ip_address) FROM stdin;
\.


--
-- Data for Name: radacct; Type: TABLE DATA; Schema: public; Owner: cnaas
--

COPY public.radacct (radacctid, acctsessionid, acctuniqueid, username, groupname, realm, nasipaddress, nasportid, nasporttype, acctstarttime, acctupdatetime, acctstoptime, acctinterval, acctsessiontime, acctauthentic, connectinfo_start, connectinfo_stop, acctinputoctets, acctoutputoctets, calledstationid, callingstationid, acctterminatecause, servicetype, framedprotocol, framedipaddress) FROM stdin;
\.


--
-- Data for Name: radcheck; Type: TABLE DATA; Schema: public; Owner: cnaas
--

COPY public.radcheck (id, username, attribute, op, value) FROM stdin;
\.


--
-- Data for Name: radgroupcheck; Type: TABLE DATA; Schema: public; Owner: cnaas
--

COPY public.radgroupcheck (id, groupname, attribute, op, value) FROM stdin;
\.


--
-- Data for Name: radgroupreply; Type: TABLE DATA; Schema: public; Owner: cnaas
--

COPY public.radgroupreply (id, groupname, attribute, op, value) FROM stdin;
\.


--
-- Data for Name: radpostauth; Type: TABLE DATA; Schema: public; Owner: cnaas
--

COPY public.radpostauth (id, username, pass, reply, calledstationid, callingstationid, authdate) FROM stdin;
\.


--
-- Data for Name: radreply; Type: TABLE DATA; Schema: public; Owner: cnaas
--

COPY public.radreply (id, username, attribute, op, value) FROM stdin;
\.


--
-- Data for Name: radusergroup; Type: TABLE DATA; Schema: public; Owner: cnaas
--

COPY public.radusergroup (id, username, groupname, priority) FROM stdin;
\.


--
-- Name: device_oui_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cnaas
--

SELECT pg_catalog.setval('public.device_oui_id_seq', 1, true);


--
-- Name: device_oui_id_seq1; Type: SEQUENCE SET; Schema: public; Owner: cnaas
--

SELECT pg_catalog.setval('public.device_oui_id_seq1', 1, false);


--
-- Name: nas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cnaas
--

SELECT pg_catalog.setval('public.nas_id_seq', 1, false);


--
-- Name: nas_port_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cnaas
--

SELECT pg_catalog.setval('public.nas_port_id_seq', 1, true);


--
-- Name: radacct_radacctid_seq; Type: SEQUENCE SET; Schema: public; Owner: cnaas
--

SELECT pg_catalog.setval('public.radacct_radacctid_seq', 1, false);


--
-- Name: radcheck_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cnaas
--

SELECT pg_catalog.setval('public.radcheck_id_seq', 1, true);


--
-- Name: radgroupcheck_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cnaas
--

SELECT pg_catalog.setval('public.radgroupcheck_id_seq', 1, false);


--
-- Name: radgroupreply_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cnaas
--

SELECT pg_catalog.setval('public.radgroupreply_id_seq', 1, false);


--
-- Name: radpostauth_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cnaas
--

SELECT pg_catalog.setval('public.radpostauth_id_seq', 99187, true);


--
-- Name: radreply_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cnaas
--

SELECT pg_catalog.setval('public.radreply_id_seq', 1002, true);


--
-- Name: radusergroup_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cnaas
--

SELECT pg_catalog.setval('public.radusergroup_id_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: device_oui device_oui_pkey; Type: CONSTRAINT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.device_oui
    ADD CONSTRAINT device_oui_pkey PRIMARY KEY (id);


--
-- Name: nas nas_pkey; Type: CONSTRAINT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.nas
    ADD CONSTRAINT nas_pkey PRIMARY KEY (id);


--
-- Name: radacct radacct_acctuniqueid_key; Type: CONSTRAINT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.radacct
    ADD CONSTRAINT radacct_acctuniqueid_key UNIQUE (acctuniqueid);


--
-- Name: radacct radacct_pkey; Type: CONSTRAINT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.radacct
    ADD CONSTRAINT radacct_pkey PRIMARY KEY (radacctid);


--
-- Name: radcheck radcheck_pkey; Type: CONSTRAINT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.radcheck
    ADD CONSTRAINT radcheck_pkey PRIMARY KEY (id);


--
-- Name: radgroupcheck radgroupcheck_pkey; Type: CONSTRAINT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.radgroupcheck
    ADD CONSTRAINT radgroupcheck_pkey PRIMARY KEY (id);


--
-- Name: radgroupreply radgroupreply_pkey; Type: CONSTRAINT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.radgroupreply
    ADD CONSTRAINT radgroupreply_pkey PRIMARY KEY (id);


--
-- Name: radpostauth radpostauth_pkey; Type: CONSTRAINT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.radpostauth
    ADD CONSTRAINT radpostauth_pkey PRIMARY KEY (id);


--
-- Name: radreply radreply_pkey; Type: CONSTRAINT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.radreply
    ADD CONSTRAINT radreply_pkey PRIMARY KEY (id);


--
-- Name: radusergroup radusergroup_pkey; Type: CONSTRAINT; Schema: public; Owner: cnaas
--

ALTER TABLE ONLY public.radusergroup
    ADD CONSTRAINT radusergroup_pkey PRIMARY KEY (id);


--
-- Name: nas_nasname; Type: INDEX; Schema: public; Owner: cnaas
--

CREATE INDEX nas_nasname ON public.nas USING btree (nasname);


--
-- Name: radacct_active_session_idx; Type: INDEX; Schema: public; Owner: cnaas
--

CREATE INDEX radacct_active_session_idx ON public.radacct USING btree (acctuniqueid) WHERE (acctstoptime IS NULL);


--
-- Name: radacct_bulk_close; Type: INDEX; Schema: public; Owner: cnaas
--

CREATE INDEX radacct_bulk_close ON public.radacct USING btree (nasipaddress, acctstarttime) WHERE (acctstoptime IS NULL);


--
-- Name: radacct_start_user_idx; Type: INDEX; Schema: public; Owner: cnaas
--

CREATE INDEX radacct_start_user_idx ON public.radacct USING btree (acctstarttime, username);


--
-- Name: radcheck_username; Type: INDEX; Schema: public; Owner: cnaas
--

CREATE INDEX radcheck_username ON public.radcheck USING btree (username, attribute);


--
-- Name: radgroupcheck_groupname; Type: INDEX; Schema: public; Owner: cnaas
--

CREATE INDEX radgroupcheck_groupname ON public.radgroupcheck USING btree (groupname, attribute);


--
-- Name: radgroupreply_groupname; Type: INDEX; Schema: public; Owner: cnaas
--

CREATE INDEX radgroupreply_groupname ON public.radgroupreply USING btree (groupname, attribute);


--
-- Name: radreply_username; Type: INDEX; Schema: public; Owner: cnaas
--

CREATE INDEX radreply_username ON public.radreply USING btree (username, attribute);


--
-- Name: radusergroup_username; Type: INDEX; Schema: public; Owner: cnaas
--

CREATE INDEX radusergroup_username ON public.radusergroup USING btree (username);


--
-- PostgreSQL database dump complete
--
