import os
#from _examples.bumblebee_spec import user_settings

THIS_SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#------------------------------------------------------------------------------
# Default settings here but they need to come from user
user_settings_FILE_BOARD_HAL_H_SETTINGS = {"fast_usec_timer_cnt_enable" : "TIM6->CR1|=(TIM_CR1_CEN)",
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

user_settings_FILE_SYS_TIME_C_SETTINGS = { "systick_interrupt_hz":      10000,     #10kHz
                                "systick_interrupt_comment": "100usec=0.1msec -> 10kHz",
                                "systime_nanosec_per_tick" : 100000}    #10nsec per tick is 10kHz timers


def set_user_settings(user_settings):
    user_settings_FILE_SYS_TIME_C_SETTINGS = user_settings.FILE_SYS_TIME_C_SETTINGS
    user_settings_FILE_BOARD_HAL_H_SETTINGS = user_settings.FILE_BOARD_HAL_H_SETTINGS

#------------------------------------------------------------------------------
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
C_FILE_TEMPLATE = """
#include "{h_file_name}"
{body}
"""

#------------------------------------------------------------------------------
C_FILE_NO_INCLUDE_TEMPLATE = \
"""{body}
"""


#---mcu_init.c-----------------------------------------------------------------
FILE_MCU_INIT_ADDITIONS = """

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

FILE_MCU_INIT_ADDITIONS = FILE_MCU_INIT_ADDITIONS.format(**(user_settings_FILE_SYS_TIME_C_SETTINGS))

#---stm32[fg]xxx_hal_conf.c-------------------------------------------------------
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
FILE_SCHEDULER_H_ADDITIONS = get_c_body('template_scheduler.h')

#---scheduler.c-----------------------------------------------------------
FILE_SCHEDULER_C_ADDITIONS = get_c_body('template_scheduler.c')

#---main.c------------------------------------------------------------------
FILE_MAIN_C_ADDITIONS = get_c_body('template_main.c')

#---stm32[fg]xxx_it.c-     ------------------------------------------------------
FILE_IT_C_ADDITIONS = get_c_body('template_it.c')

#---board_state.h-------------------------------------------------------------
FILE_BOARD_STATE_H_ADDITIONS = get_c_body('template_board_state.h')

#---board_state.c-----------------------------------------------------------
FILE_BOARD_STATE_C_ADDITIONS = get_c_body('template_board_state.c')

#---board_app.h-----------------------------------------------------------
FILE_BOARD_APP_H_ADDITIONS = get_c_body('template_board_app.h')

#---board_app.c-----------------------------------------------------------
FILE_BOARD_APP_C_ADDITIONS = get_c_body('template_board_app.c')

#---board_hal.h-----------------------------------------------------------
FILE_BOARD_HAL_H_ADDITIONS = get_c_body("template_board_hal.h", **user_settings_FILE_BOARD_HAL_H_SETTINGS)

#---sys_time.h-----------------------------------------------------------
FILE_SYS_TIME_H_ADDITIONS = get_c_body('template_sys_time.h')

#---sys_time.c-----------------------------------------------------------
FILE_SYS_TIME_C_ADDITIONS = get_c_body('template_sys_time.c', **user_settings_FILE_SYS_TIME_C_SETTINGS)

