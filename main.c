/*  WiFi softAP Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "freertos/event_groups.h"
#include "esp_http_server.h"
#include "C:\Users\student\.platformio\packages\framework-espidf\components\log\include\esp_log.h"

#include "lwip/err.h"
#include "lwip/sys.h"

#include "soft-ap.h"
#include "http-server.h"

#include "../mdns/include/mdns.h"
static const char *TAG = "wifi softAP";
void app_main(void)
{
    //Initialize NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
      ESP_ERROR_CHECK(nvs_flash_erase());
      ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
    
    ESP_LOGI(TAG, "ESP_WIFI_MODE_AP");
    wifi_init_softap();

    static httpd_handle_t server =NULL;
    server=start_webserver();
     
    wifi_ap_record_t ap_record[10];
    uint16_t nr=10;
    esp_netif_init();
    esp_event_loop_create_default();
    esp_netif_t *wifi_netif = esp_netif_create_default_wifi_sta();
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_wifi_init(&cfg);
    esp_wifi_set_mode(WIFI_MODE_STA);
    esp_wifi_start();
    esp_wifi_scan_start(NULL, true);
    esp_wifi_scan_get_ap_records(&nr, ap_record);
    esp_wifi_stop();
    esp_wifi_deinit();
    esp_wifi_clear_default_wifi_driver_and_handlers(wifi_netif);
    esp_netif_destroy(wifi_netif);
    
    for(int i=0; i<nr; i++){
      ESP_LOGI(TAG, "SSID \t\t%s", ap_record[i].ssid);
    }
    // TODO: 3. Pornire mod STA + scanare SSID-uri disponibile


    // TODO: 4. Initializare mDNS (daca mai ramane timp)    

    // TODO: 1. Pornire softAP

    // TODO: 2. Pornire server web (si config specifice in http-server.c) 
}