<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class SensorReading extends Model
{
    use HasFactory;

    protected $fillable = [
        'timestamp',
        'location',
        'co2_ppm',
        'co_ppm',
        'mq7_detected',
        'status',
    ];

    protected $casts = [
        'timestamp' => 'datetime',
        'mq7_detected' => 'boolean',
        'co2_ppm' => 'double',
        'co_ppm' => 'double',
    ];
}
