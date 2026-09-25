# 🔥 MeitiCrawler - Rastreador de Plataformas de Redes Sociales 🕷️

<div align="center">

[![GitHub Stars](https://img.shields.io/github/stars/Aswellle/MeitiCrawler?style=social)](https://github.com/Aswellle/MeitiCrawler/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Aswellle/MeitiCrawler?style=social)](https://github.com/Aswellle/MeitiCrawler/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/Aswellle/MeitiCrawler)](https://github.com/Aswellle/MeitiCrawler/issues)
[![License](https://img.shields.io/badge/license-Non--Commercial%20Learning%201.1-blue)](LICENSE)
[![中文](https://img.shields.io/badge/🇨🇳_中文-Available-blue)](README.md)
[![English](https://img.shields.io/badge/🇺🇸_English-Available-green)](README_en.md)
[![Español](https://img.shields.io/badge/🇪🇸_Español-Current-green)](README_es.md)

</div>

---

> ### 🔗 Origen del Proyecto y Declaración de Fork
>
> **Este repositorio es un fork de [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler).**
>
> El proyecto original fue creado y mantenido por **[NanmiCoder (Programador Jiang-Relakkes)](https://github.com/NanmiCoder)**, un proyecto de código abierto de recolección de datos de redes sociales multiplataforma con altas estrellas.
>
> Este fork, mantenido por **Aswellle**, ofrece mejoras de UI/UX y características adicionales sobre el proyecto original, con el objetivo de proporcionar una interfaz web modernizada y una mejor experiencia de usuario mientras preserva la excelente arquitectura del proyecto original.
>
> **Los derechos de autor, licencia y descargo de responsabilidad del proyecto original pertenecen a NanmiCoder/relakkes, mientras que las modificaciones agregadas por este fork son responsabilidad de Aswellle.** Consulte la sección [Descargo de responsabilidad](#descargo-de-responsabilidad) a continuación para obtener más detalles.

---

> **⚠️ Descargo de Resumen (Resumen)**
>
> Todo el contenido de este repositorio es únicamente para fines de aprendizaje e investigación. El uso comercial está prohibido. Ninguna persona u organización puede usar el contenido de este repositorio con fines ilegales o para infringir los derechos legítimos de otros. Por cualquier responsabilidad legal que surja del uso del contenido de este repositorio, la parte responsable correspondiente asumirá la responsabilidad de acuerdo con sus contribuciones.
>
> Este repositorio está licenciado bajo [NON-COMMERCIAL LEARNING LICENSE 1.1](LICENSE), con los derechos de autor originales pertenecientes a relakkes@gmail.com.
>
> 👉 [Haga clic para saltar al descargo de responsabilidad completo](#descargo-de-responsabilidad)

---

## 📝 Contribuciones de la Rama

Este fork introduce los siguientes cambios principales sobre el proyecto original:

- **Rediseño Completo de WebUI** — Revisión de UI/UX del frontend `webui/`, proporcionando una interfaz de operación más intuitiva y moderna
- **Optimización de la Experiencia de Interacción** — Mejora de los flujos de trabajo principales, incluyendo configuración del rastreador, monitoreo de estado y visualización de registros
- **Mejoras de Características y Correcciones de Errores** — Múltiples mejoras mientras se preserva la arquitectura original

> Todos los registros de commits y cambios de esta rama pueden verse a través de [GitHub Compare View](https://github.com/NanmiCoder/MediaCrawler/compare...Aswellle:MeitiCrawler:main).

---

## 📖 Introducción del Proyecto

Una poderosa **herramienta de recolección de datos de redes sociales multiplataforma** que soporta el rastreo de información pública de plataformas principales incluyendo Xiaohongshu, Douyin, Kuaishou, Bilibili, Weibo, Tieba, Zhihu, y más.

### 🔧 Principios Técnicos

- **Tecnología Central**: Basado en el framework de automatización de navegador [Playwright](https://playwright.dev/) para login y mantenimiento del estado de login
- **No Requiere Ingeniería Inversa de JS**: Utiliza el entorno de contexto del navegador con estado de login preservado para obtener parámetros de firma a través de expresiones JS
- **Ventajas**: No necesita hacer ingeniería inversa de algoritmos de encriptación complejos, reduciendo significativamente la barrera técnica

## ✨ Características

| Plataforma | Búsqueda por Palabras Clave | Rastreo de ID de Publicación Específica | Comentarios Secundarios | Página de Inicio de Creador Específico | Caché de Estado de Login | Pool de Proxy IP | Generar Nube de Palabras de Comentarios |
| ------ | ---------- | -------------- | -------- | -------------- | ---------- | -------- | -------------- |
| Xiaohongshu | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              |
| Douyin   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              |
| Kuaishou   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              |
| Bilibili   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              |
| Weibo   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              |
| Tieba   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              |
| Zhihu   | ✅          | ✅              | ✅        | ✅              | ✅          | ✅        | ✅              |


## 🚀 Inicio Rápido

## 📋 Prerrequisitos

### 🚀 Instalación de uv (Recomendado)

Antes de proceder con los siguientes pasos, por favor asegúrese de que uv esté instalado en su computadora:

- **Guía de Instalación**: [Guía Oficial de Instalación de uv](https://docs.astral.sh/uv/getting-started/installation)
- **Verificar Instalación**: Ingrese el comando `uv --version` en la terminal. Si el número de versión se muestra normalmente, la instalación fue exitosa
- **Razón de Recomendación**: uv es actualmente la herramienta de gestión de paquetes Python más poderosa, con velocidad rápida y resolución de dependencias precisa

### 🟢 Instalación de Node.js

El proyecto depende de Node.js, por favor descargue e instale desde el sitio web oficial:

- **Enlace de Descarga**: https://nodejs.org/en/download/
- **Requisito de Versión**: >= 16.0.0

### 📦 Instalación de Paquetes Python

```shell
# Entrar al directorio del proyecto
cd MeitiCrawler

# Usar el comando uv sync para asegurar la consistencia de la versión de python y paquetes de dependencias relacionados
uv sync
```

### 🌐 Instalación de Controlador de Navegador (Opcional)

> Si usa el modo CDP predeterminado (conectándose a un navegador Chrome existente), **no se requiere la instalación del controlador del navegador**. La instalación solo es necesaria cuando se usa el modo Playwright estándar.

```shell
# Instalar controlador de navegador solo cuando esté en modo Playwright estándar
uv run playwright install
```

### 🌍 Configuración del Navegador Chrome (Recomendado)

El proyecto usa el modo CDP por defecto para conectarse al navegador Chrome existente del usuario, que puede reutilizar el estado de login existente, cookies, extensiones, etc. del navegador, **reduciendo significativamente el riesgo de detección anti-bot de la plataforma**.

Antes de usar:

1. **Instale la última versión del navegador Chrome** (versión >= 144), [Descargar](https://www.google.com/chrome/)
2. **Habilite la depuración remota**: Escriba `chrome://inspect/#remote-debugging` en la barra de direcciones de Chrome y marque **"Permitir depuración remota para esta instancia del navegador"**
3. La página muestra `Server running at: 127.0.0.1:9222`, lo que indica que está listo

> 💡 **Consejo**: Después de ejecutar el rastreador, aparecerá un diálogo de confirmación en Chrome. Haga clic en "Aceptar" para continuar. El programa esperará la confirmación del usuario; complete la operación en 60 segundos.
>
> Si no desea usar el modo CDP, puede establecer `ENABLE_CDP_MODE = False` en `config/base_config.py` para cambiar al modo Playwright estándar.

## 🚀 Ejecutar Programa Rastreador

```shell
# Ver elementos de configuración en config/base_config.py, con comentarios disponibles

# Leer palabras clave del archivo de configuración para buscar publicaciones relacionadas y rastrear información de publicaciones y comentarios
uv run main.py --platform xhs --lt qrcode --type search

# Leer lista de ID de publicaciones específicas del archivo de configuración para obtener información e información de comentarios de publicaciones específicas
uv run main.py --platform xhs --lt qrcode --type detail

# Abrir la APP correspondiente para escanear código QR para login

# Para ejemplos de uso de rastreador de otras plataformas, ejecute el siguiente comando para ver
uv run main.py --help
```

> ⚠️ **Recordatorio del Servicio Backend**: La siguiente interfaz visual WebUI depende del servicio API backend para funcionar. Antes del uso inicial, por favor **inicie el backend por separado primero**:
>
> ```shell
> uv run uvicorn api.main:app --port 8080 --reload
> ```
>
> Después de que el backend se inicie exitosamente, abra la interfaz WebUI (`http://localhost:5173/` o `http://localhost:8080`). Si el backend no se ha iniciado, la página llamará a `/api/env/check` para una verificación de entorno en la primera visita y fallará. En este punto, puede hacer clic en "Omitir verificación" para omitirla temporalmente, pero la funcionalidad del rastreador no estará disponible.

## 🖥️ Interfaz de Operación Visual WebUI

MeitiCrawler proporciona una interfaz de operación visual basada en web, permitiéndole usar fácilmente las funciones del rastreador sin la línea de comandos.

#### Desarrollo (Recomendado)

Para el desarrollo, debe iniciar tanto el servicio API backend como el servidor de desarrollo Vite frontend:

```shell
# Terminal 1: iniciar servidor API (puerto predeterminado 8080)
uv run uvicorn api.main:app --port 8080 --reload

# Terminal 2: iniciar servidor de desarrollo frontend
cd webui
npm install
npm run dev        # se inicia en el puerto 5173 por defecto y redirige /api a 8080
```

Después de iniciar exitosamente, visite `http://localhost:5173/` para abrir la interfaz WebUI.

> En el primer inicio, se realiza una verificación de entorno (llama a `/api/env/check`), así que asegúrese de que el servicio backend esté en ejecución. Si la verificación falla, puede hacer clic en "Omitir verificación" para omitirla temporalmente.

#### Construir para Producción

Si desea que el servidor API sirva directamente los recursos estáticos de WebUI, construya el frontend primero:

```shell
cd webui
npm install
npm run build      # salida en api/webui/
```

Luego inicie solo el servidor API:

```shell
uv run uvicorn api.main:app --port 8080 --reload
```

Después de eso, visite `http://localhost:8080`.

#### Características de WebUI

- Configuración visual de parámetros del rastreador (plataforma, método de login, tipo de rastreo, etc.)
- Vista en tiempo real del estado de ejecución del rastreador y logs
- Vista previa y exportación de datos

#### Vista Previa de la Interfaz

| Panel de Resumen | Configuración del Rastreador |
| --- | --- |
| ![Panel de Resumen](docs/static/images/webui_overview.png) | ![Configuración del Rastreador](docs/static/images/webui_config.png) |

| Registros de Ejecución | <!-- Reservado --> |
| --- | --- |
| ![Registros de Ejecución](docs/static/images/webui_logs.png) | — |


## 🔗 Usando Gestión de Entorno venv Nativo de Python (No Recomendado)

#### Crear y activar entorno virtual de Python

> Si rastrea Douyin y Zhihu, necesita instalar el entorno nodejs con anticipación, versión mayor o igual a: `16`

```shell
# Entrar al directorio raíz del proyecto
cd MeitiCrawler

# Crear entorno virtual
# Las librerías en requirements.txt están basadas en python 3.11
# Si usa otras versiones de python, las librerías en requirements.txt pueden no ser compatibles, por favor resuelva por su cuenta
python -m venv venv

# macOS & Linux activar entorno virtual
source venv/bin/activate

# Windows activar entorno virtual
venv\Scripts\activate
```

#### Instalar librerías de dependencias

```shell
pip install -r requirements.txt
```

#### Instalar controlador de navegador playwright

```shell
playwright install
```

#### Ejecutar programa rastreador (entorno nativo)

```shell
# El proyecto no habilita el modo de rastreo de comentarios por defecto. Si necesita comentarios, por favor modifique la variable ENABLE_GET_COMMENTS en config/base_config.py
# Otras opciones soportadas también pueden verse en config/base_config.py con comentarios

# Leer palabras clave del archivo de configuración para buscar publicaciones relacionadas y rastrear información de publicaciones y comentarios
python main.py --platform xhs --lt qrcode --type search

# Leer lista de ID de publicaciones específicas del archivo de configuración para obtener información e información de comentarios de publicaciones específicas
python main.py --platform xhs --lt qrcode --type detail

# Abrir la APP correspondiente para escanear código QR para login

# Para ejemplos de uso de rastreador de otras plataformas, ejecute el siguiente comando para ver
python main.py --help
```



## 💾 Almacenamiento de Datos

MeitiCrawler soporta múltiples métodos de almacenamiento de datos, incluyendo CSV, JSON, JSONL, Excel, SQLite y bases de datos MySQL.

📖 **Para instrucciones de uso detalladas, por favor vea: [Guía de Almacenamiento de Datos](docs/data_storage_guide.md)**


## 📚 Referencias

- **Repositorio del Proyecto Original**: [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler)
- **Repositorio de Firmas Xiaohongshu**: [Repositorio de firmas xhs de Cloxl](https://github.com/Cloxl/xhshow)
- **Cliente Xiaohongshu**: [Repositorio xhs de ReaJason](https://github.com/ReaJason/xhs)
- **Reenvío de SMS**: [Repositorio de referencia SmsForwarder](https://github.com/pppscn/SmsForwarder)
- **Herramienta de Penetración Interna**: [Documentación oficial de ngrok](https://ngrok.com/docs/)


---

# Descargo de Responsabilidad

Este repositorio contiene dos descargos de responsabilidad:
1. **Descargo de Responsabilidad del Proyecto Original** — Proporcionado por NanmiCoder/relakkes, aplicable al código del proyecto original
2. **Descargo de Responsabilidad de la Rama Fork** — Proporcionado por Aswellle, aplicable a las modificaciones en este fork

---

## I. Descargo de Responsabilidad del Proyecto Original

> El siguiente texto de descargo de responsabilidad se preserva del proyecto original [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler).
> Los derechos de autor originales pertenecen a relakkes@gmail.com, licenciado bajo [NON-COMMERCIAL LEARNING LICENSE 1.1](LICENSE).

<div id="disclaimer">

### 1. Propósito y Naturaleza del Proyecto
Este proyecto (en adelante denominado "este proyecto") fue creado como una herramienta de investigación técnica y aprendizaje, con el objetivo de explorar y aprender tecnología de recolección de datos web. Este proyecto se centra en la investigación de tecnología de rastreo de datos para plataformas de redes sociales, destinada al intercambio y uso por parte de estudiantes e investigadores.

### 2. Declaración de Cumplimiento Legal
El desarrollador de este proyecto (en adelante denominado "el desarrollador") recuerda solemnemente a los usuarios que cumplan estrictamente con las leyes y regulaciones relevantes de la República Popular China al descargar, instalar y usar este proyecto, incluyendo pero no limitándose a la "Ley de Ciberseguridad de la República Popular China", la "Ley de Contraespionaje de la República Popular China" y todas las leyes y políticas nacionales aplicables. Los usuarios asumirán todas las responsabilidades legales que puedan surgir del uso de este proyecto.

### 3. Declaración de Propiedad Intelectual
El desarrollador respeta y protege los derechos de propiedad intelectual de todas las partes. El código fuente y el contenido relacionado proporcionados por este proyecto son únicamente para fines de intercambio técnico y aprendizaje. Los usuarios no deben usar este proyecto para ninguna forma de actividades comerciales o infringir los derechos legales de otros.

### 4. Descargo de Responsabilidad
El desarrollador no asume ninguna responsabilidad legal por cualquier forma de daños directos, indirectos, incidentales, especiales o consecuentes que surjan del uso de este proyecto. Los usuarios asumen todos los riesgos de usar este proyecto.

### 5. Responsabilidad del Usuario
Los usuarios serán responsables de sus propias acciones al usar este proyecto y asegurarán que su uso de este proyecto cumpla con las leyes y regulaciones locales. Los usuarios no deben usar este proyecto para ninguna actividad ilegal.

### 6. Derechos de Interpretación Final
El derecho a interpretar este descargo de responsabilidad pertenece al desarrollador del proyecto original. El descargo de responsabilidad se aplica a la versión obtenida por los usuarios de este repositorio.

</div>

---

## II. Descargo de Responsabilidad de la Rama Fork

> El siguiente descargo de responsabilidad es proporcionado por Aswellle para las modificaciones realizadas en esta rama fork (incluyendo pero no limitándose a WebUI, experiencia interactiva, etc.).

### 1. Alcance de las Modificaciones
Esta rama fork es modificada por Aswellle basándose en el código del proyecto original. El alcance de las modificaciones incluye el frontend WebUI, la lógica del backend API, la optimización de la estructura del proyecto, y más.

### 2. Descargo de Responsabilidad por Modificaciones
Los problemas que surjan de las modificaciones en esta rama fork (incluyendo pero no limitándose a defectos de código, anomalías funcionales, pérdida de datos, etc.) son responsabilidad de Aswellle. Los usuarios deben evaluar los riesgos por sí mismos al usar esta rama fork.

### 3. Aviso de Derechos de Autor
Los derechos de autor del proyecto original pertenecen a NanmiCoder/relakkes. Los derechos de autor de las modificaciones realizadas en esta rama fork pertenecen a Aswellle. Al distribuir o usar esta rama fork, los usuarios deberán conservar los avisos de derechos de autor del proyecto original y las modificaciones al mismo tiempo.

### 4. Retroalimentación de Problemas
Si encuentra problemas que se originan en **modificaciones en este fork** (WebUI, experiencia interactiva, etc.), por favor proporcione retroalimentación a través de los [Issues](https://github.com/Aswellle/MeitiCrawler/issues) de este repositorio.
