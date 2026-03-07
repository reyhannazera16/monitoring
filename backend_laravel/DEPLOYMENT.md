# Laravel Deployment Guide

This guide will help you host your Air Quality Monitoring API.

## Recommended Hosting Platforms

### 1. Railway.app (Recommended)
- **Ease of use**: High
- **Steps**:
    1. Connect your GitHub repository.
    2. Railway will detect Laravel automatically.
    3. Add a **MySQL Database** from the Railway dashboard.
    4. Copy the MySQL connection details to your Railway **Variables**.
    5. Run `php artisan migrate` once deployed.

### 2. Render.com
- **Ease of use**: High
- **Steps**:
    1. Create a **Web Service** from GitHub.
    2. Add a **MySQL** instance.
    3. Set environment variables (DB_HOST, DB_PASSWORD, etc.).

### 3. Shared Hosting (cPanel)
- **Steps**:
    1. Zip your project files (excluding `vendor` and `node_modules`).
    2. Upload to `public_html` or a subdirectory.
    3. Create a MySQL database and user in cPanel.
    4. Update `.env` with the cPanel database details.
    5. Point your domain to the `public/` folder.

## Production Configuration

### Environment Variables
Ensure these are set in your hosting dashboard:
- `APP_ENV=production`
- `APP_DEBUG=false`
- `APP_KEY=base64:YOUR_GENERATED_KEY`
- `DB_CONNECTION=mysql`
- `DB_HOST=your_host`
- `DB_DATABASE=your_db`
- `DB_USERNAME=your_user`
- `DB_PASSWORD=your_password`

## Arduino Update
Once hosted at `https://your-api.com`, update your Arduino code:
```cpp
const char* serverUrl = "https://your-api.com/api/sensor-readings";
```
