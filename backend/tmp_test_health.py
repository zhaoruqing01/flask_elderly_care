from app.services.health_service import HealthService
hs = HealthService()
print('distribution:', hs.get_health_distribution())
print('by_age:', hs.get_health_distribution_by_age())
print('trend_sample_dates:', hs.get_health_trend().get('dates')[:3])
