<?php

namespace App\Utils;

class AirQualityStandards
{
    public const CO2_STANDARDS = [
        'baik' => ['min' => 0, 'max' => 400, 'label' => 'Baik', 'label_en' => 'Good', 'color' => '#10b981'],
        'sedang' => ['min' => 400, 'max' => 1000, 'label' => 'Sedang', 'label_en' => 'Moderate', 'color' => '#fbbf24'],
        'tidak_sehat' => ['min' => 1000, 'max' => 2000, 'label' => 'Tidak Sehat', 'label_en' => 'Unhealthy', 'color' => '#f97316'],
        'sangat_tidak_sehat' => ['min' => 2000, 'max' => 5000, 'label' => 'Sangat Tidak Sehat', 'label_en' => 'Very Unhealthy', 'color' => '#ef4444'],
        'berbahaya' => ['min' => 5000, 'max' => 10000, 'label' => 'Berbahaya', 'label_en' => 'Hazardous', 'color' => '#a855f7'],
    ];

    public const CO_STANDARDS = [
        'baik' => ['min' => 0, 'max' => 4, 'label' => 'Baik', 'label_en' => 'Good', 'color' => '#10b981'],
        'sedang' => ['min' => 4, 'max' => 9, 'label' => 'Sedang', 'label_en' => 'Moderate', 'color' => '#fbbf24'],
        'tidak_sehat' => ['min' => 9, 'max' => 15, 'label' => 'Tidak Sehat', 'label_en' => 'Unhealthy', 'color' => '#f97316'],
        'sangat_tidak_sehat' => ['min' => 15, 'max' => 30, 'label' => 'Sangat Tidak Sehat', 'label_en' => 'Very Unhealthy', 'color' => '#ef4444'],
        'berbahaya' => ['min' => 30, 'max' => 100, 'label' => 'Berbahaya', 'label_en' => 'Hazardous', 'color' => '#a855f7'],
    ];

    public static function classify($parameter, $value)
    {
        $standards = ($parameter === 'co2') ? self::CO2_STANDARDS : self::CO_STANDARDS;

        foreach ($standards as $category => $details) {
            if ($value >= $details['min'] && $value < $details['max']) {
                return array_merge(['category' => $category], $details);
            }
        }

        return array_merge(['category' => 'berbahaya'], $standards['berbahaya']);
    }
}
