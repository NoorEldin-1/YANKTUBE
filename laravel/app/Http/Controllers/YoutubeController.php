<?php

// تحديد مساحة الاسم (namespace) للـ Controller، وهي App\Http\Controllers
namespace App\Http\Controllers;

// استيراد (use) فئة Request للوصول إلى بيانات الطلب (HTTP request)
use Illuminate\Http\Request;
// استيراد فئة Http لإرسال طلبات HTTP إلى خدمات خارجية (مثل FastAPI)
use Illuminate\Support\Facades\Http;
// استيراد فئة Validator للتحقق من صحة بيانات الطلب
use Illuminate\Support\Facades\Validator;
// استيراد فئة Log لتسجيل رسائل الأخطاء والأحداث
use Illuminate\Support\Facades\Log;

// تعريف فئة Controller التي ترث من الفئة الأساسية Controller
class YoutubeController extends Controller
{

// تعريف خاصية (property) خاصة لتخزين عنوان URL الأساسي لخدمة FastAPI
private $fastapi_base;

// دالة constructor تُنفّذ عند إنشاء كائن من الفئة
public function __construct()
{
    // تعيين قيمة الخاصية fastapi_base من ملف إعدادات الخدمات، أو استخدام قيمة افتراضية
    $this->fastapi_base = config('services.fastapi.url', 'http://127.0.0.1:8001');
}

    // دالة للتعامل مع نقطة النهاية (endpoint) الخاصة بالحصول على تفاصيل الفيديو
    public function getDetails( Request $request)
    {
        // إرسال طلب HTTP GET إلى نقطة نهاية /details في خدمة FastAPI
        $response = Http::get($this->fastapi_base . "/details", [
            // تمرير رابط الفيديو من طلب المستخدم كمعامل
            'url' => $request->url
        ]);
        // التحقق مما إذا كان الطلب إلى FastAPI قد فشل
        if ($response->failed()) {
            // إذا فشل، إرجاع استجابة JSON تحتوي على رسالة خطأ
            return response()->json([
                'error' => 'Failed to fetch details',
                'details' => $response->json() ?? $response->body(),
            ], $response->status());
        }
        // إذا نجح، إرجاع استجابة JSON ببيانات التفاصيل التي تم استلامها من FastAPI
        return response()->json($response->json());
    }

