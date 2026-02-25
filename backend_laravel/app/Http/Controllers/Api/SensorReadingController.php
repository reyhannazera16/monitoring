<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\SensorReading;
use App\Utils\AirQualityStandards;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\DB;

class SensorReadingController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $readings = SensorReading::orderBy('timestamp', 'desc')->paginate(50);
        return response()->json($readings);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $validator = Validator::make($request->all(), [
            'co2_ppm' => 'required|numeric',
            'co_ppm' => 'required|numeric',
            'mq7_detected' => 'boolean',
            'location' => 'string',
            'status' => 'string|nullable',
            'timestamp' => 'date_format:Y-m-d H:i:s|nullable',
        ]);

        if ($validator->fails()) {
            return response()->json($validator->errors(), 422);
        }

        $data = $request->all();
        if (!isset($data['timestamp'])) {
            $data['timestamp'] = now()->format('Y-m-d H:i:s');
        }

        $reading = SensorReading::create($data);

        return response()->json([
            'success' => true,
            'data' => $reading,
        ], 210);
    }

    /**
     * Latest sensor reading
     */
    public function latest(Request $request)
    {
        $location = $request->query('location', 'Perkotaan');
        $reading = SensorReading::where('location', $location)
            ->orderBy('timestamp', 'desc')
            ->first();

        if ($reading) {
            $reading->co2_classification = AirQualityStandards::classify('co2', $reading->co2_ppm);
            $reading->co_classification = AirQualityStandards::classify('co', $reading->co_ppm);
        }

        return response()->json([
            'success' => true,
            'data' => $reading
        ]);
    }

    /**
     * Historical data
     */
    public function historical(Request $request)
    {
        $location = $request->query('location', 'Perkotaan');
        $limit = $request->query('limit', 500);

        $readings = SensorReading::where('location', $location)
            ->orderBy('timestamp', 'desc')
            ->limit($limit)
            ->get();

        foreach ($readings as $reading) {
            $reading->co2_classification = AirQualityStandards::classify('co2', $reading->co2_ppm);
            $reading->co_classification = AirQualityStandards::classify('co', $reading->co_ppm);
        }

        return response()->json([
            'success' => true,
            'count' => count($readings),
            'data' => $readings->reverse()->values() // Return in chronological order for charts
        ]);
    }

    /**
     * Summary statistics
     */
    public function statistics(Request $request)
    {
        $location = $request->query('location', 'Perkotaan');

        $stats = SensorReading::where('location', $location)
            ->select(
            DB::raw('COUNT(*) as total_readings'),
            DB::raw('AVG(co2_ppm) as avg_co2'),
            DB::raw('AVG(co_ppm) as avg_co'),
            DB::raw('MIN(co2_ppm) as min_co2'),
            DB::raw('MAX(co2_ppm) as max_co2'),
            DB::raw('MIN(co_ppm) as min_co'),
            DB::raw('MAX(co_ppm) as max_co')
        )
            ->first();

        $statsArray = $stats->toArray();
        if ($statsArray['avg_co2']) {
            $statsArray['avg_co2_classification'] = AirQualityStandards::classify('co2', $statsArray['avg_co2']);
        }
        if ($statsArray['avg_co']) {
            $statsArray['avg_co_classification'] = AirQualityStandards::classify('co', $statsArray['avg_co']);
        }

        return response()->json([
            'success' => true,
            'statistics' => $statsArray
        ]);
    }

    /**
     * Predictions placeholder
     */
    public function predictions(Request $request, $parameter)
    {
        $location = $request->query('location', 'Perkotaan');

        // Mock prediction data since ARIMA is complex in PHP
        $predictions = [];
        $now = now();

        for ($i = 1; $i <= 24; $i++) {
            $date = $now->copy()->addHours($i);
            $value = ($parameter === 'co2') ? random_int(400, 600) : random_int(1, 10) / 10;

            $predictions[] = [
                'prediction_date' => $date->toIso8601String(),
                'predicted_value' => $value,
                'confidence_lower' => $value * 0.9,
                'confidence_upper' => $value * 1.1,
                'classification' => AirQualityStandards::classify($parameter, $value)
            ];
        }

        return response()->json([
            'success' => true,
            'parameter' => $parameter,
            'count' => count($predictions),
            'model_metadata' => [
                'model_params' => ['p' => 1, 'd' => 1, 'q' => 1],
                'aic' => 150.5
            ],
            'data' => $predictions
        ]);
    }

        /**
     * Survival analysis based on real sensor data with linear regression
     */
    public function survivalAnalysis(Request $request)
    {
        $location = $request->query('location', 'Perkotaan');
        $locationLabel = $location === 'Perkotaan' ? 'Permukiman Industri' : 'Pedesaan';

        $readings = SensorReading::where('location', $location)
            ->orderBy('timestamp', 'asc')
            ->limit(500)
            ->get();

        if ($readings->count() < 2) {
            return response()->json([
                'success' => true,
                'analysis' => [
                    'summary_message' => 'Data tidak cukup untuk analisis waktu bertahan.',
                    'overall_assessment' => [
                        'days_until_unhealthy' => null,
                        'days_until_hazardous' => null,
                        'status' => 'good'
                    ]
                ]
            ]);
        }

        $thresholds = [
            'co2' => ['tidak_sehat' => 1000, 'berbahaya' => 5000],
            'co'  => ['tidak_sehat' => 9, 'berbahaya' => 30],
        ];

        $avgCO2 = $readings->avg('co2_ppm');
        $avgCO = $readings->avg('co_ppm');

        $calcTrend = function ($values) {
            $n = count($values);
            if ($n < 2) return ['slope' => 0, 'lastValue' => $values[0] ?? 0];
            $sumX = 0; $sumY = 0; $sumXY = 0; $sumX2 = 0;
            for ($i = 0; $i < $n; $i++) {
                $sumX += $i;
                $sumY += $values[$i];
                $sumXY += $i * $values[$i];
                $sumX2 += $i * $i;
            }
            $slope = ($n * $sumXY - $sumX * $sumY) / ($n * $sumX2 - $sumX * $sumX);
            $intercept = ($sumY - $slope * $sumX) / $n;
            return ['slope' => $slope, 'lastValue' => $intercept + $slope * ($n - 1)];
        };

        $co2Trend = $calcTrend($readings->pluck('co2_ppm')->toArray());
        $coTrend = $calcTrend($readings->pluck('co_ppm')->toArray());

        $firstTime = strtotime($readings->first()->timestamp);
        $lastTime = strtotime($readings->last()->timestamp);
        $intervalDays = ($lastTime - $firstTime) / 86400 / ($readings->count() - 1);

        $projectDays = function ($trend, $threshold) use ($intervalDays) {
            if ($trend['lastValue'] >= $threshold) return 0;
            if ($trend['slope'] <= 0) return null;
            $steps = ($threshold - $trend['lastValue']) / $trend['slope'];
            $days = round($steps * $intervalDays);
            return $days > 0 ? (int) $days : null;
        };

        $co2Unhealthy = $projectDays($co2Trend, $thresholds['co2']['tidak_sehat']);
        $co2Hazardous = $projectDays($co2Trend, $thresholds['co2']['berbahaya']);
        $coUnhealthy = $projectDays($coTrend, $thresholds['co']['tidak_sehat']);
        $coHazardous = $projectDays($coTrend, $thresholds['co']['berbahaya']);

        $unhealthyArr = array_filter([$co2Unhealthy, $coUnhealthy], fn($v) => $v !== null);
        $hazardousArr = array_filter([$co2Hazardous, $coHazardous], fn($v) => $v !== null);

        $daysUnhealthy = count($unhealthyArr) > 0 ? min($unhealthyArr) : null;
        $daysHazardous = count($hazardousArr) > 0 ? min($hazardousArr) : null;

        if ($daysUnhealthy === 0) $status = 'critical';
        elseif ($daysUnhealthy !== null && $daysUnhealthy < 30) $status = 'warning';
        elseif ($daysUnhealthy !== null && $daysUnhealthy < 90) $status = 'caution';
        else $status = 'good';

        $avgCO2Str = number_format($avgCO2, 1);
        $avgCOStr = number_format($avgCO, 1);
        if ($daysUnhealthy === 0) {
            $summary = "PERINGATAN: Kualitas udara di wilayah {$locationLabel} sudah memasuki kategori Tidak Sehat. Rata-rata CO2: {$avgCO2Str} ppm, CO: {$avgCOStr} ppm.";
        } elseif ($daysUnhealthy !== null) {
            $summary = "Berdasarkan tren data sensor, wilayah {$locationLabel} diperkirakan dapat mempertahankan kualitas udara Baik-Sedang selama ~{$daysUnhealthy} hari ke depan. Rata-rata CO2: {$avgCO2Str} ppm, CO: {$avgCOStr} ppm.";
        } else {
            $summary = "Kualitas udara di wilayah {$locationLabel} terpantau stabil atau membaik. Rata-rata CO2: {$avgCO2Str} ppm, CO: {$avgCOStr} ppm. Tidak terdeteksi tren peningkatan menuju kategori Tidak Sehat.";
        }

        return response()->json([
            'success' => true,
            'analysis' => [
                'summary_message' => $summary,
                'overall_assessment' => [
                    'days_until_unhealthy' => $daysUnhealthy,
                    'days_until_hazardous' => $daysHazardous,
                    'status' => $status
                ]
            ]
        ]);
    }

    /**
     * Train models placeholder
     */
    public function train(Request $request)
    {
        return response()->json([
            'success' => true,
            'message' => 'Models trained successfully (Simulated)'
        ]);
    }

    /**
     * Export CSV
     */
    public function export(Request $request)
    {
        $location = $request->query('location', 'Perkotaan');
        $readings = SensorReading::where('location', $location)->get();

        $callback = function () use ($readings) {
            $file = fopen('php://output', 'w');
            fputcsv($file, ['ID', 'Timestamp', 'Location', 'CO2 PPM', 'CO PPM', 'Status']);

            foreach ($readings as $reading) {
                $locationLabel = $reading->location === 'Perkotaan' ? 'Permukiman Industri' : $reading->location;
                fputcsv($file, [
                    $reading->id,
                    $reading->timestamp,
                    $locationLabel,
                    $reading->co2_ppm,
                    $reading->co_ppm,
                    $reading->status,
                ]);
            }
            fclose($file);
        };

        return response()->stream($callback, 200, [
            "Content-type" => "text/csv",
            "Content-Disposition" => "attachment; filename=readings.csv",
            "Pragma" => "no-cache",
            "Cache-Control" => "must-revalidate, post-check=0, pre-check=0",
            "Expires" => "0"
        ]);
    }

    /**
     * Air quality standards
     */
    public function standards()
    {
        return response()->json([
            'success' => true,
            'standards' => [
                'co2' => AirQualityStandards::CO2_STANDARDS,
                'co' => AirQualityStandards::CO_STANDARDS
            ]
        ]);
    }

    /**
     * Display the specified resource.
     */
    public function show($id)
    {
        $reading = SensorReading::find($id);
        if (!$reading) {
            return response()->json(['message' => 'Not Found'], 404);
        }
        return response()->json($reading);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, $id)
    {
        $reading = SensorReading::find($id);
        if (!$reading) {
            return response()->json(['message' => 'Not Found'], 404);
        }

        $reading->update($request->all());

        return response()->json([
            'success' => true,
            'data' => $reading,
        ]);
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy($id)
    {
        $reading = SensorReading::find($id);
        if (!$reading) {
            return response()->json(['message' => 'Not Found'], 404);
        }

        $reading->delete();

        return response()->json([
            'success' => true,
            'message' => 'Deleted successfully',
        ]);
    }
}
