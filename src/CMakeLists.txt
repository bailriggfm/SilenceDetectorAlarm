cmake_minimum_required(VERSION 3.5)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

set(TARGET_NAME BFM_GPIO_Interface)

add_executable(${TARGET_NAME}
        ${TARGET_NAME}.c
        )

pico_set_program_name(${TARGET_NAME} "${TARGET_NAME}")
pico_set_program_version(${TARGET_NAME} "0.1")

target_link_libraries(${TARGET_NAME} PRIVATE
        pico_stdlib
        hardware_spi
        hardware_dma
        ETHERNET_FILES
        IOLIBRARY_FILES
        DHCP_FILES
        DNS_FILES
        TIMER_FILES
        mbedcrypto
        mbedx509
        mbedtls
        )

pico_enable_stdio_usb(${TARGET_NAME} 1)
pico_enable_stdio_uart(${TARGET_NAME} 0)

pico_add_extra_outputs(${TARGET_NAME})
