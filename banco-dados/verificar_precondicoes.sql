-- PIXELSHOP - Verificacao previa obrigatoria antes do DDL/carga.
-- Interrompe a execucao com erro se a sessao nao estiver em PIXELSHOP / XEPDB1
-- ou se o esquema ja possuir objetos de usuario.

DECLARE
    v_session_user   VARCHAR2(128) := SYS_CONTEXT('USERENV', 'SESSION_USER');
    v_current_schema VARCHAR2(128) := SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA');
    v_con_name       VARCHAR2(128) := SYS_CONTEXT('USERENV', 'CON_NAME');
    v_qtd_objetos    NUMBER := 0;
BEGIN
    IF v_session_user <> 'PIXELSHOP' THEN
        RAISE_APPLICATION_ERROR(
            -20001,
            'Abortado: SESSION_USER esperado PIXELSHOP, atual=' || NVL(v_session_user, 'NULL')
        );
    END IF;

    IF v_current_schema <> 'PIXELSHOP' THEN
        RAISE_APPLICATION_ERROR(
            -20002,
            'Abortado: CURRENT_SCHEMA esperado PIXELSHOP, atual=' || NVL(v_current_schema, 'NULL')
        );
    END IF;

    IF v_con_name <> 'XEPDB1' THEN
        RAISE_APPLICATION_ERROR(
            -20003,
            'Abortado: CON_NAME esperado XEPDB1, atual=' || NVL(v_con_name, 'NULL')
        );
    END IF;

    SELECT COUNT(*) INTO v_qtd_objetos FROM USER_OBJECTS;
    IF v_qtd_objetos > 0 THEN
        RAISE_APPLICATION_ERROR(
            -20004,
            'Abortado: esquema PIXELSHOP nao esta vazio (' || v_qtd_objetos || ' objeto(s) encontrado(s)).'
        );
    END IF;

    DBMS_OUTPUT.PUT_LINE(
        'Pre-condicoes OK: SESSION_USER=' || v_session_user
        || ', CURRENT_SCHEMA=' || v_current_schema
        || ', CON_NAME=' || v_con_name
        || ', USER_OBJECTS=0'
    );
END;
/
