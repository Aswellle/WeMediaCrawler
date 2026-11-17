# 🔥 WeMediaCrawler - Rastreador de Plataformas de Redes Sociales 🕷️

<div align="center">

[![GitHub Stars](https://img.shields.io/github/stars/Aswellle/WeMediaCrawler?style=social)](https://github.com/Aswellle/WeMediaCrawler/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Aswellle/WeMediaCrawler?style=social)](https://github.com/Aswellle/WeMediaCrawler/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/Aswellle/WeMediaCrawler)](https://github.com/Aswellle/WeMediaCrawler/issues)
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
- **Sincronización Continua con el Upstream** — Sigue las iteraciones de características del proyecto original y las correcciones de adaptación al control de riesgo de las plataformas, manteniendo el flujo de recolección alineado con el upstream
- **Legibilidad de Medios y Datos** — Cada carpeta de medios incluye un resumen CSV de una línea del contenido, para identificar la publicación propietaria al navegar por los archivos
- **Controlabilidad de la Recolección** — Los comentarios de primer nivel y sus respuestas comparten una cuota por publicación; la concurrencia, los límites de velocidad y todos los interruptores de recolección surten efecto en toda la cadena
- **Compatibilidad de Exportación** — Se corrigieron fallos de escritura bajo la tipificación estricta de PostgreSQL en algunas plataformas; todos los formatos de exportación son legibles de forma consistente
- **Aseguramiento de Calidad** — Nuevas matrices de regresión para adquisición de medios, formato de exportación × plataforma y límites/interruptores, con verificación sobre controladores de bases de datos reales y multiplexación real de audio/vídeo
- **Amigable para Agentes de IA** — El Inicio Rápido ofrece un prompt de extremo a extremo que puede entregarse a un asistente de programación con IA, desde el clonado hasta la salida sin modificar código

> Todos los registros de commits y cambios de esta rama pueden verse a través del [historial de commits de GitHub](https://github.com/Aswellle/WeMediaCrawler/commits/main).

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
cd WeMediaCrawler

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

### 🤖 Uso en Un Solo Paso vía Agente de IA (Recomendado)

Si está utilizando un asistente de programación con IA (Claude Code, Codex, Cursor, etc.), **no necesita leer este documento línea por línea**: pegue el siguiente prompt completo en el asistente (solo complete «directorio local» y «objetivo de recolección»), y el agente hará desde cero todo el flujo de «**clonar el repositorio → instalar dependencias → preparar el estado de login del navegador → (opcional) iniciar servicios locales → ejecutar la recolección → verificar la salida → reportar**».

```text
Eres el ingeniero de recolección de datos de este repositorio. Despliega y recolecta desde cero, con concurrencia única y a pequeña escala, recolectando solo datos públicos.

[Fase 0: clonar el repositorio en línea en un directorio local]
1. Clona el repositorio en mi directorio local indicado (crea los directorios padre si no existen):
   git clone https://github.com/Aswellle/WeMediaCrawler.git "<mi directorio local>"
   cd "<mi directorio local>"
2. Instala las dependencias de Python (el proyecto usa uv; si uv no está instalado, instálalo primero según
   https://docs.astral.sh/uv/getting-started/installation):
   uv sync
3. Solo si quiero el modo Playwright no-CDP, ejecuta además uv run playwright install; el modo CDP predeterminado lo omite.

[Fase 1: preparar el navegador y el estado de login]
4. El modo CDP predeterminado requiere Chrome >= 144: abre chrome://inspect/#remote-debugging en Chrome,
   marca "Allow remote debugging for this browser instance"; la página muestra 127.0.0.1:9222 cuando está listo.
   Cuando la primera ejecución requiera login por código QR, pídeme escanear el código / aceptar el diálogo del navegador manualmente; no me interrumpas en otros pasos.

[Fase 2: ejecutar la recolección (sin editar código; todo por parámetros CLI)]
5. Primero lee config/base_config.py (todos los interruptores tienen comentarios en chino) y la salida de `uv run main.py --help`, luego ejecuta:
   Mi objetivo de recolección: plataforma=xhs/dy/ks/bili/wb/tieba/zhihu, palabra clave o ID de contenido="<completar aquí>",
   datos necesarios: contenido de la publicación / comentarios / archivos multimedia (especificar según necesidad).
   Ejemplo (reemplaza los parámetros por mi objetivo):
   uv run main.py --platform xhs --lt qrcode --type search --keywords "comida" \
     --crawler_max_notes_count 20 --get_comment true --get_sub_comment true \
     --get_media true --max_comments_count_singlenotes 20 --max_concurrency_num 1 \
     --save_data_option csv --save_data_path ./data
   Para publicaciones específicas: --type detail --specified_id "<enlace o ID de la publicación>"
   Para creadores: --type creator --creator_id "<enlace o ID del perfil>"

[Fase 3: iniciar servicios locales cuando se necesite una interfaz visual (solo si quiero la WebUI)]
6. Terminal 1, inicia la API backend (el servidor de desarrollo frontend redirige /api a 8083, así que usa 8083 aquí):
   uv run uvicorn api.main:app --port 8083 --reload
   Terminal 2, inicia el frontend:
   cd webui && npm install && npm run dev
   Luego abre http://localhost:5173 ; la verificación de salud del backend es http://localhost:8083/api/env/check .
   Si solo se necesita recolección de datos, omite esta fase.
7. Para que el servidor API aloje el frontend compilado: ejecuta cd webui && npm run build (la salida va por defecto a gh-pages-dist/),
   luego copia la salida en api/webui/, e inicia solo uv run uvicorn api.main:app --port 8080 --reload ;
   abre http://localhost:8080 .

[Fase 4: reportar y verificar]
8. Reporta: lista de archivos bajo data/ con recuentos de filas/archivos, y verifica por muestreo la sanitización
   (creator_hash es un hash de 16 caracteres, los apodos están enmascarados).
9. Si aparece un captcha, una restricción de acceso o un aviso de control de riesgo de la plataforma, detente de inmediato y avísame; no reintentes para evadirlo.
```

**Por qué esto ahorra esfuerzo**:

- **Un solo prompt desde cero hasta funcionando**: clonado, instalación de dependencias, estado de login del navegador, inicio de servicios, composición de parámetros y verificación de salida están encadenados por el agente — usted solo proporciona el «directorio local» y el «objetivo de recolección»;
- Todas las capacidades son parámetros CLI (`--platform / --type / --keywords / --specified_id / --creator_id / --get_media / --get_comment / --get_sub_comment / --max_comments_count_singlenotes / --max_concurrency_num / --save_data_option / --save_data_path`); el agente puede componer cualquier forma de recolección sin tocar código;
- El formato de exportación se cambia con `--save_data_option` (csv/excel/json/jsonl/sqlite/db/postgres/mongodb), y cada carpeta de medios incluye un resumen `summary.csv` para facilitar la navegación;
- Tras el primer login por QR, el estado de login se conserva en el navegador, por lo que las ejecuciones posteriores del agente no le interrumpirán;
- La recolección puramente de datos no necesita ningún servicio local; inicie la API + WebUI solo cuando necesite una interfaz (Fase 3).

> ⚠️ **Recordatorio de Cumplimiento**: Recolecte datos públicos a pequeña escala y respete los términos de las plataformas objetivo y robots.txt; la licencia del proyecto es solo para fines de aprendizaje e investigación.

> ⚠️ **Recordatorio del Servicio Backend**: La siguiente interfaz visual WebUI depende del servicio API backend para funcionar. Antes del uso inicial, por favor **inicie el backend por separado primero** (al usar el servidor de desarrollo frontend, use el puerto 8083 para coincidir con el destino del proxy `/api`):
>
> ```shell
> uv run uvicorn api.main:app --port 8083 --reload
> ```
>
> Después de que el backend se inicie exitosamente, abra la interfaz WebUI (`http://localhost:5173/`). Si el backend no se ha iniciado, la página llamará a `/api/env/check` para una verificación de entorno en la primera visita y fallará. En este punto, puede hacer clic en "Omitir verificación" para omitirla temporalmente, pero la funcionalidad del rastreador no estará disponible.

## 🖥️ Interfaz de Operación Visual WebUI

WeMediaCrawler proporciona una interfaz de operación visual basada en web, permitiéndole usar fácilmente las funciones del rastreador sin la línea de comandos.

#### Desarrollo (Recomendado)

Para el desarrollo, debe iniciar tanto el servicio API backend como el servidor de desarrollo Vite frontend:

```shell
# Terminal 1: iniciar servidor API (el servidor de desarrollo frontend redirige /api a 8083, así que usa 8083 aquí)
uv run uvicorn api.main:app --port 8083 --reload

# Terminal 2: iniciar servidor de desarrollo frontend
cd webui
npm install
npm run dev        # se inicia en el puerto 5173 y redirige /api a 8083
```

Después de iniciar exitosamente, visite `http://localhost:5173/` para abrir la interfaz WebUI.

> En el primer inicio, se realiza una verificación de entorno (llama a `/api/env/check`), así que asegúrese de que el servicio backend esté en ejecución. Si la verificación falla, puede hacer clic en "Omitir verificación" para omitirla temporalmente.

#### Construir para Producción

Si desea que el servidor API sirva directamente los recursos estáticos de WebUI, construya el frontend primero:

```shell
cd webui
npm install
npm run build      # la salida va a gh-pages-dist/
```

Después de compilar, copie la salida en el directorio servido por el servidor API (`api/webui/`), luego inicie el servidor API:

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

## 💾 Almacenamiento de Datos

WeMediaCrawler soporta múltiples métodos de almacenamiento de datos, incluyendo CSV, JSON, JSONL, Excel, SQLite y bases de datos MySQL.

📖 **Para instrucciones de uso detalladas, por favor vea: [Guía de Almacenamiento de Datos](docs/data_storage_guide.md)**

## 📚 Referencias

- **Repositorio del Proyecto Original**: [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler)
- **Repositorio de Firmas Xiaohongshu**: [Repositorio de firmas xhs de Cloxl](https://github.com/Cloxl/xhshow)
- **Cliente Xiaohongshu**: [Repositorio xhs de ReaJason](https://github.com/ReaJason/xhs)
- **Reenvío de SMS**: [Repositorio de referencia SmsForwarder](https://github.com/pppscn/SmsForwarder)
- **Herramienta de Penetración Interna**: [Documentación oficial de ngrok](https://ngrok.com/docs/)

---
## ⭐ Apoya Este Proyecto

Si WeMediaCrawler te ha resultado útil, ¡una ⭐️ Star sería muy bienvenida!

Cada muestra de apoyo me impulsa a seguir mejorándolo.

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

> Este fork es mantenido por **Aswellle** ([https://github.com/Aswellle/WeMediaCrawler](https://github.com/Aswellle/WeMediaCrawler)).

### 1. Naturaleza de la Rama
Este repositorio es un fork independiente de [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler). Este fork aplica mejoras de UI/UX y mejoras de características sobre el proyecto original (consulte la sección [Contribuciones de la Rama](#-contribuciones-de-la-rama) arriba).

### 2. División de Responsabilidad
- Los derechos de autor y la responsabilidad del **código del proyecto original** (lógica central del rastreador, implementaciones de rastreo por plataforma, capa de almacenamiento, infraestructura de proxy/caché, etc.) pertenecen al autor original NanmiCoder/relakkes.
- **Las modificaciones de este fork** (rediseño de WebUI, optimización de la experiencia de interacción y todo el código añadido o modificado en esta rama) son el derecho y la responsabilidad correspondientes de Aswellle.
- Los usuarios de este fork deben saber que estas modificaciones no han sido revisadas por el autor original, quien no asume ninguna responsabilidad por ellas.

### 3. Aviso de Uso
- Este fork es **solo para fines de aprendizaje e investigación**. El uso comercial o cualquier fin ilegal está estrictamente prohibido.
- Este fork está licenciado bajo la [NON-COMMERCIAL LEARNING LICENSE 1.1](LICENSE) del proyecto original; los términos de esa licencia siguen vigentes para el fork en su conjunto.
- Por cualquier responsabilidad legal o pérdida derivada del uso de este fork (incluido el código original y las modificaciones), Aswellle asume responsabilidad solo por las partes que modificó y no asume responsabilidad por daños directos o indirectos.
- Si las modificaciones de este fork cambian la arquitectura del proyecto original, los usuarios deben evaluar los riesgos correspondientes por sí mismos.

### 4. Declaración de Propiedad Intelectual
Los derechos de autor del código añadido o modificado en este fork pertenecen a Aswellle; los derechos de autor del código del proyecto original siguen perteneciendo a relakkes@gmail.com. Usar este fork significa que usted reconoce y acepta todos los términos de este descargo de responsabilidad y de la licencia del proyecto original.

### 5. Retroalimentación de Problemas
- Si un problema se origina en el **código del proyecto original**, repórtelo a [NanmiCoder/MediaCrawler](https://github.com/NanmiCoder/MediaCrawler/issues).
- Si un problema se origina en **las modificaciones de este fork** (WebUI, experiencia de interacción, etc.), repórtelo a través de los [Issues](https://github.com/Aswellle/WeMediaCrawler/issues) de este repositorio.