    // دالة للتعامل مع نقطة النهاية الخاصة بتنزيل الفيديو
    public function downloadVideo(Request $request)
{
    try {
        // إنشاء كائن Validator للتحقق من صحة المدخلات
        $validator = Validator::make($request->all(), [
            // تحديد أن الحقل 'url' مطلوب ويجب أن يكون رابطًا صالحًا
            'url' => 'required|url',
            // تحديد أن الحقل 'quality' اختياري ويمكن أن يكون نصًا
            'quality' => 'sometimes|string'
        ]);

        // التحقق مما إذا كان التحقق من الصحة قد فشل
        if ($validator->fails()) {
            // إذا فشل، إرجاع خطأ 422 مع تفاصيل الأخطاء
            return response()->json([
                'error' => 'Invalid parameters',
                'details' => $validator->errors()
            ], 422);
        }

        // إرسال طلب HTTP GET إلى نقطة نهاية /download/video في FastAPI
        $fastApiResponse = Http::timeout(300)
            // استخدام خيارات متقدمة للطلب
            ->withOptions([
                // تفعيل وضع التدفق (streaming) للتعامل مع الملفات الكبيرة
                'stream' => true,
                // التحقق من شهادة SSL إلا إذا كان التطبيق يعمل محليًا
                'verify' => config('app.env') !== 'local'
            ])
            ->get($this->fastapi_base . '/download/video', [
                // تمرير رابط الفيديو من طلب المستخدم
                'url' => $request->url,
                // تمرير الجودة المطلوبة أو استخدام '720p' كقيمة افتراضية
                'quality' => $request->quality ?? '720p'
            ]);

        // التحقق مما إذا كان الطلب إلى FastAPI قد فشل
        if ($fastApiResponse->failed()) {
            // الحصول على رسالة الخطأ من استجابة FastAPI
            $error = $fastApiResponse->json()['detail'] ?? $fastApiResponse->body();
            
            // تسجيل الخطأ في ملف السجل
            Log::error('FastAPI request failed', [
                'status' => $fastApiResponse->status(),
                'error' => $error
            ]);
            
            // إرجاع استجابة JSON تحتوي على رسالة خطأ
            return response()->json([
                'error' => 'Failed to download video',
                'details' => $error
            ], $fastApiResponse->status());
        }

        // الحصول على الترويسات (headers) من استجابة FastAPI
        $headers = [
            // تعيين Content-Type من ترويسة FastAPI أو قيمة افتراضية
            'Content-Type' => $fastApiResponse->header('Content-Type', 'video/mp4'),
            // تعيين Content-Disposition من ترويسة FastAPI أو قيمة افتراضية
            'Content-Disposition' => $fastApiResponse->header('Content-Disposition', 'attachment; filename="video.mp4"'),
            // منع التخزين المؤقت (caching) للملف
            'Cache-Control' => 'no-store, no-cache',
            'Pragma' => 'no-cache',
        ];

        // التحقق مما إذا كان هناك ترويسة Content-Length
        if ($contentLength = $fastApiResponse->header('Content-Length')) {
            // إذا وجدت، أضفها إلى ترويسات الاستجابة
            $headers['Content-Length'] = $contentLength;
        }

        // تنظيف المخزن المؤقت للإخراج (output buffer)
        if (ob_get_length()) {
            ob_clean();
        }

        // إرجاع استجابة تدفقية (streamed response) للمتصفح
        return response()->stream(
            // تعريف دالة الاستدعاء الخلفي (callback) التي ستدير التدفق
            function () use ($fastApiResponse) {
                // الحصول على جسم (body) الاستجابة
                $body = $fastApiResponse->getBody();
                // حلقة تستمر ما دام هناك بيانات في الجسم
                while (!$body->eof()) {
                    // قراءة 8 كيلوبايت من البيانات وإخراجها
                    echo $body->read(1024 * 8); // 8KB chunks
                    // إرسال البيانات إلى المتصفح على الفور
                    flush();
                }
            },
            // تحديد رمز حالة الاستجابة إلى 200 (OK)
            200,
            // تمرير ترويسات الاستجابة
            $headers
        );

    // التعامل مع أي استثناءات (exceptions) قد تحدث
    } catch (\Exception $e) {
        // تسجيل تفاصيل الاستثناء في ملف السجل
        Log::error('Video download exception', [
            'error' => $e->getMessage(),
            'trace' => $e->getTraceAsString()
        ]);

        // إرجاع استجابة JSON بخطأ عام 500
        return response()->json([
            'error' => 'Download failed',
            'message' => $e->getMessage()
        ], 500);
    }
}

    // دالة للتعامل مع نقطة النهاية الخاصة بتنزيل الصوت
    public function downloadAudio(Request $request)
    {
        try {
        // إنشاء كائن Validator للتحقق من صحة المدخلات
        $validator = Validator::make($request->all(), [
            // تحديد أن الحقل 'url' مطلوب ويجب أن يكون رابطًا صالحًا
            'url' => 'required|url',
        ]);

        // التحقق مما إذا كان التحقق من الصحة قد فشل
        if ($validator->fails()) {
            // إذا فشل، إرجاع خطأ 422 مع تفاصيل الأخطاء
            return response()->json([
                'error' => 'Invalid parameters',
                'details' => $validator->errors()
            ], 422);
        }

        // إرسال طلب HTTP GET إلى نقطة نهاية /download/audio في FastAPI
        $fastApiResponse = Http::timeout(300)
            // استخدام خيارات متقدمة للطلب
            ->withOptions([
                // تفعيل وضع التدفق (streaming)
                'stream' => true,
                // التحقق من شهادة SSL
                'verify' => config('app.env') !== 'local'
            ])
            ->get($this->fastapi_base . '/download/audio', [
                // تمرير رابط الفيديو
                'url' => $request->url,
            ]);

        // التحقق مما إذا كان الطلب إلى FastAPI قد فشل
        if ($fastApiResponse->failed()) {
            // الحصول على رسالة الخطأ
            $error = $fastApiResponse->json()['detail'] ?? $fastApiResponse->body();
            
            // تسجيل الخطأ في ملف السجل
            Log::error('FastAPI request failed', [
                'status' => $fastApiResponse->status(),
                'error' => $error
            ]);
            
            // إرجاع استجابة JSON تحتوي على رسالة خطأ
            return response()->json([
                'error' => 'Failed to download video',
                'details' => $error
            ], $fastApiResponse->status());
        }

        // الحصول على الترويسات من استجابة FastAPI
        $headers = [
            // تعيين Content-Type من ترويسة FastAPI أو قيمة افتراضية
            'Content-Type' => $fastApiResponse->header('Content-Type', 'audio/mpeg'),
            // تعيين Content-Disposition من ترويسة FastAPI أو قيمة افتراضية
            'Content-Disposition' => $fastApiResponse->header('Content-Disposition', 'attachment; filename="audio.mp3"'),
            // منع التخزين المؤقت
            'Cache-Control' => 'no-store, no-cache',
            'Pragma' => 'no-cache',
        ];

        // التحقق مما إذا كان هناك ترويسة Content-Length
        if ($contentLength = $fastApiResponse->header('Content-Length')) {
            // إذا وجدت، أضفها إلى ترويسات الاستجابة
            $headers['Content-Length'] = $contentLength;
        }

        // تنظيف المخزن المؤقت للإخراج
        if (ob_get_length()) {
            ob_clean();
        }

        // إرجاع استجابة تدفقية
        return response()->stream(
            // تعريف دالة الاستدعاء الخلفي
            function () use ($fastApiResponse) {
                // الحصول على جسم الاستجابة
                $body = $fastApiResponse->getBody();
                // حلقة تستمر ما دام هناك بيانات
                while (!$body->eof()) {
                    // قراءة 8 كيلوبايت من البيانات وإخراجها
                    echo $body->read(1024 * 8); // 8KB chunks
                    // إرسال البيانات إلى المتصفح على الفور
                    flush();
                }
            },
            // تحديد رمز حالة الاستجابة
            200,
            // تمرير ترويسات الاستجابة
            $headers
        );

    // التعامل مع أي استثناءات
    } catch (\Exception $e) {
        // تسجيل تفاصيل الاستثناء
        Log::error('Video download exception', [
            'error' => $e->getMessage(),
            'trace' => $e->getTraceAsString()
        ]);

        // إرجاع استجابة JSON بخطأ عام 500
        return response()->json([
            'error' => 'Download failed',
            'message' => $e->getMessage()
        ], 500);
    }
    }

