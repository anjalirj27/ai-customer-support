from app.core.config import settings

print("🔧 Testing Configuration...\n")

print(f"App Name: {settings.APP_NAME}")
print(f"App Version: {settings.APP_VERSION}")
print(f"Debug Mode: {settings.DEBUG}")
print(f"\nDatabase URL: {settings.DATABASE_URL}")
print(f"\nOpenAI Model: {settings.OPENAI_MODEL}")
print(f"Max Tokens: {settings.OPENAI_MAX_TOKENS}")
print(f"Temperature: {settings.OPENAI_TEMPERATURE}")
print(f"\nServer: {settings.HOST}:{settings.PORT}")
print(f"\nCORS Origins: {settings.CORS_ORIGINS}")

print("\n✅ Configuration loaded successfully!")