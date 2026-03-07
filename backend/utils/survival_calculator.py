"""
Survival Time Calculator
Analyzes predictions to determine how long air quality will remain healthy
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
from backend.utils.air_quality_standards import AirQualityStandards

class SurvivalCalculator:
    """Calculate survival time based on air quality predictions"""
    
    @staticmethod
    def find_threshold_crossing(predictions: pd.DataFrame, 
                               parameter: str,
                               threshold_category: str) -> Optional[datetime]:
        """
        Find when predictions cross a specific threshold
        
        Args:
            predictions: DataFrame with prediction_date and predicted_value
            parameter: 'co2' or 'co'
            threshold_category: Category to check (e.g., 'tidak_sehat')
            
        Returns:
            Datetime when threshold is crossed, or None
        """
        threshold_value = AirQualityStandards.get_threshold_value(parameter, threshold_category)
        
        if threshold_value is None:
            return None
        
        # Find first date where prediction exceeds threshold
        crossings = predictions[predictions['predicted_value'] >= threshold_value]
        
        if len(crossings) > 0:
            return crossings.iloc[0]['prediction_date']
        
        return None
    
    @staticmethod
    def calculate_survival_time(predictions_co2: pd.DataFrame,
                               predictions_co: pd.DataFrame,
                               current_date: datetime = None) -> Dict:
        """
        Calculate survival time analysis
        
        Args:
            predictions_co2: CO2 predictions DataFrame
            predictions_co: CO predictions DataFrame
            current_date: Current date (default: now)
            
        Returns:
            Dictionary with survival analysis
        """
        if current_date is None:
            current_date = datetime.now()
        
        result = {
            'current_date': current_date.isoformat(),
            'co2_analysis': {},
            'co_analysis': {},
            'overall_assessment': {},
            'recommendations': []
        }
        
        # Analyze CO2
        co2_unhealthy = SurvivalCalculator.find_threshold_crossing(
            predictions_co2, 'co2', 'tidak_sehat'
        )
        co2_hazardous = SurvivalCalculator.find_threshold_crossing(
            predictions_co2, 'co2', 'berbahaya'
        )
        
        result['co2_analysis'] = {
            'unhealthy_date': co2_unhealthy.isoformat() if co2_unhealthy else None,
            'hazardous_date': co2_hazardous.isoformat() if co2_hazardous else None,
            'days_until_unhealthy': (co2_unhealthy - current_date).days if co2_unhealthy else None,
            'days_until_hazardous': (co2_hazardous - current_date).days if co2_hazardous else None
        }
        
        # Analyze CO
        co_unhealthy = SurvivalCalculator.find_threshold_crossing(
            predictions_co, 'co', 'tidak_sehat'
        )
        co_hazardous = SurvivalCalculator.find_threshold_crossing(
            predictions_co, 'co', 'berbahaya'
        )
        
        result['co_analysis'] = {
            'unhealthy_date': co_unhealthy.isoformat() if co_unhealthy else None,
            'hazardous_date': co_hazardous.isoformat() if co_hazardous else None,
            'days_until_unhealthy': (co_unhealthy - current_date).days if co_unhealthy else None,
            'days_until_hazardous': (co_hazardous - current_date).days if co_hazardous else None
        }
        
        # Overall assessment
        unhealthy_dates = [d for d in [co2_unhealthy, co_unhealthy] if d is not None]
        hazardous_dates = [d for d in [co2_hazardous, co_hazardous] if d is not None]
        
        earliest_unhealthy = min(unhealthy_dates) if unhealthy_dates else None
        earliest_hazardous = min(hazardous_dates) if hazardous_dates else None
        
        result['overall_assessment'] = {
            'earliest_unhealthy_date': earliest_unhealthy.isoformat() if earliest_unhealthy else None,
            'earliest_hazardous_date': earliest_hazardous.isoformat() if earliest_hazardous else None,
            'days_until_unhealthy': (earliest_unhealthy - current_date).days if earliest_unhealthy else None,
            'days_until_hazardous': (earliest_hazardous - current_date).days if earliest_hazardous else None,
            'status': SurvivalCalculator._determine_status(earliest_unhealthy, earliest_hazardous, current_date)
        }
        
        # Generate summary message
        result['summary_message'] = SurvivalCalculator._generate_summary_message(
            result['overall_assessment'], current_date
        )
        
        # Generate recommendations
        result['recommendations'] = SurvivalCalculator._generate_recommendations(
            result['overall_assessment']
        )
        
        return result
    
    @staticmethod
    def _determine_status(unhealthy_date: Optional[datetime],
                         hazardous_date: Optional[datetime],
                         current_date: datetime) -> str:
        """Determine overall air quality status"""
        if unhealthy_date is None:
            return 'excellent'
        
        days_until_unhealthy = (unhealthy_date - current_date).days
        
        if days_until_unhealthy < 0:
            return 'critical'
        elif days_until_unhealthy < 30:
            return 'warning'
        elif days_until_unhealthy < 90:
            return 'caution'
        else:
            return 'good'
    
    @staticmethod
    def _generate_summary_message(assessment: Dict, current_date: datetime) -> str:
        """Generate human-readable summary message"""
        days_unhealthy = assessment.get('days_until_unhealthy')
        days_hazardous = assessment.get('days_until_hazardous')
        
        if days_unhealthy is None:
            return (
                "Berdasarkan prediksi ARIMA, permukiman industri ini diperkirakan dapat "
                "mempertahankan kualitas udara kategori 'Baik-Sedang' untuk periode prediksi "
                "yang tersedia (12 bulan ke depan). Tidak terdeteksi peningkatan signifikan "
                "yang akan membawa kualitas udara ke kategori 'Tidak Sehat'."
            )
        
        if days_unhealthy < 0:
            return (
                "PERINGATAN: Berdasarkan prediksi ARIMA, permukiman industri ini SUDAH "
                "berada dalam kategori 'Tidak Sehat'. Tindakan mitigasi segera diperlukan!"
            )
        
        unhealthy_date = datetime.fromisoformat(assessment['earliest_unhealthy_date'])
        unhealthy_str = unhealthy_date.strftime('%d %B %Y')
        
        message = (
            f"Berdasarkan prediksi ARIMA, permukiman industri ini dapat mempertahankan "
            f"kualitas udara kategori 'Baik-Sedang' hingga sekitar {unhealthy_str} "
            f"({days_unhealthy} hari dari sekarang). "
        )
        
        if days_hazardous is not None and days_hazardous > 0:
            hazardous_date = datetime.fromisoformat(assessment['earliest_hazardous_date'])
            hazardous_str = hazardous_date.strftime('%d %B %Y')
            message += (
                f"Setelah itu, diperkirakan akan memasuki kategori 'Tidak Sehat' dan "
                f"berpotensi mencapai kategori 'Berbahaya' pada {hazardous_str} "
                f"({days_hazardous} hari dari sekarang)."
            )
        else:
            message += (
                "Setelah itu, diperkirakan akan memasuki kategori 'Tidak Sehat'."
            )
        
        return message
    
    @staticmethod
    def _generate_recommendations(assessment: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        days_unhealthy = assessment.get('days_until_unhealthy')
        status = assessment.get('status')
        
        if status == 'critical':
            recommendations.extend([
                "SEGERA tingkatkan ventilasi di seluruh area permukiman",
                "Pasang sistem purifier udara di area dengan tingkat polusi tertinggi",
                "Kurangi atau hentikan sementara aktivitas industri yang menghasilkan emisi tinggi",
                "Lakukan monitoring kualitas udara secara real-time",
                "Pertimbangkan evakuasi sementara untuk kelompok rentan (anak-anak, lansia)",
                "Hubungi pihak berwenang untuk inspeksi dan tindakan darurat"
            ])
        elif status == 'warning':
            recommendations.extend([
                "Tingkatkan ventilasi dan sirkulasi udara",
                "Pasang purifier udara di area kritis",
                "Evaluasi dan optimalkan sistem filtrasi emisi industri",
                "Kurangi aktivitas outdoor yang berat",
                "Lakukan monitoring berkala (minimal 2x sehari)",
                "Siapkan rencana mitigasi darurat"
            ])
        elif status == 'caution':
            recommendations.extend([
                "Pastikan sistem ventilasi berfungsi optimal",
                "Pertimbangkan instalasi purifier udara",
                "Lakukan audit emisi industri secara berkala",
                "Monitor tren kualitas udara mingguan",
                "Edukasi warga tentang pentingnya kualitas udara",
                "Rencanakan peningkatan infrastruktur hijau (tanaman penyerap polutan)"
            ])
        else:
            recommendations.extend([
                "Pertahankan sistem ventilasi yang ada",
                "Lakukan monitoring rutin kualitas udara",
                "Jaga kebersihan lingkungan",
                "Tingkatkan area hijau di sekitar permukiman",
                "Edukasi warga tentang praktik ramah lingkungan"
            ])
        
        return recommendations
    
    @staticmethod
    def calculate_best_worst_scenarios(predictions: pd.DataFrame,
                                      parameter: str) -> Dict:
        """
        Calculate best and worst case scenarios using confidence intervals
        
        Args:
            predictions: DataFrame with confidence_lower and confidence_upper
            parameter: 'co2' or 'co'
            
        Returns:
            Dictionary with scenario analysis
        """
        # Best case: using lower confidence bound
        best_case_df = predictions.copy()
        best_case_df['predicted_value'] = best_case_df['confidence_lower']
        
        best_unhealthy = SurvivalCalculator.find_threshold_crossing(
            best_case_df, parameter, 'tidak_sehat'
        )
        
        # Worst case: using upper confidence bound
        worst_case_df = predictions.copy()
        worst_case_df['predicted_value'] = worst_case_df['confidence_upper']
        
        worst_unhealthy = SurvivalCalculator.find_threshold_crossing(
            worst_case_df, parameter, 'tidak_sehat'
        )
        
        current_date = datetime.now()
        
        return {
            'best_case': {
                'unhealthy_date': best_unhealthy.isoformat() if best_unhealthy else None,
                'days_until_unhealthy': (best_unhealthy - current_date).days if best_unhealthy else None
            },
            'worst_case': {
                'unhealthy_date': worst_unhealthy.isoformat() if worst_unhealthy else None,
                'days_until_unhealthy': (worst_unhealthy - current_date).days if worst_unhealthy else None
            }
        }
