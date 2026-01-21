# Driver Gaitán - Backend API

API REST robusta desarrollada para la gestión integral de conductores, vehículos y servicios de transporte/domicilio.

## 🚀 Propósito
Esta API actúa como el núcleo del ecosistema Driver Gaitán, permitiendo la interacción fluida entre clientes y conductores, gestionando desde el registro de vehículos compartidos hasta la negociación dinámica de tarifas.

## ✅ Avances Recientes (Enero 2026)
- **Consolidación de Identidad**: Implementación de API Versioning (`/api/v1/`).
- **Gestión de Vehículos Flexible**: 
    - Cambio a relación **Many-to-Many** entre conductores y vehículos.
    - Validación estricta de placas colombianas (Carros: ABC123 | Motos: ABC12D).
    - Registro inteligente: si una placa ya existe, se vincula al nuevo conductor sin errores.
- **Sistema de Negociación**:
    - Implementación de `TripOffers`: los conductores pueden subastar sus precios para viajes solicitados.
    - Flujo de aceptación del cliente que asigna automáticamente al conductor y notifica el estado.
- **Internacionalización y Servicios**:
    - Soporte nativo para **Viajes** y **Domicilios**.
    - Etiquetas de UI localizadas en español.
- **Seguridad y Perfiles**:
    - Integración total con JWT (SimpleJWT).
    - Perfil de usuario enriquecido que muestra vehículos asociados y roles.
    - Limpieza automática de datos (borrado en cascada de vehículos si el usuario es el único propietario).

## 🛠️ Tecnologías
- **Core**: Python 3.x, Django 5.2.
- **API**: Django REST Framework (DRF).
- **Geolocalización**: PostGIS (Integral para búsqueda por radio y rutas).
- **Autenticación**: JWT (JSON Web Tokens) y Google OAuth2.
- **Base de Datos**: PostgreSQL / SQLite (Desarrollo).

## 📦 Instalación y Ejecución

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/ivnmtz09/transportes_backend.git
   cd transportes_backend
   ```

2. **Configurar el entorno**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Variables de Entorno**:
   Crea un archivo `.env` en la raíz con las credenciales necesarias (ver `.env.example` si está disponible).

4. **Migraciones y Servidor**:
   ```bash
   cd backend
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
   ```

---
*Desarrollado con ❤️ para la comunidad de Riohacha.*
