// File: main/includes/pngdemo.h
//#include "lvgl/lvgl.h"
//#include "lodepng.h"
#include "lvgl/lvgl.h"
#include "lodepng.h"

#pragma once

// Max number of messages to store
#define MSG_QUEUE_DEPTH 128
// Max number of images to store in the buffer 
#define PNG_QUEUE_DEPTH 1
// Max size of the incoming message containing an URL
#define MAX_URL_BUFF_SIZE 1024
// Theoretical maximum size of an incoming PNG. 
// It includes the PNG file data, signature, chunks and CRC checksum.
#define MAX_PNG_BUFF_SIZE (320*240*4)+8+4+4+4

// Function prototypes

void convert_color_depth(uint8_t * img, uint32_t px_cnt);

void processJSON(char * json);

void iot_subscribe_callback_handler_pngdemo(char * payload, int len);

void check_messages(void * param);