CREATE OR REPLACE FUNCTION insertar_cliente(
    rut_e INT, 
    nombre_e TEXT, 
    apellido_e TEXT, 
    correo_e TEXT, 
    fecha_nac_e TEXT, -- Recibimos como string para convertirlo
    region_e TEXT, 
    comuna_e TEXT, 
    calle_e TEXT, 
    numero_e INT, 
    telefono_e BIGINT,
	rol TEXT
) RETURNS TEXT AS $$
DECLARE
    fecha_nac_nueva DATE;
BEGIN
    -- Convertir fecha
    fecha_nac_nueva := TO_DATE(fecha_nac_e, 'DD/MM/YYYY');
    
    -- Validar RUT
    IF NOT rut_validar(rut_e::VARCHAR) THEN
        RAISE EXCEPTION 'EL RUT DEL CLIENTE ES INVALIDO';
    END IF;
    
    -- Validar si ya existe
    IF EXISTS (SELECT 1 FROM cliente WHERE rut_cliente = rut_e) THEN
        RAISE EXCEPTION 'EL CLIENTE YA EXISTE';
    END IF;
    
    -- Validar si es menor de edad
    IF fecha_nac_nueva > CURRENT_DATE - INTERVAL '18 years' THEN
        RAISE EXCEPTION 'CLIENTE MENOR DE EDAD';
    END IF;

    -- Insertar cliente con tipo compuesto
    INSERT INTO cliente (rut_cliente, nombre, apellido, correo, fecha_nacimiento, direccion_cliente, telefono,rol)
    VALUES (rut_e, nombre_e, apellido_e, correo_e, fecha_nac_nueva, 
            ROW(region_e, comuna_e, calle_e, numero_e)::direccion_c, telefono_e,rol);
    
    RETURN 'CLIENTE INGRESADO CORRECTAMENTE';
EXCEPTION
    WHEN OTHERS THEN
        RETURN SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Llamada correcta a la función
SELECT insertar_cliente(201437067, 'Sergio', 'Leon', 'juan.perez@dominio.com', '15/08/1995',
                        'Santiago', 'Ñuñoa', 'Av. Principal', 123, 992527915,'admin');


CREATE OR REPLACE FUNCTION actualizar_datos_cliente()
RETURNS TRIGGER AS $$
DECLARE
    v_region VARCHAR(100);
    v_comuna VARCHAR(100);
    v_calle VARCHAR(100);
    v_numero INT;
BEGIN
    -- Convertir a mayúsculas los campos simples
    NEW.NOMBRE := UPPER(NEW.NOMBRE);
    NEW.APELLIDO := UPPER(NEW.APELLIDO);
    NEW.CORREO := UPPER(NEW.CORREO);

    -- Descomponer el tipo compuesto DIRECCION_CLIENTE
    v_region := (NEW.DIRECCION_CLIENTE).region;
    v_comuna := (NEW.DIRECCION_CLIENTE).comuna;
    v_calle := (NEW.DIRECCION_CLIENTE).calle;
    v_numero := (NEW.DIRECCION_CLIENTE).numero;

    -- Convertir a mayúsculas los campos de la dirección
    v_region := UPPER(v_region);
    v_comuna := UPPER(v_comuna);
    v_calle := UPPER(v_calle);

    -- Reconstruir el tipo compuesto DIRECCION_CLIENTE
    NEW.DIRECCION_CLIENTE := ROW(v_region, v_comuna, v_calle, v_numero)::direccion_c;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION INSERTAR_AGENCIA(
    RUT_AGENCIA_E INT,       -- O cambiar a VARCHAR si incluye guion
    NOMBRE_AGENCIA_E TEXT,
    REGION_E TEXT,
    COMUNA_E TEXT,
    CALLE_E TEXT,
    NUMERO_E INT,
    TELEFONO_E BIGINT          -- O cambiar a VARCHAR si el número es largo
    
)RETURNS TEXT AS $$
BEGIN
   
    -- Insertar nueva agencia sin especificar ID_AGENCIA porque es SERIAL
    INSERT INTO AGENCIA (RUT_AGENCIA, NOMBRE_AGENCIA, DIRECCION_A, TELEFONO)
    VALUES (RUT_AGENCIA_E, NOMBRE_AGENCIA_E, ROW(REGION_E, COMUNA_E, CALLE_E, NUMERO_E)::direccion_c, TELEFONO_E);

    -- Mensaje de éxito
    RETURN 'AGENCIA INGRESADA CORRECTAMENTE';
   

EXCEPTION
    
    WHEN others THEN
        RETURN SQLERRM;
        
END;
$$ LANGUAGE plpgsql;

