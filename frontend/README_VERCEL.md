# Deploy Ke Vercel 🚀

Website ini siap untuk diunggah ke Vercel sebagai situs statis yang terhubung ke backend Laravel di `https://dimas.rulsit.com`.

## Cara Deploy (Metode Termudah):

1.  **Gunakan Vercel CLI**:
    - Buka terminal di folder `frontend`.
    - Jalankan perintah: `vercel`
    - Ikuti instruksi (Pilih "Yes" untuk semua default).

2.  **Gunakan GitHub/GitLab (Rekomendasi)**:
    - Push seluruh folder project ini ke repositori Git Anda.
    - Masuk ke dashboard Vercel, pilih **"Add New Project"**.
    - Sambungkan repositori Git Anda.
    - **PENTING**: Pada bagian **"Root Directory"**, klik "Edit" dan pilih folder `frontend`.
    - Klik **Deploy**.

## Konfigurasi yang Digunakan:
- **API Backend**: `https://dimas.rulsit.com/api` (Sudah teratur secara otomatis di `js/api_client.js`).
- **Timezone**: Jakarta (WIB).
- **Realtime**: AJAX update setiap 10 detik.

Selamat mencoba! Website Anda akan memiliki domain `.vercel.app` secara gratis.
