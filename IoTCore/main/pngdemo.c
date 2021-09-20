// File: main/pngdemo.c
#include "lvgl/lvgl.h"
#include "lodepng.h"
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "esp_http_client.h"
#include "cJSON.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "pngdemo.h"

static const char *TAG = "PNGDEMO";

// Queue to store the pointers to the PNG buffers
extern QueueHandle_t xQueuePngPtrs;    
// Handler to the semaphore that makes the guiTask yield
extern SemaphoreHandle_t xGuiSemaphore; 

extern QueueHandle_t xQueueMsgPtrs;

// File: main/pngdemo.c

void convert_color_depth(uint8_t * img, uint32_t px_cnt)
{
    lv_color32_t * img_argb = (lv_color32_t*)img;
    lv_color_t c;
    uint32_t i;

    for(i = 0; i < px_cnt; i++) {
        c = LV_COLOR_MAKE(
				img_argb[i].ch.blue, 
				img_argb[i].ch.green, 
				img_argb[i].ch.red);
        img[i*2 + 1] = c.full >> 8;
        img[i*2 + 0] = c.full & 0xFF;
    }

}

void iot_subscribe_callback_handler_pngdemo(char * payload, int len)
{
    // Create buffer to store the incoming message
    char * myItem = heap_caps_malloc(len, MALLOC_CAP_SPIRAM);

    // Copy the incoming data into the buffer
    strncpy(myItem,payload,len);

    // Send the pointer to the incoming message to the xQueue.
    xQueueSend(xQueueMsgPtrs,&myItem,portMAX_DELAY);
}

void processJSON(char * json) 
 {
    cJSON * root   = cJSON_Parse(json);

    // Find out how big is the string is
    int len = strlen(cJSON_GetObjectItem(root,"img_url")->valuestring);
    
    // Allocate memory, align it to use the SPIRAM
    char * url_buffer = heap_caps_malloc(MAX_URL_BUFF_SIZE, MALLOC_CAP_SPIRAM);

    // Copy the contents of the parsed string to the allocated memory
    memcpy(url_buffer, cJSON_GetObjectItem(root,"img_url")->valuestring, len+1);

    // Make sure the last byte is zero (NULL character)
    url_buffer[len+1] = 0;

    // Don't need the parsed object anymore, free memory
    cJSON_Delete(root);

        // Allocate a large buffer, align it to use the SPIRAM
    unsigned char * buffer = heap_caps_malloc(MAX_PNG_BUFF_SIZE, MALLOC_CAP_SPIRAM);
    if (buffer == NULL) {
        ESP_LOGE(TAG, "Cannot malloc http receive buffer");
        return;
    }
    
    esp_err_t err;
    int content_length;
    int read_len;
    
    // Intialize the HTTP client
    esp_http_client_config_t config = {.url = url_buffer};
    esp_http_client_handle_t http_client = esp_http_client_init(&config);

    // Establish a connection with the HTTPs server and send headers
    if ((err = esp_http_client_open(http_client, 0)) != ESP_OK) {
        ESP_LOGE(TAG, "Failed to open HTTP connection: %s", esp_err_to_name(err));
        free(buffer);
        return;
    }

    // Immediately start retrieving headers from the stream
    content_length =  esp_http_client_fetch_headers(http_client);

    // Retrieve data from the stream and store it in the SPI ram
    read_len = esp_http_client_read(http_client, (char *) buffer, content_length);

    // Validate that we actually read something
    if (read_len <= 0) {
           ESP_LOGE(TAG, "Error read data");
    }

    ESP_LOGI(TAG, "HTTP Stream reader Status = %d, content_length = %d",
      esp_http_client_get_status_code(http_client),
      esp_http_client_get_content_length(http_client));
    
    // Tear down the http session
    esp_http_client_cleanup(http_client);

     // Pointer that will point to the decoded PNG data
    unsigned char * png_decoded = 0;

    uint32_t error;
    uint32_t png_width;
    uint32_t png_height;

    // Use LodePNG to convert the PNG image to 32-bit RGBA and store it 
    // in the new buffer.
    error = lodepng_decode32(&png_decoded, 
							&png_width, 
							&png_height, 
							buffer, 
							read_len);
    if(error) {
       ESP_LOGE(TAG, "error %u: %s\n", error, lodepng_error_text(error));
       return;
    }
   
   // Clean up
   free(url_buffer);
   free(buffer);

   // Convert the 32-bit RGBA image to 16-bit and swap blue and red data.
   convert_color_depth(png_decoded,  png_width * png_height);

   xQueueSend(xQueuePngPtrs,&png_decoded,portMAX_DELAY);
}

 void check_messages(void *param)
{
    char * pngPtr;
    char * msgPtr;

    while(1)
    {
        // Yield for 500ms to let other tasks do work
        vTaskDelay(500 / portTICK_RATE_MS); 

        if(xQueuePngPtrs != 0)
        {
            if (xQueueReceive(xQueuePngPtrs,&pngPtr,(TickType_t)10))
            {
                ESP_LOGI(TAG, "Got a PNG pointer, free heap: %d\n",
                              
                esp_get_free_heap_size());

                // Make sure the gui Task will yield
                xSemaphoreTake(xGuiSemaphore, portMAX_DELAY);

                // Object that will contain the LVGL image 
                // in RAW BGR565 format
                lv_obj_t * image_background;

                // Clean the screen
                lv_obj_clean(lv_scr_act());

                // Create a new object using the active screen and no parent
                image_background = lv_img_create(lv_scr_act(), NULL);

                lv_img_dsc_t img = {
                  .header.always_zero = 0,
                  .header.w = 320,
                  .header.h = 240,
                  .data_size = 320 * 240 * 2,
                  .header.cf = LV_IMG_CF_TRUE_COLOR,
                  .data = (unsigned char *)pngPtr
                };

                // Force LVGL to invalidate the cache
                lv_img_cache_invalidate_src(&img);

                // Tell LVGL to load the data that the pointer points to
                lv_img_set_src(image_background, &img);

                // Free the PNG data
                free(pngPtr);

                // Let the guiTask continue so that the screen gets refreshed
                xSemaphoreGive(xGuiSemaphore);
            }
        }
        if(xQueueMsgPtrs != 0)
        {
            if (xQueueReceive(xQueueMsgPtrs,&msgPtr,(TickType_t)10))
            { 
                // Send the pointer that  points to the string to process it
                processJSON(msgPtr);

                // Free the URL data
                free(msgPtr);
            }
        }
    }
}