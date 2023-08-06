#include "board_state.h"
#include "sys_time.h"
#include <stdint.h>
#include <stdbool.h>
#include "board_hal.h"


//#define SCHEDULER_DEBUG_ON
#if defined(SCHEDULER_DEBUG_ON)
#include <stdio.h>
#define PRINTF(...) printf(__VA_ARGS__)
#warning "SCHEDULER_DEBUG_ON is turned ON"
#else
#define PRINTF(...)
#endif

#define SCHEDULER_HEART_BEAT_MSEC       5
#define SCHEDULER_MSEC_TO_COUNT(msec)   ((uint32_t)(msec/SCHEDULER_HEART_BEAT_MSEC))

uint32_t g_schedulerTime = 0;

uint32_t g_boardStateTask_counter = 0;
bool g_boardStateTask_enable = true;
bool g_boardStateTask_go = false;
#define SCHEDULER_BOARDSTATE_TASK_COUNTER_MAX  SCHEDULER_MSEC_TO_COUNT(5)


uint32_t g_ledBlinkTask_counter = 0;
bool g_ledBlinkTask_enable = true;
bool g_ledBlinkTask_go = false;
#define SCHEDULER_LEDBLINK_TASK_COUNTER_MAX  SCHEDULER_MSEC_TO_COUNT(125)


void Scheduler_init()
{{
    g_schedulerTime = SysTime_msec();
}}

void Scheduler_mainFunction_foreground()
{{
    if(SysTime_msecIntervalElapsed(g_schedulerTime, SCHEDULER_HEART_BEAT_MSEC)) {{
        g_schedulerTime = SysTime_msec();
    }}
    else {{
        return;
    }}

    //-------------------------------------------------------------------------
    g_boardStateTask_counter += 1;
    if(g_boardStateTask_counter >= SCHEDULER_BOARDSTATE_TASK_COUNTER_MAX) {{
        g_boardStateTask_counter = 0;
        if(g_boardStateTask_enable) {{
            g_boardStateTask_go = true;
        }}
    }}
    //-------------------------------------------------------------------------
    g_ledBlinkTask_counter += 1;
    if(g_ledBlinkTask_counter >= SCHEDULER_LEDBLINK_TASK_COUNTER_MAX) {{
        g_ledBlinkTask_counter = 0;
        if(g_ledBlinkTask_enable) {{
            g_ledBlinkTask_go = true;
        }}
    }}
}}


void Scheduler_mainFunction_background()
{{
    while(1) {{
        if(g_boardStateTask_go) {{
            g_boardStateTask_go = false;
            BoardState_mainFunction();
        }}
        if(g_ledBlinkTask_go) {{
            g_ledBlinkTask_go = false;
            //BHAL_LED_BLUE_TGL();
        }}

        // Non-scheduled tasks are done here
    }}
}}
