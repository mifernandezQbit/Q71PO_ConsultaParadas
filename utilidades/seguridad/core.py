#***************************************************************************************#
# Función: verificarSeguridadMCU                                                        #
# Propósito: Verificar si determinado MCU está permitido según configuración de P00950  #
# Entrada:  mcu - centro de costos a verificar                                          #
#           inclusiva - tipo de seguridad, si el rango es inclusivo o exclusivo         #
#           rangoMCU - rango de centros de costos a los que está incluído o excluído    #
# Salida: True si tiene permitido el MCU, caso contrario False                          #
# VERSION: 1.0.0                                                                        #
#***************************************************************************************#
import logging

def verificarSeguridadMCU(mcu,inclusiva=False, rangoMCU=[]):
    existe = False
    mcuJust=mcu.rjust(12, ' ')
    # iteramos sobre los rangos hasta encontrar uno
    for item in rangoMCU:
        cc_desde = item.get("ccDesde", "").replace("*BLANKS", "").rjust(12, ' ')
        cc_hasta = item.get("ccHasta", "").replace("*BLANKS", "").rjust(12, ' ')
        # Si el rango está vacío, continuamos
        if not cc_desde or not cc_hasta:
            continue

        # Comparación alfabética (string)
        if cc_desde <= mcuJust <= cc_hasta:
            existe=True
            break

    # Dependiendo si es inclusiva o exclusiva respondemos 
    return existe if inclusiva else not existe

def completarRequestSeguridad(json,accion):

    jsonCompleto = json
    # verificar si seguridad está activada
    if 'seguridadCCActivada' in jsonCompleto and jsonCompleto['seguridadCCActivada']:
        # verificar tipo de seguridad y determinar valor a buscar
        if 'seguridadInclusiva' in jsonCompleto and jsonCompleto['seguridadInclusiva']:
            jsonCompleto['valorAccionCC']='Y'
        else:
            jsonCompleto['valorAccionCC']='N'
        
        # asignar acción JDE
        jsonCompleto['accionJDE']=accion

    return jsonCompleto
