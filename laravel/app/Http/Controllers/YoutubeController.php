<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Facades\Log;

class YoutubeController extends Controller
{

private $fastapi_base;

public function __construct()
{
    $this->fastapi_base = config('services.fastapi.url', 'http://127.0.0.1:8001');
}

    public function getDetails( Request $request)
    {
        $response = Http::get($this->fastapi_base . "/details", [
            'url' => $request->url
        ]);
        if ($response->failed()) {
            return response()->json([
                'error' => 'Failed to fetch details',
                'details' => $response->json() ?? $response->body(),
            ], $response->status());
        }
        return response()->json($response->json());
    }

    public function downloadVideo(Request $request)
{
    try {
        $validator = Validator::make($request->all(), [
            'url' => 'required|url',
            'quality' => 'sometimes|string'
        ]);

        if ($validator->fails()) {
            return response()->json([
                'error' => 'Invalid parameters',
                'details' => $validator->errors()
            ], 422);
        }

        $fastApiResponse = Http::timeout(300)
            ->withOptions([
                'stream' => true,
                'verify' => config('app.env') !== 'local'
            ])
            ->get($this->fastapi_base . '/download/video', [
                'url' => $request->url,
                'quality' => $request->quality ?? '720p'
            ]);

        if ($fastApiResponse->failed()) {
            $error = $fastApiResponse->json()['detail'] ?? $fastApiResponse->body();
            
            Log::error('FastAPI request failed', [
                'status' => $fastApiResponse->status(),
                'error' => $error
            ]);
            
            return response()->json([
                'error' => 'Failed to download video',
                'details' => $error
            ], $fastApiResponse->status());
        }

        $headers = [
            'Content-Type' => $fastApiResponse->header('Content-Type', 'video/mp4'),
            'Content-Disposition' => $fastApiResponse->header('Content-Disposition', 'attachment; filename="video.mp4"'),
            'Cache-Control' => 'no-store, no-cache',
            'Pragma' => 'no-cache',
        ];

        if ($contentLength = $fastApiResponse->header('Content-Length')) {
            $headers['Content-Length'] = $contentLength;
        }

        if (ob_get_length()) {
            ob_clean();
        }

        return response()->stream(
            function () use ($fastApiResponse) {
                $body = $fastApiResponse->getBody();
                while (!$body->eof()) {
                    echo $body->read(1024 * 8); 
                    flush();
                }
            },
            200,
            $headers
        );

    } catch (\Exception $e) {
        Log::error('Video download exception', [
            'error' => $e->getMessage(),
            'trace' => $e->getTraceAsString()
        ]);

        return response()->json([
            'error' => 'Download failed',
            'message' => $e->getMessage()
        ], 500);
    }
}

    public function downloadAudio(Request $request)
    {
        try {
        $validator = Validator::make($request->all(), [
            'url' => 'required|url',
        ]);

        if ($validator->fails()) {
            return response()->json([
                'error' => 'Invalid parameters',
                'details' => $validator->errors()
            ], 422);
        }

        $fastApiResponse = Http::timeout(300)
            ->withOptions([
                'stream' => true,
                'verify' => config('app.env') !== 'local'
            ])
            ->get($this->fastapi_base . '/download/audio', [
                'url' => $request->url,
            ]);

        if ($fastApiResponse->failed()) {
            $error = $fastApiResponse->json()['detail'] ?? $fastApiResponse->body();
            
            Log::error('FastAPI request failed', [
                'status' => $fastApiResponse->status(),
                'error' => $error
            ]);
            
            return response()->json([
                'error' => 'Failed to download video',
                'details' => $error
            ], $fastApiResponse->status());
        }

        $headers = [
            'Content-Type' => $fastApiResponse->header('Content-Type', 'audio/mpeg'),
            'Content-Disposition' => $fastApiResponse->header('Content-Disposition', 'attachment; filename="audio.mp3"'),
            'Cache-Control' => 'no-store, no-cache',
            'Pragma' => 'no-cache',
        ];

        if ($contentLength = $fastApiResponse->header('Content-Length')) {
            $headers['Content-Length'] = $contentLength;
        }

        if (ob_get_length()) {
            ob_clean();
        }

        return response()->stream(
            function () use ($fastApiResponse) {
                $body = $fastApiResponse->getBody();
                while (!$body->eof()) {
                    echo $body->read(1024 * 8); 
                    flush();
                }
            },
            200,
            $headers
        );

    } catch (\Exception $e) {
        Log::error('Video download exception', [
            'error' => $e->getMessage(),
            'trace' => $e->getTraceAsString()
        ]);

        return response()->json([
            'error' => 'Download failed',
            'message' => $e->getMessage()
        ], 500);
    }
    }

