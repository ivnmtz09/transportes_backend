"""
Script para configurar GDAL en Windows automáticamente
Añade las rutas de OSGeo4W al PATH y configura las variables de entorno
"""
import os
import sys


def configure_gdal_windows():
    """
    Configura GDAL para Windows buscando OSGeo4W en las ubicaciones comunes
    """
    if os.name != 'nt':
        print("Este script es solo para Windows")
        return False
    
    # Ubicaciones comunes de OSGeo4W
    possible_paths = [
        r"C:\OSGeo4W64",
        r"C:\OSGeo4W",
        r"C:\Program Files\QGIS 3.34.3",
        r"C:\Program Files\QGIS 3.28",
        r"C:\Program Files\QGIS 3.22",
    ]
    
    osgeo_path = None
    for path in possible_paths:
        if os.path.isdir(path):
            osgeo_path = path
            print(f"✓ Encontrado OSGeo4W en: {path}")
            break
    
    if not osgeo_path:
        print("✗ No se encontró OSGeo4W instalado")
        print("\nPor favor, instala OSGeo4W desde:")
        print("https://trac.osgeo.org/osgeo4w/")
        print("\nO instala QGIS que incluye OSGeo4W:")
        print("https://qgis.org/download/")
        return False
    
    # Configurar variables de entorno
    os.environ['OSGEO4W_ROOT'] = osgeo_path
    os.environ['GDAL_DATA'] = os.path.join(osgeo_path, "share", "gdal")
    os.environ['PROJ_LIB'] = os.path.join(osgeo_path, "share", "proj")
    
    # Añadir al PATH
    bin_path = os.path.join(osgeo_path, "bin")
    if bin_path not in os.environ['PATH']:
        os.environ['PATH'] = bin_path + ";" + os.environ['PATH']
    
    print("\n✓ Variables de entorno configuradas:")
    print(f"  OSGEO4W_ROOT = {os.environ['OSGEO4W_ROOT']}")
    print(f"  GDAL_DATA = {os.environ['GDAL_DATA']}")
    print(f"  PROJ_LIB = {os.environ['PROJ_LIB']}")
    print(f"  PATH incluye: {bin_path}")
    
    return True


def test_gdal():
    """
    Prueba si GDAL está correctamente configurado
    """
    try:
        from django.contrib.gis.geos import Point
        p = Point(-72.9072, 11.5444, srid=4326)
        print("\n✓ GDAL está correctamente configurado!")
        print(f"  Punto de prueba: {p}")
        return True
    except Exception as e:
        print(f"\n✗ Error al probar GDAL: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Configuración de GDAL para Django PostGIS en Windows")
    print("=" * 60)
    
    if configure_gdal_windows():
        print("\n" + "=" * 60)
        print("Probando configuración...")
        print("=" * 60)
        
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        import django
        django.setup()
        
        test_gdal()
    else:
        sys.exit(1)
