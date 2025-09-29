"""Ejemplo de uso no interactivo del módulo.

Muestra cómo importar la función `search_hostname`.
"""
from azure_gtw_hostname_checker import azure_gtw_checker as checker  # adjust path if running as package
# En este repo el script está en la raiz, así que this example assumes it's importable.
# Llamada de ejemplo (requiere credenciales y subscription):
# credential = checker.get_credentials()
# found = checker.search_hostname('mi-subscription-id', 'ejemplo.com', credential=credential)
# print(found)

print('Este ejemplo muestra la forma de usar search_hostname desde código. Modifícalo según tu entorno.')
