# Teslas.ai - PowerShell Build Script
# Usage: .\Makefile.ps1 <command>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("install", "run", "api", "ui", "test", "ingest", "reset", "clean")]
    [string]$Command
)

$ErrorActionPreference = "Stop"

switch ($Command) {
    "install" {
        Write-Host "📦 Installing dependencies with uv..." -ForegroundColor Cyan
        uv pip install -e .
    }
    
    "run" {
        Write-Host "🚀 Starting Teslas.ai (API + UI with uv)..." -ForegroundColor Green
        $apiJob = Start-Job -ScriptBlock {
            uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
        }
        Start-Sleep -Seconds 3
        $uiJob = Start-Job -ScriptBlock {
            uv run streamlit run app/ui/streamlit_app.py --theme.base dark
        }
        Write-Host "🔵 API: http://localhost:8000" -ForegroundColor Blue
        Write-Host "🟢 UI:  http://localhost:8501" -ForegroundColor Green
        Write-Host "Press Ctrl+C to stop jobs or use 'Get-Job'/'Stop-Job'" -ForegroundColor Yellow
        Wait-Job -Any $apiJob, $uiJob
    }
    
    "api" {
        Write-Host "🔵 Starting API server..." -ForegroundColor Blue
        uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
    }
    
    "ui" {
        Write-Host "🟢 Starting UI..." -ForegroundColor Green
        uv run streamlit run app/ui/streamlit_app.py --theme.base dark
    }
    
    "test" {
        Write-Host "🧪 Running tests..." -ForegroundColor Yellow
        uv run pytest tests/ -v
    }
    
    "ingest" {
        Write-Host "📥 Ingesting documents..." -ForegroundColor Magenta
        $path = Read-Host "Enter path to documents"
        uv run python scripts/ingest_docs.py $path
    }
    
    "reset" {
        Write-Host "🗑️ Resetting knowledge base..." -ForegroundColor Red
        uv run python scripts/reset_db.py
    }
    
    "clean" {
        Write-Host "🧹 Cleaning project..." -ForegroundColor DarkGray
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue .venv
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue __pycache__
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue .pytest_cache
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue chroma
        Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
        Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
        Write-Host "✨ Project cleaned!" -ForegroundColor Green
    }
}
