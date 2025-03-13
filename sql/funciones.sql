CREATE OR REPLACE FUNCTION Fecha_valida(FECHA_VUELO DATE) 
RETURNS CHAR AS 
$$
DECLARE 
    v_return CHAR := 'N';
BEGIN  
    -- Si la fecha es mayor a la fecha actual, retornar 'S'
    IF FECHA_VUELO > CURRENT_DATE THEN
        v_return := 'S';
    END IF;
    
    RETURN v_return;
EXCEPTION
    WHEN OTHERS THEN 
        RETURN 'S';  -- Si ocurre un error, devuelve 'S'
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION ESTA_AGENCIA(COD_AGENCIA INT) 
RETURNS BOOLEAN AS 
$$
DECLARE 
    RES INT;
BEGIN 
    -- Contar el número de registros con el ID_AGENCIA especificado
    SELECT COUNT(*) INTO RES FROM AGENCIA WHERE ID_AGENCIA = COD_AGENCIA;
    
    -- Si existe exactamente 1 registro, retornar TRUE, de lo contrario FALSE
    IF RES = 1 THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;

EXCEPTION
    WHEN OTHERS THEN 
        RAISE EXCEPTION 'Ha ocurrido un problema en la validación de agencia';
END;
$$ LANGUAGE plpgsql;



-- Función para verificar si un itinerario existe
CREATE OR REPLACE FUNCTION ESTA_ITINERARIO(COD_ITI INT) 
RETURNS BOOLEAN AS 
$$
DECLARE 
    RESULTA INT;
BEGIN 
    SELECT COUNT(*) INTO RESULTA FROM ITINERARIO WHERE COD_ITINERARIO = COD_ITI;
    RETURN RESULTA = 1;

EXCEPTION
    WHEN OTHERS THEN 
        RAISE EXCEPTION 'Ha ocurrido un problema en la validación de itinerario';
END;
$$ LANGUAGE plpgsql;


-- Función para verificar si un origen existe
CREATE OR REPLACE FUNCTION ESTA_ORIGEN(CODIGO_O INT) 
RETURNS BOOLEAN AS 
$$
DECLARE 
    RESU INT;
BEGIN 
    SELECT COUNT(*) INTO RESU FROM ORIGEN WHERE COD_ORIGEN = CODIGO_O;
    RETURN RESU = 1;

EXCEPTION
    WHEN OTHERS THEN 
        RAISE EXCEPTION 'Ha ocurrido un problema en la validación de origen';
END;
$$ LANGUAGE plpgsql;


-- Función para verificar si un destino existe
CREATE OR REPLACE FUNCTION ESTA_DESTINO(CODIGO_D INT) 
RETURNS BOOLEAN AS 
$$
DECLARE 
    RESU INT;
BEGIN 
    SELECT COUNT(*) INTO RESU FROM DESTINO WHERE COD_DESTINO = CODIGO_D;
    RETURN RESU = 1;

EXCEPTION
    WHEN OTHERS THEN 
        RAISE EXCEPTION 'Ha ocurrido un problema en la validación de destino';
END;
$$ LANGUAGE plpgsql;


-- Función para verificar si un asiento está disponible en un vuelo
CREATE OR REPLACE FUNCTION VERIFICA_ASIENTO(
    NUMERO INT, -- N_ASIENTO
    ID INT      -- COD_VUELO
) 
RETURNS INT AS 
$$
DECLARE 
    num INT;
BEGIN 
    SELECT COUNT(*) INTO num
    FROM PASAJE
    WHERE N_ASIENTO = NUMERO AND COD_VUELO = ID;

    IF num = 0 THEN
        RAISE NOTICE 'EL ASIENTO ESTA DISPONIBLE';
    ELSE
        RAISE NOTICE 'EL ASIENTO NO ESTA DISPONIBLE';
    END IF;

    RETURN num;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE TABLA_TEMPORAL(
	COD_PASAJE INT,
	TOTAL INT
);																					---------
-- Función para verificar si un vuelo está asociado a un itinerario
CREATE OR REPLACE FUNCTION VERIFICA_VUELO_ITINERARIO(
    id_vuelo INT, 
    id_itine INT
) 
RETURNS INT AS 
$$
DECLARE 
    num INT;
BEGIN 
    SELECT COUNT(*) INTO num
    FROM ITINERARIO 
    WHERE COD_ITINERARIO = (SELECT COD_ITINERARIO 
                            FROM VUELO
                            WHERE COD_ITINERARIO = id_itine AND id_vuelo = COD_VUELO);

    IF num = 0 THEN
        RAISE NOTICE 'NO TA';
    ELSE
        RAISE NOTICE 'SI TA';
    END IF;

    RETURN num;
END;
$$ LANGUAGE plpgsql;


-- Función para validar el rango de valores en una encuesta
CREATE OR REPLACE FUNCTION RANGO_VALOR(
    COD_PA INT, 
    ATENCION INT, 
    CALIDAD INT, 
    RAPIDEZ INT
) 
RETURNS BOOLEAN AS 
$$
DECLARE 
    RESU INT;
BEGIN 
    SELECT COUNT(*) INTO RESU FROM ENCUESTA WHERE COD_PASAJE = COD_PA;
    
    IF RESU = 0 THEN
        IF ATENCION BETWEEN 0 AND 10 AND 
           CALIDAD BETWEEN 0 AND 10 AND 
           RAPIDEZ BETWEEN 0 AND 10 THEN 
            RETURN TRUE; 
        END IF;
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;


-- Función para verificar si un cliente existe
CREATE OR REPLACE FUNCTION ESTA_CLIENTE(RUT_C INT) 
RETURNS BOOLEAN AS 
$$
DECLARE 
    RESU INT;
BEGIN 
    SELECT COUNT(*) INTO RESU FROM CLIENTE WHERE RUT_CLIENTE = RUT_C;
    RETURN RESU = 1;

EXCEPTION
    WHEN OTHERS THEN 
        RAISE EXCEPTION 'Ha ocurrido un problema en la validación de cliente';
END;
$$ LANGUAGE plpgsql;


-- Función para verificar si un pasaje existe
CREATE OR REPLACE FUNCTION ESTA_PASAJE(COD_PA INT) 
RETURNS BOOLEAN AS 
$$
DECLARE 
    RESU INT;
BEGIN 
    SELECT COUNT(*) INTO RESU FROM PASAJE WHERE COD_PASAJE = COD_PA;
    RETURN RESU = 1;

EXCEPTION
    WHEN OTHERS THEN 
        RAISE EXCEPTION 'Ha ocurrido un problema en la validación del pasaje';
END;
$$ LANGUAGE plpgsql;


-- Función para verificar si un vuelo existe
CREATE OR REPLACE FUNCTION ESTA_VUELO(COD_V INT) 
RETURNS BOOLEAN AS 
$$
DECLARE 
    RESU INT;
BEGIN 
    SELECT COUNT(*) INTO RESU FROM VUELO WHERE COD_VUELO = COD_V;
    RETURN RESU = 1;

EXCEPTION
    WHEN OTHERS THEN 
        RAISE EXCEPTION 'Ha ocurrido un problema en la validación del vuelo';
END;
$$ LANGUAGE plpgsql;



