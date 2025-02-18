#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#define GPIO_OUTPUT_IO 4
#define GPIO_OUTPUT_PIN_SEL (1ULL<<GPIO_OUTPUT_IO)
void app_main() {
//zero-initialize the config structure.
    gpio_config_t io_conf = {};
//disable interrupt
    io_conf.intr_type = GPIO_INTR_DISABLE;
//set as output mode
    io_conf.mode = GPIO_MODE_OUTPUT;
//bit mask of the pins that you want to set
    io_conf.pin_bit_mask = GPIO_OUTPUT_PIN_SEL;
//disable pull-down mode
    io_conf.pull_down_en = 0;
//disable pull-up mode
    io_conf.pull_up_en = 0;
//configure GPIO with the given settings
    gpio_config(&io_conf);
    int cnt = 0;
    while(1) {
        printf("cnt: %d\n", cnt++);
        if(cnt % 4==0){ 
            gpio_set_level(GPIO_OUTPUT_IO, 1);
            vTaskDelay(750 / portTICK_PERIOD_MS);
            }
        if(cnt % 4==1){ 
            gpio_set_level(GPIO_OUTPUT_IO, 0);
            vTaskDelay(1000 / portTICK_PERIOD_MS);
        }
        if(cnt % 4==2){
            gpio_set_level(GPIO_OUTPUT_IO, 1);
            vTaskDelay(500 / portTICK_PERIOD_MS);
            }
         if(cnt % 4 ==3){
            gpio_set_level(GPIO_OUTPUT_IO, 0);
            vTaskDelay(250 / portTICK_PERIOD_MS);
        }
    }
}

/*
1. Ce rol are gpio_config? 
 gpio_config este api folosit pentru configurarea dispozitivelor IO. 
*/


/*2.In codul exemplu, pinul GPIO4 este configurat ca iesire. Care sunt celelalte moduri in care poate fi configurat un pin GPIO?
pull-up/pull-down, input/output enable, pin mapping
*/
/*IDF peripheral drivers always take care of the necessary IO configurations that need to be applied onto the pins, so 
that they can be used as the peripheral signal inputs or outputs. This means the users usually only need to be responsible 
for configuring the IOs as simple inputs or outputs. gpio_config() is an all-in-one API that can be used to configure the I/O 
mode, internal pull-up/pull-down resistors, etc. for pins.*/