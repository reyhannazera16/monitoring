<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\SensorReadingController;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

// Dashboard endpoints
Route::get('/data/latest', [SensorReadingController::class, 'latest']);
Route::get('/data/historical', [SensorReadingController::class, 'historical']);
Route::get('/statistics', [SensorReadingController::class, 'statistics']);
Route::get('/standards', [SensorReadingController::class, 'standards']);
Route::get('/predictions/{parameter}', [SensorReadingController::class, 'predictions']);
Route::get('/analysis/survival', [SensorReadingController::class, 'survivalAnalysis']);
Route::post('/model/train', [SensorReadingController::class, 'train']);
Route::get('/export/csv', [SensorReadingController::class, 'export']);
Route::post('/log', [SensorReadingController::class, 'store']); // Compat with Flask endpoint

Route::apiResource('sensor-readings', SensorReadingController::class);
