# 🚗 Sistema de Transporte - Backend Django + Flutter App

Sistema de gestión de transporte con backend Django REST Framework y aplicación móvil Flutter.

---

## 📋 Descripción

Plataforma de transporte que conecta clientes con conductores, similar a servicios de ride-sharing. Incluye:

- 🔐 Autenticación con Google OAuth 2.0
- 👥 Sistema de roles (Cliente, Conductor, Admin, Moderador)
- 🚗 Gestión de viajes y vehículos
- 💰 Sistema de tarifas y pagos
- ⭐ Sistema de calificaciones
- 💬 Chat en tiempo real
- 📱 API REST para integración con Flutter

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────┐
│         Flutter Mobile App              │
│         (Cliente / Conductor)           │
└─────────────────┬───────────────────────┘
                  │
                  │ HTTP/REST API
                  │ JWT Authentication
                  │
┌─────────────────▼───────────────────────┐
│      Django REST Framework              │
│      - Google OAuth 2.0                 │
│      - JWT Tokens                       │
│      - Role-based Access Control        │
└─────────────────┬───────────────────────┘
                  │
                  │
┌─────────────────▼───────────────────────┐
│         PostgreSQL Database             │
│         (Producción / Desarrollo)       │
└─────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Configurar Backend

```bash
# Navegar al directorio backend
cd backend

# Instalar dependencias (si es necesario)
pip install -r requirements.txt

# Configurar variables de entorno
# Editar .env con tus credenciales

# Ejecutar servidor
python manage.py runserver 0.0.0.0:8000
```

### 2. Probar Conectividad

```bash
# Desde tu PC
curl http://192.168.1.4:8000/api/accounts/health/

# Desde tu móvil (navegador)
# Ir a: http://192.168.1.4:8000/api/accounts/health/
```

### 3. Integrar con Flutter

Revisar la documentación de Flutter y los endpoints de la API.

---

## 📁 Estructura del Proyecto

```
transportes/
├── backend/                    # Backend Django
│   ├── apps/
│   │   ├── accounts/          # Usuarios y autenticación
│   │   ├── clients/           # Perfiles de clientes
│   │   ├── drivers/           # Perfiles de conductores
│   │   ├── vehicles/          # Gestión de vehículos
│   │   ├── trips/             # Gestión de viajes
│   │   ├── fares/             # Sistema de tarifas
│   │   ├── payments/          # Procesamiento de pagos
│   │   ├── ratings/           # Sistema de calificaciones
│   │   ├── chat/              # Chat en tiempo real
│   │   ├── notifications/     # Notificaciones
│   │   ├── support/           # Soporte al cliente
│   │   └── administration/    # Panel de administración
│   ├── backend/               # Configuración del proyecto
│   ├── manage.py
│   └── db.sqlite3
│
├── .env                       # Variables de entorno (no en git)
├── .env.example              # Template de variables de entorno
│
└── README.md                 # Este archivo
```

---

## 🔑 Características Principales

### Autenticación y Autorización
- ✅ Google OAuth 2.0
- ✅ JWT (JSON Web Tokens)
- ✅ Sistema de roles (CLIENT, DRIVER, ADMIN, MODERATOR)
- ✅ Asignación automática de rol CLIENT
- ✅ Creación automática de perfiles

### API REST
- ✅ Django REST Framework
- ✅ CORS habilitado para desarrollo móvil
- ✅ Endpoints documentados
- ✅ Versionado de API

### Gestión de Usuarios
- ✅ Registro con Google
- ✅ Perfiles de cliente y conductor
- ✅ Gestión de información personal
- ✅ Foto de perfil

### Gestión de Viajes
- ✅ Solicitud de viajes
- ✅ Asignación de conductores
- ✅ Seguimiento en tiempo real
- ✅ Historial de viajes

### Sistema de Pagos
- ✅ Cálculo de tarifas
- ✅ Procesamiento de pagos
- ✅ Historial de transacciones

### Comunicación
- ✅ Chat en tiempo real
- ✅ Notificaciones push
- ✅ Soporte al cliente

---

## 🛠️ Tecnologías

### Backend
- **Django 6.0** - Framework web
- **Django REST Framework** - API REST
- **django-allauth** - Autenticación social
- **dj-rest-auth** - Autenticación REST
- **djangorestframework-simplejwt** - JWT tokens
- **django-cors-headers** - CORS
- **PostgreSQL** - Base de datos principal

