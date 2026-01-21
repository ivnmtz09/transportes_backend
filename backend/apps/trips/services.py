"""
Servicio para obtener rutas usando Mapbox Directions API
Protege la API Key en el backend
"""
import os
import requests
import polyline
from typing import Dict, List, Tuple


class RouteService:
    """
    Servicio para obtener rutas entre dos puntos usando Mapbox
    """
    MAPBOX_API_KEY = os.getenv('MAPBOX_API_KEY', '')
    MAPBOX_DIRECTIONS_URL = 'https://api.mapbox.com/directions/v5/mapbox/driving'
    
    @classmethod
    def get_route(cls, origin: Tuple[float, float], destination: Tuple[float, float]) -> Dict:
        """
        Obtiene la ruta entre origen y destino
        
        Args:
            origin: Tupla (longitude, latitude) del origen
            destination: Tupla (longitude, latitude) del destino
        
        Returns:
            Dict con la información de la ruta:
            {
                'route': List[Tuple[float, float]],  # Lista de puntos (lat, lng)
                'distance': float,  # Distancia en metros
                'duration': float,  # Duración en segundos
                'encoded_polyline': str  # Polyline codificado
            }
        """
        if not cls.MAPBOX_API_KEY:
            raise ValueError("MAPBOX_API_KEY no está configurada en las variables de entorno")
        
        # Construir la URL con las coordenadas
        # Mapbox espera: longitude,latitude;longitude,latitude
        coordinates = f"{origin[0]},{origin[1]};{destination[0]},{destination[1]}"
        url = f"{cls.MAPBOX_DIRECTIONS_URL}/{coordinates}"
        
        params = {
            'access_token': cls.MAPBOX_API_KEY,
            'geometries': 'polyline',  # Obtener polyline codificado
            'overview': 'full',  # Obtener la geometría completa
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('routes'):
                raise ValueError("No se encontró ninguna ruta")
            
            route_data = data['routes'][0]
            encoded_polyline = route_data['geometry']
            
            # Decodificar el polyline a lista de coordenadas
            decoded_route = polyline.decode(encoded_polyline)
            
            return {
                'route': decoded_route,  # Lista de (lat, lng)
                'distance': route_data['distance'],  # metros
                'duration': route_data['duration'],  # segundos
                'encoded_polyline': encoded_polyline,
            }
        
        except requests.RequestException as e:
            raise Exception(f"Error al obtener la ruta de Mapbox: {str(e)}")
    
    @classmethod
    def get_route_from_addresses(cls, origin_lat: float, origin_lng: float, 
                                 dest_lat: float, dest_lng: float) -> Dict:
        """
        Wrapper más simple para obtener rutas usando coordenadas separadas
        
        Args:
            origin_lat: Latitud del origen
            origin_lng: Longitud del origen
            dest_lat: Latitud del destino
            dest_lng: Longitud del destino
        
        Returns:
            Dict con la información de la ruta
        """
        origin = (origin_lng, origin_lat)
        destination = (dest_lng, dest_lat)
        return cls.get_route(origin, destination)
