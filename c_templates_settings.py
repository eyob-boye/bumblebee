#---board_hal.h-----------------------------------------------------------
FILE_BOARD_HAL_H_SETTINGS = {"fast_usec_timer_cnt_enable" : "TIM6->CR1|=(TIM_CR1_CEN)",
                             "fast_usec_timer_cnt_register_name" : "TIM6->CNT", 
                             "fast_usec_timer_ticks_per_usec" : 1,
                             "fast_usec_timer_t": "uint16_t",     #uint32_t, uint16_t
                             "fast_usec_timer_max_allowed_delay": 65536,

                             "fast_msec_timer_cnt_enable" : "TIM7->CR1|=(TIM_CR1_CEN)",
                             "fast_msec_timer_cnt_register_name" : "TIM7->CNT", 
                             "fast_msec_timer_ticks_per_msec" : 50,
                             "fast_msec_timer_t": "uint16_t",     #uint32_t, uint16_t
                             "fast_msec_timer_max_allowed_delay": 1310
                             }

#---sys_time.c-----------------------------------------------------------
FILE_SYS_TIME_C_SETTINGS = { "systick_interrupt_hz":      10000,     #10kHz
                             "systick_interrupt_comment": "100usec=0.1msec -> 10kHz",
                             "systime_nanosec_per_tick" : 100000}    #10nsec per tick is 10kHz timers

