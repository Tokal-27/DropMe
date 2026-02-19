import time
import random
from prometheus_client import start_http_server, Gauge, Counter

# مقاييس التشغيل (Operations Metrics)
UPTIME = Gauge('machine_status', '1=Online, 0=Offline')
TEMP = Gauge('machine_temperature', 'Temperature in Celsius')
ERRORS = Counter('machine_errors_total', 'Total count of errors')

# مقاييس الاستدامة (ESG Metrics)
ENERGY = Counter('esg_energy_kwh_total', 'Total Energy Consumption')
CARBON = Gauge('esg_carbon_footprint', 'Carbon emissions (kg CO2)')

if __name__ == '__main__':
    start_http_server(8000)
    print("Machine Sim is running on port 8000...")

    while True:
        # محاكاة الحالة (90% شغالة)
        is_online = 1 if random.random() > 0.1 else 0
        UPTIME.set(is_online)

        if is_online:
            t = random.uniform(65, 98)
            TEMP.set(t)
            e = random.uniform(0.2, 0.8)
            ENERGY.inc(e)
            # حساب الكربون (ESG logic: استهلاك الطاقة * معامل الانبعاثات)
            CARBON.set(e * 0.4) 
            if t > 95: ERRORS.inc()
        else:
            TEMP.set(25)
            CARBON.set(0)
        
        time.sleep(5)