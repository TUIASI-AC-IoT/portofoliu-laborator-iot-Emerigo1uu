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

#include "../soft-ap.h"
#include "../http-server.h"

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
   
    
    // TODO: 3. Pornire mod STA + scanare SSID-uri disponibile

    // TODO: 4. Initializare mDNS (daca mai ramane timp)    

    // TODO: 1. Pornire softAP

    // TODO: 2. Pornire server web (si config specifice in http-server.c) 
}