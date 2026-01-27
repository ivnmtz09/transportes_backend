# 🚗 Driver Gaitán - Backend API

Sistema de transporte colaborativo con sistema de subastas para conductores en Riohacha, La Guajira.

## 📋 Tabla de Contenidos

- [Características Principales](#características-principales)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Modelos de Datos](#modelos-de-datos)
- [Endpoints de la API](#endpoints-de-la-api)
- [Instalación y Configuración](#instalación-y-configuración)
- [Sistema de Roles y Permisos](#sistema-de-roles-y-permisos)
- [Flujo de Subastas](#flujo-de-subastas)

---

## 🎯 Características Principales

### ✅ Sistema de Subastas
- Los clientes publican viajes con precio estimado
- Los conductores hacen ofertas competitivas
- El cliente elige la mejor oferta
- Búsqueda geoespacial de viajes cercanos (5km de radio)

### ✅ Gestión de Vehículos
- Conductores pueden registrar múltiples vehículos
- Sistema de vehículo activo (`is_active`)
- Validación automática de placas colombianas
- Soporte para carros y motos

### ✅ Autenticación Robusta
- Login con Google OAuth 2.0
- JWT tokens (access + refresh)
- Roles: CLIENT, DRIVER, ADMIN, MODERATOR

### ✅ Geolocalización con PostGIS
- Cálculo de distancias reales
- Rutas optimizadas con Mapbox
- Filtrado de viajes por proximidad

---

## 🏗️ Arquitectura del Sistema

```
backend/
├── apps/
│   ├── accounts/      # Usuarios y autenticación
│   ├── drivers/       # Perfiles de conductores
│   ├── vehicles/      # Gestión de vehículos
│   ├── trips/         # Viajes y ofertas
│   ├── fares/         # Cálculo de tarifas
│   ├── ratings/       # Sistema de calificaciones
│   ├── chat/          # Mensajería (futuro)
│   ├── payments/      # Pagos (futuro)
│   └── notifications/ # Notificaciones (futuro)
├── backend/           # Configuración Django
└── manage.py
```

### Stack Tecnológico

- **Framework:** Django 5.2.9 + Django REST Framework
- **Base de Datos:** PostgreSQL 16 con PostGIS
- **Autenticación:** django-allauth + dj-rest-auth + JWT
- **Geolocalización:** PostGIS + Mapbox Directions API
- **Servidor:** Gunicorn (producción)

---

## 📊 Modelos de Datos

### User (accounts)
```python
- id, username, email, password
- first_name, last_name, phone_number
- role: CLIENT | DRIVER | ADMIN | MODERATOR
- profile_picture
```

### DriverProfile (drivers)
```python
- user (OneToOne)
- license_number
- is_verified (bool)
```

### Vehicle (vehicles)
```python
- drivers (ManyToMany con User)
- vehicle_type: CAR | MOTORCYCLE
- make, model, year, color
- license_plate (validación colombiana)
- is_active (bool) ⭐ NUEVO
```
**Validación de Placas:**
- Carros: `ABC123` (3 letras + 3 números)
- Motos: `ABC12D` (3 letras + 2 números + 1 letra)

### Trip (trips)
```python
- client, driver (opcional hasta aceptar)
- pickup_address, destination_address
- origin_location, destination_location (PostGIS Point)
- service_type: TRIP | DELIVERY
- vehicle_type: CAR | MOTORCYCLE
- status: REQUESTED | ACCEPTED | IN_PROGRESS | COMPLETED | CANCELLED
- estimated_price (DecimalField, max_digits=12) ⭐ EDITABLE
- created_at, updated_at
```

### TripOffer (trips)
```python
- trip, driver
- offered_price (DecimalField)
- estimated_arrival_time (minutos)
- status: PENDING | ACCEPTED | REJECTED
- created_at, updated_at
```

### Rating (trips) ⭐ NUEVO
```python
- trip (OneToOne)
- rater (User que califica)
- rated_driver (DriverProfile calificado)
- stars (0-5)
- comment (opcional)
- created_at
```

### Fare (fares)
```python
- trip (OneToOne)
- base_fare (según vehicle_type)
- distance_km
- surcharge_per_km
- amount (calculado automáticamente)
- currency (COP)
```

---

## 🔌 Endpoints de la API

### 🔐 Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/accounts/google/` | Login con Google OAuth |
| `POST` | `/api/v1/auth/login/` | Login tradicional (JWT) |
| `POST` | `/api/v1/token/refresh/` | Renovar access token |
| `POST` | `/api/v1/token/verify/` | Verificar token válido |

### 👤 Perfil de Usuario

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/accounts/profile/` | Obtener perfil completo |
| `PATCH` | `/api/v1/accounts/profile/` | Actualizar perfil |

**Respuesta del Perfil:**
```json
{
  "id": 1,
  "username": "ivan",
  "email": "ivan@example.com",
  "first_name": "Iván",
  "last_name": "Martínez",
  "role": "DRIVER",
  "phone_number": "+573001234567",
  "profile_picture": "url...",
  "is_admin": false,
  "stats": {
    "viajes_completados": 0,
    "calificacion": 5.0
  },
  "vehicles": [
    {
      "id": 1,
      "vehicle_type": "MOTORCYCLE",
      "make": "YAMAHA",
      "model": "FZ16",
      "license_plate": "ABC12D",
      "is_active": true
    }
  ]
}
```

### 🚗 Vehículos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/vehicles/` | Listar vehículos del conductor |
| `POST` | `/api/v1/vehicles/` | Registrar nuevo vehículo |
| `PATCH` | `/api/v1/vehicles/{id}/` | Actualizar vehículo |
| `PATCH` | `/api/v1/vehicles/{id}/set-active/` | ⭐ Activar vehículo |
| `POST` | `/api/v1/vehicles/{id}/set-active/` | ⭐ Activar vehículo (alias) |

**Endpoint `set-active`:**
- Activa el vehículo seleccionado (`is_active = true`)
- Desactiva automáticamente todos los demás del mismo conductor
- Solo un vehículo puede estar activo a la vez

### 🚕 Viajes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/trips/` | Listar viajes (filtrado por rol) |
| `POST` | `/api/v1/trips/` | Crear nuevo viaje (cliente) |
| `GET` | `/api/v1/trips/{id}/` | Detalle de viaje |
| `PATCH` | `/api/v1/trips/{id}/` | Actualizar viaje |
| `POST` | `/api/v1/trips/{id}/offer/` | Hacer oferta (conductor) |
| `GET` | `/api/v1/trips/{id}/offers/` | Ver ofertas (cliente) |
| `POST` | `/api/v1/trips/get_route/` | Obtener ruta Mapbox |

**Crear Viaje (Flexible):**
```json
{
  "pickup_address": "Calle 15 #5-20",
  "destination_address": "Av. La Marina #10-30",
  "pickup_latitude": 11.544,
  "pickup_longitude": -72.907,
  "destination_latitude": 11.550,
  "destination_longitude": -72.910,
  "service_type": "VIAJE",  // ⭐ Acepta: VIAJE, TRIP, DOMICILIO, DELIVERY
  "vehicle_type": "MOTORCYCLE",
  "estimated_price": 15000
}
```

**Sistema de Mapeo Automático:**
- `"VIAJE"` → se guarda como `"TRIP"`
- `"DOMICILIO"` → se guarda como `"DELIVERY"`
- También acepta directamente `"TRIP"` y `"DELIVERY"`

### 💰 Tarifas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/fares/estimate/` | Estimar precio de viaje |

**Estimación de Tarifa:**
```json
// Request
{
  "origin_lat": 11.544,
  "origin_lng": -72.907,
  "dest_lat": 11.550,
  "dest_lng": -72.910,
  "vehicle_type": "MOTORCYCLE"  // Opcional, default: CAR
}

// Response
{
  "estimated_price": 5000,  // Redondeado a centena
  "distance_km": 2.5,
  "duration_mins": 8,
  "currency": "COP"
}
```

**Tarifas Base:**
- **Moto:** $3.000 COP base + $1.000/km
- **Carro:** $7.000 COP base + $1.000/km

### 🏆 Estadísticas de Conductor

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/drivers/stats/` | Estadísticas del conductor |

```json
{
  "viajes_completados": 0,
  "calificacion": 5.0
}
```

### 🎯 Ofertas (Subastas)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/trips/offers/{id}/accept/` | Aceptar oferta (cliente) |

---

## 🔒 Sistema de Roles y Permisos

### CLIENT (Cliente)
✅ Crear viajes  
✅ Ver sus propios viajes  
✅ Ver ofertas de conductores  
✅ Aceptar/rechazar ofertas  
✅ Incrementar `estimated_price` del viaje  
❌ No puede ver vehículos  

### DRIVER (Conductor)
✅ Ver viajes disponibles (5km de radio)  
✅ Hacer ofertas en viajes  
✅ Registrar y gestionar vehículos  
✅ Activar/desactivar vehículos  
✅ Ver estadísticas propias  
❌ No puede crear viajes  

### ADMIN (Administrador) ⭐ CAPACIDADES INTEGRADAS
✅ **Todas las capacidades de DRIVER**  
✅ Ver todos los viajes del sistema  
✅ Ver todos los vehículos  
✅ Gestionar usuarios  
✅ Acceso al panel de Django Admin  

### Seguridad
- Todos los endpoints requieren autenticación JWT
- Permisos granulares por acción (list, create, update, delete)
- Validación de propiedad de recursos (IsOwnerOrAdmin)
- Auto-creación de DriverProfile para ADMIN si hace ofertas

---

## 🎲 Flujo de Subastas

```
1. CLIENTE crea viaje
   ├─ Define origen, destino, tipo de servicio
   ├─ Establece estimated_price inicial
   └─ Estado: REQUESTED

2. CONDUCTORES cercanos (5km) ven el viaje
   ├─ Pueden hacer ofertas con su precio
   └─ Cada conductor solo 1 oferta por viaje

3. CLIENTE revisa ofertas
   ├─ Ve precio, tiempo estimado, perfil del conductor
   └─ Puede incrementar estimated_price si no hay ofertas

4. CLIENTE acepta una oferta
   ├─ Viaje pasa a estado: ACCEPTED
   ├─ Se asigna el conductor
   └─ Todas las demás ofertas se rechazan automáticamente

5. CONDUCTOR completa el viaje
   ├─ Estado: IN_PROGRESS → COMPLETED
   └─ Se genera Rating para calificar
```

---

## 🛠️ Instalación y Configuración

### Requisitos Previos

- Python 3.11+
- PostgreSQL 16 con PostGIS
- GDAL (para geolocalización)

### 1. Clonar el Repositorio

```bash
git clone https://github.com/ivnmtz09/transportes_backend.git
cd transportes_backend
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crear archivo `.env` en la raíz:

```env
# Django
SECRET_KEY=tu-secret-key-super-segura
DEBUG=True

# Database
DB_NAME=driver_gaitan_db
DB_USER=postgres
DB_PASSWORD=tu-password
DB_HOST=localhost
DB_PORT=5432

# Google OAuth
GOOGLE_CLIENT_ID=tu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu-client-secret

# Mapbox
MAPBOX_API_KEY=tu-mapbox-api-key

# GDAL (Windows)
GDAL_LIBRARY_PATH=C:/OSGeo4W/bin/gdal309.dll
GEOS_LIBRARY_PATH=C:/OSGeo4W/bin/geos_c.dll
```

### 5. Configurar PostgreSQL con PostGIS

```sql
CREATE DATABASE driver_gaitan_db;
\c driver_gaitan_db
CREATE EXTENSION postgis;
```

### 6. Ejecutar Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Crear Superusuario

```bash
python manage.py createsuperuser
```

### 8. Ejecutar Servidor de Desarrollo

```bash
python manage.py runserver 0.0.0.0:8000
```

La API estará disponible en: `http://localhost:8000/api/v1/`

---

## 🚀 Despliegue en Producción

### Configuración de Producción

```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['tu-dominio.com', 'api.tu-dominio.com']

# Seguridad
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Servidor con Gunicorn

```bash
pip install gunicorn
gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Nginx (Proxy Reverso)

```nginx
server {
    listen 80;
    server_name api.tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /ruta/a/static/;
    }

    location /media/ {
        alias /ruta/a/media/;
    }
}
```

---

## 📝 Notas de Desarrollo

### Migraciones Recientes

- `trips.0007`: Añadido campo `estimated_price` editable
- `trips.0008`: Aumentado `max_digits` de `estimated_price` a 12
- `vehicles.0006`: Añadido campo `is_active` para vehículos

### Validaciones Especiales

1. **Placas de Vehículos:** Formato colombiano automático
2. **Service Type:** Mapeo español ↔ inglés transparente
3. **Coordenadas:** Conversión automática String → Float
4. **Vehículo Activo:** Solo uno activo por conductor

### Testing

```bash
# Ejecutar tests
python manage.py test

# Tests de integración
python test_integration.py
python test_ofertas.py
```

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto es privado y confidencial.

---

## 👨‍💻 Autor

**Iván Martínez**  
GitHub: [@ivnmtz09](https://github.com/ivnmtz09)

---

## 🎉 Estado del Proyecto

| Módulo | Estado | Logro |
|--------|--------|-------|
| Base de Datos | ✅ OK | PostgreSQL con PostGIS funcionando y limpio |
| Perfil | ✅ OK | Una sola pantalla que cambia según el rol (Adaptativa) |
| Vehículos | ✅ OK | El conductor decide qué moto/carro tiene "En uso" |
| Viajes | ✅ OK | Corregido error 400; servidor entiende peticiones del móvil |
| Roles | ✅ OK | Admin puede ser conductor; Cliente tiene menú completo |
| Subastas | ✅ OK | Sistema de ofertas competitivas funcionando |
| Geolocalización | ✅ OK | PostGIS + Mapbox integrados |
| Autenticación | ✅ OK | Google OAuth + JWT tokens |

**Última actualización:** 27 de enero de 2026

---

## 📞 Soporte

Para reportar bugs o solicitar features, abre un issue en GitHub.
