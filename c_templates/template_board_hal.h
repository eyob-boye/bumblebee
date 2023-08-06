/******************************************************************************
Overview: This file abstracts the different characteristics of the board

*******************************************************************************/
#include "cmsis_device_include.h" 
#include "mcu_init_gpio.h"
#include <stdint.h>

#define BHAL_FAST_USEC_TIMER_ENABLE()  {fast_usec_timer_cnt_enable}
#define BHAL_FAST_USEC_TIMER_CNT()  (({fast_usec_timer_t})({fast_usec_timer_cnt_register_name}))
#define BHAL_FAST_USEC_TIMER_TICKS_PER_USEC  {fast_usec_timer_ticks_per_usec}

#define BHAL_FAST_MSEC_TIMER_ENABLE()  {fast_msec_timer_cnt_enable}
#define BHAL_FAST_MSEC_TIMER_CNT()  (({fast_msec_timer_t})({fast_msec_timer_cnt_register_name}))
#define BHAL_FAST_MSEC_TIMER_TICKS_PER_MSEC  {fast_msec_timer_ticks_per_msec}

//Max allowed delay is {fast_usec_timer_max_allowed_delay} usec
#define BHAL_DELAY_USEC(usec) \
do {{ \
    BHAL_FAST_USEC_TIMER_ENABLE(); \
    do {{ \
        {fast_usec_timer_t} delayTime = BHAL_FAST_USEC_TIMER_CNT(); \
        while(({fast_usec_timer_t})(({fast_usec_timer_t})(BHAL_FAST_USEC_TIMER_CNT() - delayTime)) < ({fast_usec_timer_t})(BHAL_FAST_USEC_TIMER_TICKS_PER_USEC*(usec)) )  {{}} \
    }} while(0) \
}} while(0)


//Max allowed delay is {fast_msec_timer_max_allowed_delay} msec
#define BHAL_DELAY_MSEC(msec) \
do {{ \
    BHAL_FAST_MSEC_TIMER_ENABLE(); \
    do {{ \
        {fast_msec_timer_t} delayTime = BHAL_FAST_MSEC_TIMER_CNT(); \
        while(({fast_msec_timer_t})(({fast_msec_timer_t})(BHAL_FAST_MSEC_TIMER_CNT() - delayTime)) < ({fast_msec_timer_t})(BHAL_FAST_MSEC_TIMER_TICKS_PER_MSEC*(msec)) )  {{}} \
    }} while(0) \
}} while(0)


#define BHAL_MCU_UID_UINT8_PTR()   ((uint8_t*) (UID_BASE))

//Sample macros for definining custom board IO abstractions
//#define BHAL_NAME_PIN_HI()  PORT_NAME->BSRR = PIN_NAME
//#define BHAL_NAME_PIN_LO()  PORT_NAME->BSRR = (((uint32_t)PIN_NAME) << 16)
//#define BHAL_NAME_PIN_TGL() PORT_NAME->ODR ^= PIN_NAME
//#define BHAL_NAME_PIN_IS_HI()  ((PORT_NAME->IDR & PIN_NAME) != 0)
//#define BHAL_NAME_PIN_IS_LO()  ((PORT_NAME->IDR & PIN_NAME) == 0)


//#define BHAL_LED_BLUE_TGL()  LD6_GPIO_Port->ODR ^= LD6_Pin