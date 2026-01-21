"""
Script de prueba para verificar la configuración de PostGIS y el sistema de ofertas
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from apps.trips.models import Trip, TripOffer
from apps.trips.services import RouteService


def test_postgis():
    """Prueba que PostGIS esté correctamente configurado"""
    print("\n" + "="*60)
    print("1. Probando PostGIS...")
    print("="*60)
    
    try:
        # Crear un punto de prueba
        point = Point(-72.9072, 11.5444, srid=4326)
        print(f"✓ Punto creado: {point}")
        print(f"  Latitud: {point.y}")
        print(f"  Longitud: {point.x}")
        print(f"  SRID: {point.srid}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_distance_query():
    """Prueba consultas de distancia con PostGIS"""
    print("\n" + "="*60)
    print("2. Probando consultas de distancia...")
    print("="*60)
    
    try:
        # Crear ubicación de prueba
        driver_location = Point(-72.9072, 11.5444, srid=4326)
        
        # Buscar viajes dentro de 5km
        trips = Trip.objects.filter(
            origin_location__dwithin=(driver_location, D(km=5))
        )
        
        print(f"✓ Consulta ejecutada correctamente")
        print(f"  Viajes encontrados dentro de 5km: {trips.count()}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_route_service():
    """Prueba el servicio de rutas (requiere MAPBOX_API_KEY)"""
    print("\n" + "="*60)
    print("3. Probando servicio de rutas...")
    print("="*60)
    
    mapbox_key = os.getenv('MAPBOX_API_KEY')
    if not mapbox_key or mapbox_key == 'your-mapbox-api-key-here':
        print("⚠ MAPBOX_API_KEY no configurada")
        print("  Configura MAPBOX_API_KEY en .env para probar este servicio")
        return None
    
    try:
        # Riohacha centro a Aeropuerto
        route_data = RouteService.get_route_from_addresses(
            origin_lat=11.5444,
            origin_lng=-72.9072,
            dest_lat=11.5233,
            dest_lng=-72.9261
        )
        
        print(f"✓ Ruta obtenida correctamente")
        print(f"  Distancia: {route_data['distance']:.2f} metros")
        print(f"  Duración: {route_data['duration']:.2f} segundos")
        print(f"  Puntos en la ruta: {len(route_data['route'])}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_models():
    """Prueba que los modelos estén correctamente configurados"""
    print("\n" + "="*60)
    print("4. Probando modelos...")
    print("="*60)
    
    try:
        # Verificar que los modelos existan
        print(f"✓ Modelo Trip: {Trip._meta.db_table}")
        print(f"  Campos: {[f.name for f in Trip._meta.fields]}")
        
        print(f"\n✓ Modelo TripOffer: {TripOffer._meta.db_table}")
        print(f"  Campos: {[f.name for f in TripOffer._meta.fields]}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("VERIFICACIÓN DEL SISTEMA DE OFERTAS - DRIVER GAITÁN")
    print("="*60)
    
    results = []
    
    # Ejecutar pruebas
    results.append(("PostGIS", test_postgis()))
    results.append(("Consultas de distancia", test_distance_query()))
    results.append(("Servicio de rutas", test_route_service()))
    results.append(("Modelos", test_models()))
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    
    for name, result in results:
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⚠ SKIP"
        print(f"{status} - {name}")
    
    # Verificar si todas las pruebas pasaron
    all_passed = all(r in [True, None] for _, r in results)
    
    if all_passed:
        print("\n✓ Todas las pruebas pasaron o fueron omitidas")
        print("\nPróximos pasos:")
        print("1. Configura MAPBOX_API_KEY en .env (si no lo has hecho)")
        print("2. Ejecuta: python manage.py makemigrations trips")
        print("3. Ejecuta: python manage.py migrate")
        print("4. Reinicia el servidor: python manage.py runserver")
    else:
        print("\n✗ Algunas pruebas fallaron")
        print("\nRevisa:")
        print("1. ¿Está GDAL instalado? (Ver POSTGIS_SETUP.md)")
        print("2. ¿Está PostGIS habilitado en PostgreSQL?")
        print("3. ¿Están las migraciones aplicadas?")


if __name__ == "__main__":
    main()
