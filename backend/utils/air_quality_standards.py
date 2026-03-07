"""
Air Quality Standards and Classification
Based on WHO, EPA, and Indonesian PP No. 22 Tahun 2021
"""
from typing import Dict, Tuple

class AirQualityStandards:
    """Air quality standards and classification"""
    
    # CO2 Standards (ppm)
    CO2_STANDARDS = {
        'baik': {'min': 0, 'max': 400, 'label': 'Baik', 'label_en': 'Good', 'color': '#10b981'},
        'sedang': {'min': 400, 'max': 1000, 'label': 'Sedang', 'label_en': 'Moderate', 'color': '#fbbf24'},
        'tidak_sehat': {'min': 1000, 'max': 2000, 'label': 'Tidak Sehat', 'label_en': 'Unhealthy', 'color': '#f97316'},
        'sangat_tidak_sehat': {'min': 2000, 'max': 5000, 'label': 'Sangat Tidak Sehat', 'label_en': 'Very Unhealthy', 'color': '#ef4444'},
        'berbahaya': {'min': 5000, 'max': 10000, 'label': 'Berbahaya', 'label_en': 'Hazardous', 'color': '#a855f7'}
    }
    
    # CO Standards (ppm)
    CO_STANDARDS = {
        'baik': {'min': 0, 'max': 4, 'label': 'Baik', 'label_en': 'Good', 'color': '#10b981'},
        'sedang': {'min': 4, 'max': 9, 'label': 'Sedang', 'label_en': 'Moderate', 'color': '#fbbf24'},
        'tidak_sehat': {'min': 9, 'max': 15, 'label': 'Tidak Sehat', 'label_en': 'Unhealthy', 'color': '#f97316'},
        'sangat_tidak_sehat': {'min': 15, 'max': 30, 'label': 'Sangat Tidak Sehat', 'label_en': 'Very Unhealthy', 'color': '#ef4444'},
        'berbahaya': {'min': 30, 'max': 100, 'label': 'Berbahaya', 'label_en': 'Hazardous', 'color': '#a855f7'}
    }
    
    @classmethod
    def classify_co2(cls, value: float) -> Dict:
        """
        Classify CO2 level
        
        Args:
            value: CO2 value in ppm
            
        Returns:
            Dictionary with classification details
        """
        for category, details in cls.CO2_STANDARDS.items():
            if details['min'] <= value < details['max']:
                return {
                    'category': category,
                    'label': details['label'],
                    'label_en': details['label_en'],
                    'color': details['color'],
                    'value': value,
                    'parameter': 'CO2',
                    'unit': 'ppm'
                }
        
        # If value exceeds all ranges, return hazardous
        return {
            'category': 'berbahaya',
            'label': 'Berbahaya',
            'label_en': 'Hazardous',
            'color': '#a855f7',
            'value': value,
            'parameter': 'CO2',
            'unit': 'ppm'
        }
    
    @classmethod
    def classify_co(cls, value: float) -> Dict:
        """
        Classify CO level
        
        Args:
            value: CO value in ppm
            
        Returns:
            Dictionary with classification details
        """
        for category, details in cls.CO_STANDARDS.items():
            if details['min'] <= value < details['max']:
                return {
                    'category': category,
                    'label': details['label'],
                    'label_en': details['label_en'],
                    'color': details['color'],
                    'value': value,
                    'parameter': 'CO',
                    'unit': 'ppm'
                }
        
        # If value exceeds all ranges, return hazardous
        return {
            'category': 'berbahaya',
            'label': 'Berbahaya',
            'label_en': 'Hazardous',
            'color': '#a855f7',
            'value': value,
            'parameter': 'CO',
            'unit': 'ppm'
        }
    
    @classmethod
    def get_threshold_value(cls, parameter: str, category: str) -> float:
        """
        Get threshold value for a specific category
        
        Args:
            parameter: 'co2' or 'co'
            category: Category name (e.g., 'tidak_sehat')
            
        Returns:
            Threshold value
        """
        standards = cls.CO2_STANDARDS if parameter.lower() == 'co2' else cls.CO_STANDARDS
        
        if category in standards:
            return standards[category]['min']
        
        return None
    
    @classmethod
    def get_all_thresholds(cls, parameter: str) -> Dict[str, float]:
        """
        Get all threshold values for a parameter
        
        Args:
            parameter: 'co2' or 'co'
            
        Returns:
            Dictionary of category: threshold_value
        """
        standards = cls.CO2_STANDARDS if parameter.lower() == 'co2' else cls.CO_STANDARDS
        
        return {
            category: details['min']
            for category, details in standards.items()
        }
    
    @classmethod
    def is_healthy(cls, parameter: str, value: float) -> bool:
        """
        Check if value is in healthy range (Baik or Sedang)
        
        Args:
            parameter: 'co2' or 'co'
            value: Value to check
            
        Returns:
            True if healthy, False otherwise
        """
        if parameter.lower() == 'co2':
            classification = cls.classify_co2(value)
        else:
            classification = cls.classify_co(value)
        
        return classification['category'] in ['baik', 'sedang']
    
    @classmethod
    def get_health_recommendations(cls, parameter: str, category: str) -> str:
        """
        Get health recommendations based on air quality category
        
        Args:
            parameter: 'co2' or 'co'
            category: Air quality category
            
        Returns:
            Recommendation text
        """
        recommendations = {
            'baik': 'Kualitas udara sangat baik. Tidak ada tindakan khusus yang diperlukan.',
            'sedang': 'Kualitas udara dapat diterima. Pertimbangkan ventilasi yang baik.',
            'tidak_sehat': 'Kualitas udara tidak sehat. Tingkatkan ventilasi, kurangi aktivitas luar ruangan yang berat. Pertimbangkan penggunaan purifier udara.',
            'sangat_tidak_sehat': 'Kualitas udara sangat tidak sehat! Segera tingkatkan ventilasi, hindari aktivitas luar ruangan. Gunakan purifier udara dan masker jika diperlukan.',
            'berbahaya': 'BAHAYA! Kualitas udara berbahaya untuk kesehatan. Evakuasi area jika memungkinkan. Gunakan masker respirator dan purifier udara. Hubungi pihak berwenang.'
        }
        
        return recommendations.get(category, 'Tidak ada rekomendasi tersedia.')
