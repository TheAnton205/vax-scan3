set(COMPONENT_SRCS "main.c" "blink.c" "ui.c" "wifi.c" "pngdemo.c")
set(COMPONENT_ADD_INCLUDEDIRS "./includes")
set(COMPONENT_REQUIRES "nvs_flash" "esp-aws-iot" "esp-cryptoauthlib" "core2forAWS" "lv_lib_png" "esp_http_client" "json")
register_component()

target_add_binary_data(${COMPONENT_TARGET} "certs/aws-root-ca.pem" TEXT)
