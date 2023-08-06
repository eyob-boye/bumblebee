/******************************************************************************
Overview: This file controls the board's running state.

*******************************************************************************/
#include "sys_time.h"
#include "mcu_init.h"

static BoardState_t g_boardState = BoardState_STARTUP_1OF3;

void BoardState_startup_1of3()
{{
    SysTime_init();
    McuInit_HAL();
    McuInit_systick();    //Initialize with original clock setting
    McuInit_clock();
    McuInit_systick();    //Initialize after application clock setting
    g_boardState = BoardState_STARTUP_2OF3;
}}

void BoardState_startup_2of3()
{{
    //McuInit_*()
    g_boardState = BoardState_STARTUP_3OF3;
}}

static void startup_3of3()
{{
    g_boardState = BoardState_RUN;
}}

static void run()
{{
    //if(FirmwareUpgradeMgr_isRebootRequested()) {{
    //    g_boardState = BoardState_SHUTDOWN_TO_BOOTLOADER;
    //}}
    //else if(LowPowerSupplyMgr_isSleepRequested()) {{
    //
    //}}
    //else {{
        g_boardState = BoardState_RUN;
    //}}
}}

static void shutdownToBootloader()
{{
    //Do graceful shutdown of the board and reboot
}}

static void shutdownToOff()
{{
    //Do graceful shutdown of the board and turn off power supply
}}

static void shutdownToSleep()
{{
    //Do graceful transition to sleep
}}

static void wakeupFromSleep()
{{
    //Do graceful wakeup state of the board from sleep
}}

void BoardState_mainFunction()
{{
    switch(g_boardState) {{
        case BoardState_STARTUP_1OF3:
            BoardState_startup_1of3();
            break;
        case BoardState_STARTUP_2OF3:
            BoardState_startup_2of3();
            break;
        case BoardState_STARTUP_3OF3:
            startup_3of3();
            break;
        case BoardState_RUN:
            run();
            break;
        case BoardState_SHUTDOWN_TO_BOOTLOADER:
            shutdownToBootloader();
            while(1){{}};
            //break;
        case BoardState_SHUTDOWN_TO_OFF:
            shutdownToOff();
            while(1){{}};
            //break;
        case BoardState_SHUTDOWN_TO_SLEEP:
            shutdownToSleep();
            while(1){{}};
            //break;
        case BoardState_WAKEUP_FROM_SLEEP:
            wakeupFromSleep();
            while(1){{}};
            //break;
        default:
            while(1){{}};
            //break;
    }}
}}

BoardState_t BoardState_get()
{{
    return(g_boardState);
}}
