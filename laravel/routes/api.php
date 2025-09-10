<?php

use App\Http\Controllers\YoutubeController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;





Route::get('/youtube/details', [YoutubeController::class, 'getDetails']);
Route::get('/youtube/download/video', [YoutubeController::class, 'downloadVideo']);
Route::get('/youtube/download/audio', [YoutubeController::class, 'downloadAudio']);
Route::get('/youtube/download/playlist/video', [YoutubeController::class, 'downloadPlaylistVideo']);
Route::get('/youtube/download/playlist/audio', [YoutubeController::class, 'downloadPlaylistAudio']);


