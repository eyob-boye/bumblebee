import os
#from _examples.bumblebee_spec import user_settings

THIS_SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#------------------------------------------------------------------------------
# Default settings here but they need to come from user
user_settings_FILE_BOARD_HAL_H_SETTINGS__default = {
                                "fast_usec_timer_cnt_enable" : "TIM6->CR1|=(TIM_CR1_CEN)",
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

user_settings_FILE_SYS_TIME_C_SETTINGS__default = {
                                "systick_interrupt_hz":      10000,     #10kHz
                                "systick_interrupt_comment": "100usec=0.1msec -> 10kHz",
                                "systime_nanosec_per_tick" : 100000}    #10nsec per tick is 10kHz timers

#------------------------------------------------------------------------------
# All global variables are wrapped in this function. It will be called once when
# the module loaded and it uses the default settings. But once the importer
# module has read the actual user settings it can call it again to refresh the
# global variables.
#------------------------------------------------------------------------------
def set_user_settings(user_settings):
    global user_settings_FILE_BOARD_HAL_H_SETTINGS
    global user_settings_FILE_SYS_TIME_C_SETTINGS
    if user_settings != None:
        user_settings_FILE_BOARD_HAL_H_SETTINGS = user_settings.FILE_BOARD_HAL_H_SETTINGS
        user_settings_FILE_SYS_TIME_C_SETTINGS = user_settings.FILE_SYS_TIME_C_SETTINGS
    else:
        user_settings_FILE_BOARD_HAL_H_SETTINGS = user_settings_FILE_BOARD_HAL_H_SETTINGS__default
        user_settings_FILE_SYS_TIME_C_SETTINGS = user_settings_FILE_SYS_TIME_C_SETTINGS__default

    #------------------------------------------------------------------------------
    global H_FILE_TEMPLATE
    H_FILE_TEMPLATE = """
#ifndef {file_name_uppercase}
#define {file_name_uppercase}

#ifdef __cplusplus 
extern "C" 
{{ 
#endif 

{body}

#ifdef __cplusplus
}}
#endif

#endif
"""

    #------------------------------------------------------------------------------
    global C_FILE_TEMPLATE
    C_FILE_TEMPLATE = """
#include "{h_file_name}"
{body}
"""

    #------------------------------------------------------------------------------
    global C_FILE_NO_INCLUDE_TEMPLATE
    C_FILE_NO_INCLUDE_TEMPLATE = \
    """{body}
"""


    #---mcu_init.c-----------------------------------------------------------------
    global FILE_MCU_INIT_ADDITIONS
    FILE_MCU_INIT_ADDITIONS_FMT = """

void HAL_TIM_MspPostInit(TIM_HandleTypeDef *htim);


//Overrride the default weak function for hal library
HAL_StatusTypeDef HAL_InitTick(uint32_t TickPriority)
{{
  return HAL_OK;
}}

void McuInit_HAL()
{{
  HAL_Init();
}}

void McuInit_systick(void)
{{
  SystemCoreClockUpdate();
  //{systick_interrupt_comment}
  if(HAL_SYSTICK_Config(SystemCoreClock / {systick_interrupt_hz}U) > 0U)
  {{
    while(1) {{}};
  }}
  HAL_SYSTICK_CLKSourceConfig(SYSTICK_CLKSOURCE_HCLK);
}}
"""
    def get_mcu_init_additions():
        return FILE_MCU_INIT_ADDITIONS_FMT.format(**(user_settings_FILE_SYS_TIME_C_SETTINGS))

    FILE_MCU_INIT_ADDITIONS = get_mcu_init_additions()

    #---stm32[fg]xxx_hal_conf.c-------------------------------------------------------
    global FILE_HAL_CONF_ADDITIONS
    FILE_HAL_CONF_ADDITIONS = """
#include "device_hal.h"  //Cannot include "device_hal_conf.h" directly


void _Error_Handler(char *file, int line)
{
  //User can add own implementation to report the HAL error return state
  while(1)
  {
  }
}

#ifdef  USE_FULL_ASSERT
void assert_failed(uint8_t *file, uint32_t line)
{
  //User can add own implementation to report the file name and line number,
  //ex: printf("Wrong parameters value: file %s on line %d", file, line)
}
#endif

"""


    #---board_app.h-----------------------------------------------------------
    def get_c_body(fname, **kwargs):
        fpath = os.path.join(THIS_SCRIPT_PATH + "/c_templates", fname)
        with open(fpath, 'r') as ifile:
            ifile_cont = ifile.readlines()
        ifile_cont = "".join(ifile_cont)
        body = ifile_cont.format(**kwargs)
        return body


    #---scheduler.h-----------------------------------------------------------
    global FILE_SCHEDULER_H_ADDITIONS
    FILE_SCHEDULER_H_ADDITIONS = get_c_body('template_scheduler.h')

    #---scheduler.c-----------------------------------------------------------
    global FILE_SCHEDULER_C_ADDITIONS
    FILE_SCHEDULER_C_ADDITIONS = get_c_body('template_scheduler.c')

    #---main.c------------------------------------------------------------------
    global FILE_MAIN_C_ADDITIONS
    FILE_MAIN_C_ADDITIONS = get_c_body('template_main.c')

    #---stm32[fg]xxx_it.c-     ------------------------------------------------------
    global FILE_IT_C_ADDITIONS
    FILE_IT_C_ADDITIONS = get_c_body('template_it.c')

    #---board_state.h-------------------------------------------------------------
    global FILE_BOARD_STATE_H_ADDITIONS
    FILE_BOARD_STATE_H_ADDITIONS = get_c_body('template_board_state.h')

    #---board_state.c-----------------------------------------------------------
    global FILE_BOARD_STATE_C_ADDITIONS
    FILE_BOARD_STATE_C_ADDITIONS = get_c_body('template_board_state.c')

    #---board_app.h-----------------------------------------------------------
    global FILE_BOARD_APP_H_ADDITIONS
    FILE_BOARD_APP_H_ADDITIONS = get_c_body('template_board_app.h')

    #---board_app.c-----------------------------------------------------------
    global FILE_BOARD_APP_C_ADDITIONS
    FILE_BOARD_APP_C_ADDITIONS = get_c_body('template_board_app.c')

    #---board_hal.h-----------------------------------------------------------
    global FILE_BOARD_HAL_H_ADDITIONS
    def get_c_body_board_hal():
        return get_c_body("template_board_hal.h", **user_settings_FILE_BOARD_HAL_H_SETTINGS)

    FILE_BOARD_HAL_H_ADDITIONS = get_c_body_board_hal()

    #---sys_time.h-----------------------------------------------------------
    global FILE_SYS_TIME_H_ADDITIONS
    FILE_SYS_TIME_H_ADDITIONS = get_c_body('template_sys_time.h')

    #---sys_time.c-----------------------------------------------------------
    global FILE_SYS_TIME_C_ADDITIONS
    def get_c_body_sys_time():
        return get_c_body('template_sys_time.c', **user_settings_FILE_SYS_TIME_C_SETTINGS)

    FILE_SYS_TIME_C_ADDITIONS = get_c_body_sys_time()


set_user_settings(None)