    public function downloadPlaylistVideo(Request $request)
    {
        set_time_limit(600);
        
        try {
            $validator = Validator::make($request->all(), [
                'url' => 'required|url',
                'quality' => 'sometimes|string'
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'error' => 'Invalid parameters',
                    'details' => $validator->errors()
                ], 422);
            }

            $fastApiResponse = Http::timeout(600)
                ->withOptions([
                    'verify' => config('app.env') !== 'local'
                ])
                ->get($this->fastapi_base . '/download/playlist/video', [
                    'url' => $request->url,
                    'quality' => $request->quality ?? '720p'
                ]);

            if ($fastApiResponse->failed()) {
                $error = $fastApiResponse->json()['detail'] ?? $fastApiResponse->body();
                
                Log::error('FastAPI playlist video request failed', [
                    'status' => $fastApiResponse->status(),
                    'error' => $error
                ]);
                
                return response()->json([
                    'error' => 'Failed to download playlist videos',
                    'details' => $error
                ], $fastApiResponse->status());
            }

            $headers = [
                'Content-Type' => $fastApiResponse->header('Content-Type', 'application/zip'),
                'Content-Disposition' => $fastApiResponse->header('Content-Disposition', 'attachment; filename="playlist_videos.zip"'),
                'Cache-Control' => 'no-store, no-cache',
                'Pragma' => 'no-cache',
            ];

            if ($contentLength = $fastApiResponse->header('Content-Length')) {
                $headers['Content-Length'] = $contentLength;
            }

            if (ob_get_length()) {
                ob_clean();
            }

            return response($fastApiResponse->body(), 200, $headers);

        } catch (\Exception $e) {
            Log::error('Playlist video download exception', [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return response()->json([
                'error' => 'Download failed',
                'message' => $e->getMessage()
            ], 500);
        }
    }

    public function downloadPlaylistAudio(Request $request)
    {
        set_time_limit(600);
        
        try {
            $validator = Validator::make($request->all(), [
                'url' => 'required|url',
            ]);

            if ($validator->fails()) {
                return response()->json([
                    'error' => 'Invalid parameters',
                    'details' => $validator->errors()
                ], 422);
            }

            $fastApiResponse = Http::timeout(600) 
                ->withOptions([
                    'verify' => config('app.env') !== 'local'
                ])
                ->get($this->fastapi_base . '/download/playlist/audio', [
                    'url' => $request->url,
                ]);

            if ($fastApiResponse->failed()) {
                $error = $fastApiResponse->json()['detail'] ?? $fastApiResponse->body();
                
                Log::error('FastAPI playlist audio request failed', [
                    'status' => $fastApiResponse->status(),
                    'error' => $error
                ]);
                
                return response()->json([
                    'error' => 'Failed to download playlist audio',
                    'details' => $error
                ], $fastApiResponse->status());
            }

            $headers = [
                'Content-Type' => $fastApiResponse->header('Content-Type', 'application/zip'),
                'Content-Disposition' => $fastApiResponse->header('Content-Disposition', 'attachment; filename="playlist_audio.zip"'),
                'Cache-Control' => 'no-store, no-cache',
                'Pragma' => 'no-cache',
            ];

            if ($contentLength = $fastApiResponse->header('Content-Length')) {
                $headers['Content-Length'] = $contentLength;
            }

            if (ob_get_length()) {
                ob_clean();
            }

            return response($fastApiResponse->body(), 200, $headers);

        } catch (\Exception $e) {
            Log::error('Playlist audio download exception', [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            return response()->json([
                'error' => 'Download failed',
                'message' => $e->getMessage()
            ], 500);
        }
    }

}