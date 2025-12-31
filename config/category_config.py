#!/usr/bin/env python3
import configparser

category_config_parser = configparser.ConfigParser()

url = "https://www.trendyol.com"
base_api_url = (
    "https://www.trendyol.com/discovery-web-searchgw-service/v2/api/infinite-scroll"
)


# -----------------------------------------------------------------------------------------
# Requested Categories
# -----------------------------------------------------------------------------------------


category_config_parser["MAKYAJ"] = {
    "NAME": "Makyaj",
    "URL": f"{url}/makyaj-x-c100?sst=BEST_SELLER",
    "BASE_API_URL": f"{base_api_url}/makyaj-x-c100",
}

category_config_parser["CILT_BAKIMI"] = {
    "NAME": "Cilt Bakımı",
    "URL": f"{url}/cilt-bakimi-x-c85?sst=MOST_RATED",
    "BASE_API_URL": f"{base_api_url}/cilt-bakimi-x-c85",
}

category_config_parser["SAC_BAKIMI"] = {
    "NAME": "Saç Bakımı",
    "URL": f"{url}/sac-bakimi-x-c87?sst=BEST_SELLER",
    "BASE_API_URL": f"{base_api_url}/sac-bakimi-x-c87",
}

category_config_parser["PARFUM_DEODORANT"] = {
    "NAME": "Parfüm ve Deodorant",
    "URL": f"{url}/parfum-ve-deodorant-x-c103717?sst=BEST_SELLER",
    "BASE_API_URL": f"{base_api_url}/parfum-ve-deodorant-x-c103717",
}

category_config_parser["DIGER_KISISEL_BAKIM"] = {
    "NAME": "Diğer Kişisel Bakım",
    "URL": f"{url}/diger-kisisel-bakim-urunleri-x-c104068?sst=BEST_SELLER",
    "BASE_API_URL": f"{base_api_url}/diger-kisisel-bakim-urunleri-x-c104068",
}

category_config_parser["SAC_SEKILLENDIRICI"] = {
    "NAME": "Saç Şekillendirici",
    "URL": f"{url}/sac-sekillendirici-urunler-x-c101390?sst=BEST_SELLER",
    "BASE_API_URL": f"{base_api_url}/sac-sekillendirici-urunler-x-c101390",
}

category_config_parser["MAKYAJ_AKSESUARLARI"] = {
    "NAME": "Makyaj Aksesuarları",
    "URL": f"{url}/makyaj-aksesuarlari-x-c1252?sst=BEST_SELLER",
    "BASE_API_URL": f"{base_api_url}/makyaj-aksesuarlari-x-c1252",
}

category_config_parser["TIRAS_EPILASYON"] = {
    "NAME": "Tıraş, Ağda, Epilasyon",
    "URL": f"{url}/tiras-agda-epilasyon-x-c105782?sst=BEST_SELLER",
    "BASE_API_URL": f"{base_api_url}/tiras-agda-epilasyon-x-c105782",
}

category_config_parser["KOZMETIK"] = {
    "NAME": "Kozmetik (Genel)",
    "URL": f"{url}/kozmetik-x-c89?sst=BEST_SELLER",
    "BASE_API_URL": f"{base_api_url}/kozmetik-x-c89",
}
