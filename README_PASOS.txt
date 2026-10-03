DULCES MOMENTOS - V4 GRATIS
GitHub Pages + Supabase
================================

OBJETIVO
Esta versión no usa Render ni servidor Python.
- GitHub Pages publica la aplicación web.
- Supabase guarda productos, lotes, ventas y usuarios.
- Se puede abrir desde varios celulares o computadoras con Internet.
- Para comenzar se puede usar una misma cuenta autorizada en varios dispositivos.

ARCHIVOS
1. index.html
2. app.js
3. config.js
4. SUPABASE_SETUP.sql
5. AUTORIZAR_USUARIO.sql

PASO 1 - CREAR PROYECTO EN SUPABASE
1. Entra a https://supabase.com
2. Crea una cuenta e inicia un proyecto gratuito.
3. Espera a que el proyecto esté listo.

PASO 2 - CREAR LA BASE
1. En Supabase abre SQL Editor.
2. Crea una consulta nueva.
3. Copia TODO el contenido de SUPABASE_SETUP.sql.
4. Pulsa Run.

PASO 3 - CREAR EL USUARIO QUE ENTRARÁ A LA APP
1. Ve a Authentication > Users.
2. Pulsa Add user / Create new user.
3. Coloca un correo y una contraseña.
4. Luego abre SQL Editor y ejecuta AUTORIZAR_USUARIO.sql,
   reemplazando TU_CORREO@EJEMPLO.COM por ese mismo correo.

Para agregar más personas:
- Crea otro usuario en Authentication > Users.
- Ejecuta otra vez AUTORIZAR_USUARIO.sql con el nuevo correo.

PASO 4 - COPIAR LOS DATOS PÚBLICOS DE CONEXIÓN
1. En Supabase abre Project Settings > API.
2. Copia:
   - Project URL
   - Publishable key o anon public key
3. Abre config.js.
4. Reemplaza:
   PEGA_AQUI_TU_SUPABASE_URL
   PEGA_AQUI_TU_CLAVE_PUBLICA_ANON_O_PUBLISHABLE

IMPORTANTE:
NUNCA copies una clave service_role al archivo config.js ni a GitHub.

PASO 5 - SUBIR A GITHUB
Puedes usar el repositorio "dulces-momentos" que ya creaste.
Para esta V4, en la raíz del repositorio deben quedar:
- index.html
- app.js
- config.js
- SUPABASE_SETUP.sql
- AUTORIZAR_USUARIO.sql
- README_PASOS.txt (este archivo, si deseas subirlo)

Los archivos viejos de Render (app.py, requirements.txt, render.yaml, Procfile)
ya no son necesarios para esta versión.

PASO 6 - ACTIVAR GITHUB PAGES
1. En tu repositorio abre Settings.
2. Entra a Pages.
3. En Build and deployment elige "Deploy from a branch".
4. Branch: main
5. Folder: / (root)
6. Guarda.
7. GitHub mostrará la dirección de tu página cuando esté publicada.

PRUEBA
1. Abre el enlace de GitHub Pages.
2. Ingresa con el correo y contraseña creados en Supabase.
3. Crea un producto.
4. Registra una entrada con lote y vencimiento.
5. Registra una venta.
6. Verifica que el stock baje.

FUNCIONES INCLUIDAS EN ESTA V4
- Inicio de sesión.
- Productos y precios.
- Entradas a vitrina por lote.
- Fecha de ingreso y vencimiento.
- Estado Vigente / Por vencer / Vencido / Agotado.
- Venta y descuento automático del stock.
- Dashboard de unidades, vencimientos y valor de vitrina.
- Reporte de ventas del día y del mes.
- Uso desde varios dispositivos.

NOTA SOBRE COSTO
GitHub Pages puede usarse con GitHub Free en repositorios públicos.
Supabase ofrece un plan Free sujeto a sus cuotas y políticas vigentes.
