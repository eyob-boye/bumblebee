#include <stdint.h>
#include <stdbool.h>


typedef struct {{
    uint32_t usec;
    uint32_t msec;
    uint32_t sec;
    uint32_t minute;
    uint32_t usecWorking;
    uint32_t msecWorking;
    uint32_t secWorking;
    uint32_t minuteWorking;
}} SysTime_t;


SysTime_t g_sysTime;

void SysTime_init()
{{
    g_sysTime.usec = 0;
    g_sysTime.msec = 0;
    g_sysTime.sec = 0;
    g_sysTime.minute = 0;
    g_sysTime.usecWorking = 0;
    g_sysTime.msecWorking = 0;
    g_sysTime.secWorking = 0;
    g_sysTime.minuteWorking = 0;
}}

#define SYS_TIME_CFG_NANOSEC_PER_TICK 100000U
#define SYS_TIME_USEC_PER_TICK        ((uint32_t)(SYS_TIME_CFG_NANOSEC_PER_TICK/1000))


void SysTime_mainFunction_tick()
{{
    g_sysTime.usec += SYS_TIME_USEC_PER_TICK;
    g_sysTime.msecWorking += SYS_TIME_CFG_NANOSEC_PER_TICK;
    if(g_sysTime.msecWorking >= 1000000U) {{
        g_sysTime.msec += 1;
        g_sysTime.msecWorking -= 1000000U;
        g_sysTime.secWorking += 1;
        if(g_sysTime.secWorking >= 1000) {{
            g_sysTime.sec += 1;
            g_sysTime.secWorking = 0;
            g_sysTime.minuteWorking += 1;
            if(g_sysTime.minuteWorking >= 60) {{
                g_sysTime.minute += 1;
                g_sysTime.minuteWorking = 0;
            }}
        }}
    }}
}}


//This is not compute efficient way when compared to the fixed tick update. 
//This is useful in a non-embedded environments such as unit test.
void SysTime_mainFunction_tickVariable(uint32_t nanoSecSincePreviousTick)
{{
    g_sysTime.usecWorking += nanoSecSincePreviousTick;
    if(g_sysTime.usecWorking >= 1000) {{
        uint32_t usecIncrement = ( g_sysTime.usecWorking / 1000);
        g_sysTime.usecWorking %= 1000;
        g_sysTime.usec += usecIncrement;
        g_sysTime.msecWorking += usecIncrement;
        if(g_sysTime.msecWorking >= 1000) {{
            uint32_t msecIncrement = ( g_sysTime.msecWorking / 1000);
            g_sysTime.msecWorking %= 1000;
            g_sysTime.msec += msecIncrement;
            g_sysTime.secWorking += msecIncrement;
            if(g_sysTime.secWorking >= 1000) {{
                uint32_t secIncrement = ( g_sysTime.secWorking / 1000);
                g_sysTime.secWorking %= 1000;
                g_sysTime.sec += secIncrement;
                g_sysTime.minuteWorking += secIncrement;
                if(g_sysTime.minuteWorking >= 60) {{
                    uint32_t minuteIncrement = ( g_sysTime.minuteWorking / 60);
                    g_sysTime.minuteWorking %= 1000;
                    g_sysTime.minute += minuteIncrement;
                }}
            }}
        }}
    }}
}}

bool SysTime_usecIntervalElapsed(uint32_t startTime, uint32_t interval)
{{
    return ((uint32_t)(g_sysTime.usec - startTime) >= interval) ? true: false;
}}

bool SysTime_msecIntervalElapsed(uint32_t startTime, uint32_t interval)
{{
    return ((uint32_t)(g_sysTime.msec - startTime) >= interval) ? true: false;
}}

bool SysTime_secIntervalElapsed(uint32_t startTime, uint32_t interval)
{{
    return ((uint32_t)(g_sysTime.sec - startTime) >= interval) ? true: false;
}}

bool SysTime_minuteIntervalElapsed(uint32_t startTime, uint32_t interval)
{{
    return ((uint32_t)(g_sysTime.minute - startTime) >= interval) ? true: false;
}}

uint32_t SysTime_usec()
{{
    return (g_sysTime.usec);
}}

uint32_t SysTime_msec()
{{
    return (g_sysTime.msec);
}}

uint32_t SysTime_sec()
{{
    return (g_sysTime.sec);
}}

uint32_t SysTime_minute()
{{
    return (g_sysTime.minute);
}}

uint32_t SysTime_usecSince(uint32_t startTime)
{{
    return ((uint32_t)(g_sysTime.usec - startTime));
}}

uint32_t SysTime_msecSince(uint32_t startTime)
{{
    return ((uint32_t)(g_sysTime.msec - startTime));
}}

uint32_t SysTime_secSince(uint32_t startTime)
{{
    return ((uint32_t)(g_sysTime.sec - startTime));
}}

uint32_t SysTime_mineutSince(uint32_t startTime)
{{
    return ((uint32_t)(g_sysTime.minute - startTime));
}}
