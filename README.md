# endpointsearch
#  AGREGAR EJEMPLO VISUAL, MEJORAR Y COMPLETAR ESTRUCTURA Y FORMATO

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![CI](https://github.com/JavierRamirezMoral/endpointsearch/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)

Script en **Python** para buscar un *hostname* en todos los **Application Gateways** de un tenant de Azure.  
Útil para administradores y equipos de seguridad que gestionan múltiples gateways y necesitan localizar rápidamente dónde se usa un dominio.

---

## 🚀 Requisitos previos
- Python **3.9+**  
- Acceso al tenant de Azure y permisos para listar Application Gateways  
- Haber iniciado sesión con `az login` o tener configurado un método de autenticación compatible con `DefaultAzureCredential`  
- Subscription ID de Azure  

---

## ⚙️ Instalación
```bash
git clone https://github.com/JavierRamirezMoral/endpointsearch.git
cd endpointsearch
python -m venv .venv
source .venv/bin/activate   # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
🖥️ Uso
Ejecución directa
bash
Copiar código
python azure_gtw_checker.py
El script pedirá el hostname y el subscription id. También puedes pasar el hostname como argumento:

bash
Copiar código
python azure_gtw_checker.py ejemplo.com
Ejemplo interactivo
(Extraído de examples/example_output.txt)

yaml
Copiar código
Ingrese el hostname a buscar: ejemplo.com
Ingrese el Subscription ID (o pulse Enter para usar AZURE_SUBSCRIPTION_ID env): xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

Resultados:
✔ Encontrado en Application Gateway: app-gtw-prod (Resource Group: rg-prod)
✔ Encontrado en Application Gateway: app-gtw-dr (Resource Group: rg-dr)
Uso desde código
En examples/usage_example.py tienes un ejemplo de cómo importar la función principal:

python
Copiar código
from azure_gtw_checker import search_hostname, get_credentials

cred = get_credentials()
resultados = search_hostname("xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", "ejemplo.com", cred)
print(resultados)
✅ Tests
Este proyecto incluye tests con pytest. Para ejecutarlos:

bash
Copiar código
pytest
🔄 CI/CD
Este repo incluye un workflow de GitHub Actions que:

Instala Python 3.10

Instala dependencias desde requirements.txt

Ejecuta pytest para validar el código

Cada push o pull request lanzará automáticamente los tests.

🤝 Contribuir
Si quieres contribuir:

Abre un issue para sugerir mejoras o reportar bugs

Envía un pull request con tu cambio

(En el futuro se puede añadir un archivo CONTRIBUTING.md).

📜 Changelog
Consulta CHANGELOG.md (opcional) para ver el historial de cambios en futuras versiones.
