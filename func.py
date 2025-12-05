import io
import json
import logging
import requests

from fdk import response

def handler(ctx, data: io.BytesIO = None):
    try:
        cfg = ctx.Config()
        url = cfg["urlLogin"]
        params = json.loads(data.getvalue())

    except (Exception, ValueError) as ex:
        logging.getLogger().info('error parsing json payload: ' + str(ex))

    logging.getLogger().info('Params: ' + str(params))

    respuesta   = sendQuery(params, url, 'Q71PO_ORCH_ConsultaParadas')
    logging.getLogger().info(respuesta)
    respJson    = respuesta.json()
    if (respuesta.status_code == 444):
        respJson = {
            "success"         : False,
            "rowset"          : None,
            "tokenExpirado"   : True,
            "data"            : None,
            "errorJde"        : True,
            "errorsList"      : []
        }
    else:
        respJson    = procesarRespuesta(respJson)
    return response.Response(
        ctx, response_data=json.dumps(respJson),
        headers={"Content-Type": "application/json"}
    )

def sendQuery(params, urlOrc, orchestation):
    url = urlOrc + '/v3/orchestrator/' + orchestation
    try:
        resp    = requests.post(url, json= params)
    except Exception as e:
        resp = "Falló: " + str(e)
    
    return resp

def procesarRespuesta(respuesta):
    try:
        resultado = {}
        errorsList=[]
        logging.getLogger().info(respuesta)
        logging.getLogger().info(type(respuesta))
        if ("jde__status" in respuesta):
            if ((respuesta['jde__status']).strip() == "SUCCESS" or (respuesta['jde__status'].strip() == "WARN" )):
                if "rowset" in respuesta:
                    rowset = respuesta["rowset"]
                    resultado = {
                        "success"         : True,
                        "rowset"          : rowset,
                        "tokenExpirado"   : False,
                        "data"            : None,
                        "errorJde"        : False,
                        "errorsList"      : errorsList
                    }
            else:
                resultado =  {
                    "success"         : False,
                    "rowset"          : None,
                    "tokenExpirado"   : False,
                    "data"            : None,
                    "errorJde"        : True,
                    "errorsList"      : procesarErrores(respuesta)
                }
        else:
            resultado =  {
                "success"         : False,
                "rowset"          : None,
                "tokenExpirado"   : False,
                "data"            : None,
                "errorJde"        : True,
                "errorsList"      : procesarErrores(respuesta)
            }
    except Exception as e:
        logging.getLogger().info('** error procesarRespuesta: ' + str(e))
    
    return resultado

def extraerErrores(respuesta):
    errorsList = []
    
    # Verificar que el JSON es un diccionario y contiene la clave 'message'
    if isinstance(respuesta, dict) and 'message' in respuesta:
        infoMessage = respuesta["message"]
        
        # Verificar que 'infoMessage' es un diccionario
        if isinstance(infoMessage, dict):
            # Recorrer todas las claves de infoMessage
            for key, value in infoMessage.items():
                # Verificar si la clave actual tiene como valor un diccionario y contiene a su vez "JAS Response"
                if isinstance(value, dict) and "JAS Response" in value:
                    jasResponse = value['JAS Response']
                    
                    # Recorrer todas las claves dentro de 'JAS Response'
                    for keyInJasResponse, valueInJasResponse in jasResponse.items():
                        # Verificar si contiene la clave 'errors' y es un diccionario
                        if isinstance(valueInJasResponse, dict) and "errors" in valueInJasResponse:
                            errors = valueInJasResponse["errors"]
                            
                            # Verificar si "errors" es una lista y tiene elementos
                            if isinstance(errors, list) and errors:
                                # Recorrer cada error dentro de la lista
                                for error in errors:
                                    if isinstance(error, dict):
                                        # Crear un diccionario con las claves 'code', 'title' y 'desc'
                                        errorInfo = {
                                            "code": error.get("CODE", '000'),
                                            "title": error.get("TITLE", 'ERROR INESPERADO'),
                                            "desc": error.get("DESC", 'Descripción no disponible')
                                        }
                                        # Agregar el error a la lista de errores
                                        errorsList.append(errorInfo)
                                        logging.getLogger().info('**** Error List ****')
                                        logging.getLogger().info(errorsList)
                elif isinstance(value, dict) and "message" in value:
                    errorsList.extend(extraerErrores(value))
        else:
            infoError = {
                "code": '0000',
                "title": 'Error',
                "desc": infoMessage
            }
            # Agregar el diccionario a la lista de errores
            errorsList.append(infoError)
    return errorsList

## Función para revisar los errores que retornó la orquestación y normalizarlos en una lista única
def procesarErrores(respuesta):
    errorsList  = extraerErrores(respuesta)
    logging.getLogger().info(errorsList)
    return errorsList