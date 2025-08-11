# Deployment Instructions

## SOLUTION FOR CURRENT ERROR

The error you're seeing indicates the platform is trying to run `main.py --dashboard` which uses subprocess calls that don't work in cloud environments.

### 🎯 **RECOMMENDED SOLUTION:**

**Use `streamlit_app.py` as the entry point instead of `main.py`**

1. **Change your deployment entry point to:** `streamlit_app.py`
2. **Or use the Procfile:** The `Procfile` is configured to run the correct command
3. **Or specify this command:** `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --server.fileWatcherType=none`

### 📁 **Entry Point Priority:**

1. **`streamlit_app.py`** ✅ - **USE THIS** - Direct Streamlit app with fallback handling
2. **`test_app.py`** - Minimal test version for troubleshooting  
3. **`app_production.py`** - Production version with enhanced configuration
4. ~~`main.py --dashboard`~~ ❌ - **AVOID** - Uses subprocess (causes current error)

## Cloud Deployment Entry Points

For cloud deployment, use one of these entry points depending on your platform:

### Option 1: Test Version (Recommended for troubleshooting)
```
test_app.py
```
- Uses: Minimal dashboard with built-in sample data
- Best for: Testing deployment and diagnosing issues

### Option 2: Standard Streamlit Entry Point
```
streamlit_app.py
```
- Uses: Standard Streamlit deployment with enhanced debugging
- Best for: Streamlit Cloud, Heroku with Streamlit buildpack

### Option 3: Production Entry Point  
```
app_production.py
```
- Uses: Enhanced file watcher disabling
- Best for: Platforms with strict file system limitations

### Option 4: Direct Main Module
```
main.py --dashboard
```
- Uses: CLI wrapper around dashboard
- Best for: Custom deployment scripts

## Configuration Files

- `.streamlit/config.toml` - Streamlit configuration with file watcher disabled
- `.env` - Environment variables for deployment
- `runtime.txt` - Python version specification
- `requirements.txt` - Python dependencies

## Environment Variables Set

The deployment files automatically set these environment variables:
- `STREAMLIT_SERVER_FILE_WATCHER_TYPE=none`
- `STREAMLIT_SERVER_RUN_ON_SAVE=false`
- `STREAMLIT_GLOBAL_DEVELOPMENT_MODE=false`
- `STREAMLIT_SERVER_HEADLESS=true`

## Troubleshooting

If you still get inotify errors:
1. Use `app_production.py` as entry point
2. Ensure `.streamlit/config.toml` has `fileWatcherType = "none"`
3. Check that environment variables are properly set
4. Contact platform support about inotify limits
