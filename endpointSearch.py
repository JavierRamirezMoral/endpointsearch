"""
Autor: Javier Ramírez Moral
Fecha: 16/05/2025

Objetivo:
-----------
Este script surge para facilitarnos el trabajo  cuando recibimos incidencias en Azure.
Su propósito es agilizar y simplificar la búsqueda de endpoints específicos (por ejemplo, un path como '/miapi' o un hostname como 'api.midominio.com') en todos los Application Gateways de todas las suscripciones del tenant. 
Así, podemos identificar rápidamente dónde está configurado un endpoint y actuar con mayor eficiencia ante cualquier requerimiento o incidencia.

Características principales:
- Utiliza las credenciales del Azure CLI para autenticarse.
- Recorre todas las suscripciones disponibles en el tenant.
- Busca coincidencias del endpoint proporcionado en:
    - Las reglas de rutas (Path Maps) de cada Application Gateway.
    - Los listeners HTTP de cada Application Gateway.
    - Las reglas de enrutamiento (`request_routing_rules`), incluyendo posibles redirecciones.
- Muestra información detallada sobre dónde se encontró el endpoint, incluyendo el nombre del Application Gateway, la suscripción, el grupo de recursos, el Path Map, la regla, la redirección o el listener correspondiente.
- Incluye un enlace directo al recurso en el portal de Azure para acceder rápidamente.
- Si no se encuentra el endpoint, informa al usuario.

Requisitos:
- Python 3.8 o superior instalado.
  Puedes descargarlo desde: https://www.python.org/downloads/
- Instalar los paquetes necesarios ejecutando en la terminal:
    pip install azure-identity azure-mgmt-network azure-mgmt-resource
- Azure CLI instalado y autenticado (`az login`).

Uso:
    python endpointSearch.py

El script solicitará el endpoint a buscar por consola.

Versiones:
    1.0.0 - 16/05/2025 - Creación del script.
    1.1.0 - 16/05/2025 - Añadido enlace directo al recurso en Azure Portal.
    1.2.0 - 16/05/2025 - Añadida búsqueda en las reglas de enrutamiento (request_routing_rules).
"""

from azure.identity import AzureCliCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import SubscriptionClient

def get_app_gateways_with_endpoint_all_subs(endpoint_to_find):
    credential = AzureCliCredential()
    subscription_client = SubscriptionClient(credential)

    print(f"\n🔍 Buscando endpoint '{endpoint_to_find}' en todos los Application Gateways del tenant...\n")

    found = False

    for sub in subscription_client.subscriptions.list():
        subscription_id = sub.subscription_id
        print(f"📦 Revisando suscripción: {sub.display_name} ({subscription_id})")
        network_client = NetworkManagementClient(credential, subscription_id)

        try:
            app_gateways = list(network_client.application_gateways.list_all())
        except Exception as e:
            print(f"⚠️  No se pudo acceder a los App GW de la suscripción {subscription_id}: {e}")
            continue

        for appgw in app_gateways:
            rg_name = appgw.id.split("/")[4]
            portal_link = f"https://portal.azure.com/#@/resource/subscriptions/{subscription_id}/resourceGroups/{rg_name}/providers/Microsoft.Network/applicationGateways/{appgw.name}"

            # Buscar en Path Maps
            for path_map in appgw.url_path_maps or []:
                for path_rule in path_map.path_rules or []:
                    for path in path_rule.paths or []:
                        if endpoint_to_find in path:
                            print(f"✅ Encontrado en App GW: {appgw.name}")
                            print(f"   - Subscripción: {sub.display_name}")
                            print(f"   - Resource Group: {rg_name}")
                            print(f"   - Path Map: {path_map.name}")
                            print(f"   - Rule: {path_rule.name}")
                            print(f"   - Path: {path}")
                            print(f"   - 🔗 Portal Azure: {portal_link}\n")
                            found = True

            # Buscar en Listeners
            for listener in appgw.http_listeners or []:
                if (listener.host_name and endpoint_to_find in listener.host_name) or \
                   (listener.name and endpoint_to_find in listener.name):
                    print(f"✅ Posible coincidencia en Listener del App GW: {appgw.name}")
                    print(f"   - Subscripción: {sub.display_name}")
                    print(f"   - Resource Group: {rg_name}")
                    print(f"   - Listener Name: {listener.name}")
                    print(f"   - Hostname: {listener.host_name}")
                    print(f"   - 🔗 Portal Azure: {portal_link}\n")
                    found = True

            # Buscar en Request Routing Rules
            for rule in appgw.request_routing_rules or []:
                if rule.rule_type == "Basic":
                    if rule.name and endpoint_to_find in rule.name:
                        print(f"✅ Coincidencia en regla básica del App GW: {appgw.name}")
                        print(f"   - Rule: {rule.name}")
                        print(f"   - Subscripción: {sub.display_name}")
                        print(f"   - Resource Group: {rg_name}")
                        print(f"   - 🔗 Portal Azure: {portal_link}\n")
                        found = True

                if rule.redirect_configuration and endpoint_to_find in rule.redirect_configuration.id:
                    print(f"✅ Posible coincidencia en redirección del App GW: {appgw.name}")
                    print(f"   - Rule: {rule.name}")
                    print(f"   - Redirección (ID): {rule.redirect_configuration.id}")
                    print(f"   - Subscripción: {sub.display_name}")
                    print(f"   - Resource Group: {rg_name}")
                    print(f"   - 🔗 Portal Azure: {portal_link}\n")
                    found = True

                if rule.url_path_map and endpoint_to_find in rule.url_path_map.id:
                    print(f"✅ Posible coincidencia en URL Path Map ID del App GW: {appgw.name}")
                    print(f"   - Rule: {rule.name}")
                    print(f"   - URL Path Map ID: {rule.url_path_map.id}")
                    print(f"   - Subscripción: {sub.display_name}")
                    print(f"   - Resource Group: {rg_name}")
                    print(f"   - 🔗 Portal Azure: {portal_link}\n")
                    found = True


    if not found:
        print("\n❌ Endpoint no encontrado en ningún Application Gateway del tenant.")

if __name__ == "__main__":
    endpoint = input("🔎 Introduce el endpoint a buscar (por ejemplo, /miapi o api.midominio.com): ").strip()
    get_app_gateways_with_endpoint_all_subs(endpoint)