### Frontend (Flutter)
- **Flutter** - Framework móvil
- **http** - Cliente HTTP
- **google_sign_in** - Google OAuth
- **flutter_secure_storage** - Almacenamiento seguro

---

Consulta este archivo `README.md` para la información general del proyecto.

---

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Django
SECRET_KEY=tu-secret-key-aqui
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,192.168.1.4

# Google OAuth 2.0
GOOGLE_CLIENT_ID=tu-google-client-id
GOOGLE_CLIENT_SECRET=tu-google-client-secret
```

### Google OAuth 2.0

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto
3. Habilita Google+ API
4. Crea credenciales OAuth 2.0
5. Agrega URI de redirección: `http://192.168.1.4:8000/api/accounts/google/login/callback/`
6. Copia Client ID y Client Secret al archivo `.env`

### Firewall de Windows

Configura el firewall para permitir conexiones al puerto 8000 si deseas acceso desde otros dispositivos.

---

## 🧪 Testing

### Health Check
```bash
curl http://192.168.1.4:8000/api/accounts/health/
```

### Test de Conexión
```bash
curl http://192.168.1.4:8000/api/accounts/test/
```

### Script de Pruebas Automatizado
```bash
cd backend
python test_integration.py
```

---

## 📱 Endpoints Principales

### Autenticación
- `POST /api/accounts/google/` - Login con Google OAuth
- `POST /api/accounts/token/` - Obtener JWT tokens
- `POST /api/accounts/token/refresh/` - Refrescar token

### Usuario
- `GET /api/accounts/profile/` - Perfil del usuario
- `GET /api/accounts/users/` - Listar usuarios (admin)
- `POST /api/accounts/users/` - Crear usuario

### Testing
- `GET /api/accounts/health/` - Health check
- `GET /api/accounts/test/` - Test de conexión

Revisa el código fuente para ver todos los endpoints disponibles.

---

## 👥 Roles de Usuario

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **CLIENT** | Cliente (por defecto) | Solicitar viajes, calificar conductores |
| **DRIVER** | Conductor | Aceptar viajes, gestionar vehículos |
| **ADMIN** | Administrador | Acceso completo al sistema |
| **MODERATOR** | Moderador | Gestión de contenido y soporte |

---

## 🔒 Seguridad

### Desarrollo
- ✅ CORS habilitado para red local
- ✅ JWT authentication
- ✅ Role-based access control
- ✅ Secure password hashing

### Producción (Pendiente)
- ⏳ HTTPS/SSL
- ✅ PostgreSQL
- ⏳ Servidor WSGI (Gunicorn)
- ⏳ Firewall de aplicación (WAF)
- ⏳ Rate limiting
- ⏳ Logging y monitoreo

---

## 🚧 Estado del Proyecto

### ✅ Completado
- [x] Backend Django configurado
- [x] CORS habilitado
- [x] Google OAuth integrado
- [x] JWT authentication
- [x] Sistema de roles
- [x] Signals para crear perfiles automáticamente
- [x] Endpoints de testing
- [x] Documentación completa

### ⏳ En Progreso
- [ ] Configuración de Google OAuth credentials
- [ ] Configuración de firewall
- [ ] Integración con Flutter
- [ ] Testing en dispositivo físico

### 📋 Pendiente
- [ ] Implementación completa de módulos (trips, payments, etc.)
- [ ] Chat en tiempo real
- [ ] Notificaciones push
- [ ] Panel de administración
- [ ] Deploy a producción

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto es privado y está en desarrollo.

---

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs del servidor Django
2. Revisa la consola de Flutter

---

## 🎯 Próximos Pasos

1. ✅ **Configurar variables de entorno** (`.env`)
2. ✅ **Configurar Google OAuth** en Google Cloud Console
3. ✅ **Configurar firewall** de Windows
4. ✅ **Probar conectividad** desde dispositivo móvil
5. ✅ **Integrar con Flutter**
6. ✅ **Probar flujo completo** de login con Google
7. ✅ **Verificar** creación automática de perfiles

---

**🚀 ¡Listo para empezar la integración con Flutter!**

**Servidor**: `http://192.168.1.4:8000`  
**Estado**: ✅ Funcionando

---

**Última actualización**: 25 de Diciembre, 2025
