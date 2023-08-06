#include "device_hal.h"
#include "sys_time.h"
#include "scheduler.h"
#include "board_app.h"

void NMI_Handler()
{{
    //This function handles Non maskable interrupt.
    while(1) {{}};
}}

void HardFault_Handler()
{{
    //This function handles Hard fault interrupt.
    while(1) {{}};
}}

void MemManage_Handler()
{{
    //This function handles Memory management fault.
    while(1) {{}};
}}

void BusFault_Handler()
{{
    //This function handles Pre-fetch fault, memory access fault.
    while(1) {{}};
}}

void UsageFault_Handler()
{{
    //This function handles Undefined instruction or illegal state.
    while(1) {{}};
}}

void SVC_Handler()
{{
    //This function handles System service call via SWI instruction.
    while(1) {{}};
}}

void DebugMon_Handler()
{{
    //This function handles Debug monitor.
    while(1) {{}};
}}

void PendSV_Handler()
{{
    //This function handles Pendable request for system service.
    while(1) {{}};
}}

void SysTick_Handler()
{{
    static uint32_t halTime = 0;

    SysTime_mainFunction_tick();

    // Every milli-second increment the HAL library tick
    if(SysTime_msecIntervalElapsed(halTime, 1)) {{
        HAL_IncTick();
        HAL_SYSTICK_IRQHandler();
        halTime = SysTime_msec();
    }}

    // Don't proceed until the board application is initialized
    // This makes sure that kernel tick does not get executed
    // before all the tasks are initialized.
    if(BoardApp_isInitialized == 0) {{
        return;
    }}

    Scheduler_mainFunction_foreground();
}}