    // دالة للتعامل مع نقطة النهاية الخاصة بتنزيل قائمة تشغيل من الفيديوهات
    public function downloadPlaylistVideo(Request $request)
    {
        // زيادة حد وقت التنفيذ (execution time limit) إلى 600 ثانية (10 دقائق) للتعامل مع التنزيلات الطويلة
        set_time_limit(600);
        
        try {
            // إنشاء كائن Validator للتحقق من صحة المدخلات
            $validator = Validator::make($request->all(), [
                // تحديد أن الحقل 'url' مطلوب ويجب أن يكون رابطًا صالحًا
                'url' => 'required|url',
                // تحديد أن الحقل 'quality' اختياري ويمكن أن يكون نصًا
                'quality' => 'sometimes|string'
            ]);

            // التحقق مما إذا كان التحقق من الصحة قد فشل
            if ($validator->fails()) {
                // إذا فشل، إرجاع خطأ 422 مع تفاصيل الأخطاء
                return response()->json([
                    'error' => 'Invalid parameters',
                    'details' => $validator->errors()
                ], 422);
            }

            // إرسال طلب HTTP GET إلى نقطة نهاية /download/playlist/video في FastAPI
            $fastApiResponse = Http::timeout(600) // زيادة المهلة (timeout) لتنزيل القوائم
                ->withOptions([
                    // التحقق من شهادة SSL
                    'verify' => config('app.env') !== 'local'
                ])
                ->get($this->fastapi_base . '/download/playlist/video', [
                    // تمرير رابط القائمة
                    'url' => $request->url,
                    // تمرير الجودة المطلوبة أو استخدام '720p' كقيمة افتراضية
                    'quality' => $request->quality ?? '720p'
                ]);

            // التحقق مما إذا كان الطلب إلى FastAPI قد فشل
            if ($fastApiResponse->failed()) {
                // الحصول على رسالة الخطأ
                $error = $fastApiResponse->json()['detail'] ?? $fastApiResponse->body();
                
                // تسجيل الخطأ في ملف السجل
                Log::error('FastAPI playlist video request failed', [
                    'status' => $fastApiResponse->status(),
                    'error' => $error
                ]);
                
                // إرجاع استجابة JSON تحتوي على رسالة خطأ
                return response()->json([
                    'error' => 'Failed to download playlist videos',
                    'details' => $error
                ], $fastApiResponse->status());
            }

            // الحصول على الترويسات من استجابة FastAPI
            $headers = [
                // تعيين Content-Type من ترويسة FastAPI أو قيمة افتراضية
                'Content-Type' => $fastApiResponse->header('Content-Type', 'application/zip'),
                // تعيين Content-Disposition من ترويسة FastAPI أو قيمة افتراضية
                'Content-Disposition' => $fastApiResponse->header('Content-Disposition', 'attachment; filename="playlist_videos.zip"'),
                // منع التخزين المؤقت
                'Cache-Control' => 'no-store, no-cache',
                'Pragma' => 'no-cache',
            ];

            // التحقق مما إذا كان هناك ترويسة Content-Length
            if ($contentLength = $fastApiResponse->header('Content-Length')) {
                // إذا وجدت، أضفها إلى ترويسات الاستجابة
                $headers['Content-Length'] = $contentLength;
            }

            // تنظيف المخزن المؤقت للإخراج
            if (ob_get_length()) {
                ob_clean();
            }

            // إرجاع محتوى الملف الكامل كاستجابة HTTP
            return response($fastApiResponse->body(), 200, $headers);

        // التعامل مع أي استثناءات
        } catch (\Exception $e) {
            // تسجيل تفاصيل الاستثناء
            Log::error('Playlist video download exception', [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            // إرجاع استجابة JSON بخطأ عام 500
            return response()->json([
                'error' => 'Download failed',
                'message' => $e->getMessage()
            ], 500);
        }
    }

    // دالة للتعامل مع نقطة النهاية الخاصة بتنزيل قائمة تشغيل من الملفات الصوتية
    public function downloadPlaylistAudio(Request $request)
    {
        // زيادة حد وقت التنفيذ إلى 600 ثانية (10 دقائق)
        set_time_limit(600);
        
        try {
            // إنشاء كائن Validator للتحقق من صحة المدخلات
            $validator = Validator::make($request->all(), [
                // تحديد أن الحقل 'url' مطلوب ويجب أن يكون رابطًا صالحًا
                'url' => 'required|url',
            ]);

            // التحقق مما إذا كان التحقق من الصحة قد فشل
            if ($validator->fails()) {
                // إذا فشل، إرجاع خطأ 422 مع تفاصيل الأخطاء
                return response()->json([
                    'error' => 'Invalid parameters',
                    'details' => $validator->errors()
                ], 422);
            }

            // إرسال طلب HTTP GET إلى نقطة نهاية /download/playlist/audio في FastAPI
            $fastApiResponse = Http::timeout(600) // زيادة المهلة لتنزيل القوائم
                ->withOptions([
                    // التحقق من شهادة SSL
                    'verify' => config('app.env') !== 'local'
                ])
                ->get($this->fastapi_base . '/download/playlist/audio', [
                    // تمرير رابط القائمة
                    'url' => $request->url,
                ]);

            // التحقق مما إذا كان الطلب إلى FastAPI قد فشل
            if ($fastApiResponse->failed()) {
                // الحصول على رسالة الخطأ
                $error = $fastApiResponse->json()['detail'] ?? $fastApiResponse->body();
                
                // تسجيل الخطأ في ملف السجل
                Log::error('FastAPI playlist audio request failed', [
                    'status' => $fastApiResponse->status(),
                    'error' => $error
                ]);
                
                // إرجاع استجابة JSON تحتوي على رسالة خطأ
                return response()->json([
                    'error' => 'Failed to download playlist audio',
                    'details' => $error
                ], $fastApiResponse->status());
            }

            // الحصول على الترويسات من استجابة FastAPI
            $headers = [
                // تعيين Content-Type من ترويسة FastAPI أو قيمة افتراضية
                'Content-Type' => $fastApiResponse->header('Content-Type', 'application/zip'),
                // تعيين Content-Disposition من ترويسة FastAPI أو قيمة افتراضية
                'Content-Disposition' => $fastApiResponse->header('Content-Disposition', 'attachment; filename="playlist_audio.zip"'),
                // منع التخزين المؤقت
                'Cache-Control' => 'no-store, no-cache',
                'Pragma' => 'no-cache',
            ];

            // التحقق مما إذا كان هناك ترويسة Content-Length
            if ($contentLength = $fastApiResponse->header('Content-Length')) {
                // إذا وجدت، أضفها إلى ترويسات الاستجابة
                $headers['Content-Length'] = $contentLength;
            }

            // تنظيف المخزن المؤقت للإخراج
            if (ob_get_length()) {
                ob_clean();
            }

            // إرجاع محتوى الملف الكامل كاستجابة HTTP
            return response($fastApiResponse->body(), 200, $headers);

        // التعامل مع أي استثناءات
        } catch (\Exception $e) {
            // تسجيل تفاصيل الاستثناء
            Log::error('Playlist audio download exception', [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            // إرجاع استجابة JSON بخطأ عام 500
            return response()->json([
                'error' => 'Download failed',
                'message' => $e->getMessage()
            ], 500);
        }
    }

}