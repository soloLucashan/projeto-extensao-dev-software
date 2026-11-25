-- PIXELSHOP - Script SQL*Plus de instalacao controlada (XEPDB1 / PIXELSHOP)
-- NAO executa DROP, TRUNCATE, DELETE ou CREATE USER.
--
-- Execute a partir do diretorio banco-dados\ para garantir a resolucao relativa
-- dos scripts chamados com @@:
--   @instalar_pixelshop.sql
--
-- ATENCAO: DDL no Oracle realiza commit implicito e NAO e desfeito por ROLLBACK.
-- Em caso de falha parcial durante create_tables.sql, interrompa e diagnostique
-- manualmente antes de qualquer nova tentativa.

WHENEVER SQLERROR EXIT SQL.SQLCODE ROLLBACK
WHENEVER OSERROR EXIT FAILURE ROLLBACK

SET DEFINE OFF
SET ECHO ON
SET SERVEROUTPUT ON

@@verificar_precondicoes.sql
@@create_tables.sql
@@insert_data.sql
@@verificar_pos_carga.sql
