"""Print the loaded configuration. Run with: python -m scripts.check_config"""
from app.core.config import settings


def main():
    print("Testing Configuration...\n")

    print(f"App Name: {settings.APP_NAME}")
    print(f"App Version: {settings.APP_VERSION}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"Environment: {settings.ENVIRONMENT}")

    # Never print credentials; show only the host part of the database URL
    db_url = settings.DATABASE_URL
    print(f"\nDatabase: {db_url.split('@')[-1] if '@' in db_url else 'configured'}")

    print(f"\nAI Provider: {settings.AI_PROVIDER}")
    print(f"AI Model: {settings.ai_model}")
    print(f"API key configured: {bool(settings.ai_api_key)}")
    print(f"Max Tokens: {settings.MAX_TOKENS}")
    print(f"Temperature: {settings.TEMPERATURE}")

    print(f"\nServer: {settings.HOST}:{settings.PORT}")
    print(f"Rate limit: {settings.RATE_LIMIT_PER_MINUTE}/minute")
    print(f"CORS Origins: {settings.CORS_ORIGINS}")

    print("\nConfiguration loaded successfully!")


if __name__ == "__main__":
    main()
