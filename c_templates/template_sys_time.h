/******************************************************************************
Overview: Time control abstraction for keeping the application time. This
abstraction will keep the source code consistent with an efficient and
accurate implementation of time.

*******************************************************************************/
#include <stdint.h>
#include <stdbool.h>

bool SysTime_usecIntervalElapsed(uint32_t startTime, uint32_t interval);
bool SysTime_msecIntervalElapsed(uint32_t startTime, uint32_t interval);
bool SysTime_secIntervalElapsed(uint32_t startTime, uint32_t interval);
bool SysTime_minuteIntervalElapsed(uint32_t startTime, uint32_t interval);

uint32_t SysTime_usec(void);
uint32_t SysTime_msec(void);
uint32_t SysTime_sec(void);
uint32_t SysTime_minute(void);

uint32_t SysTime_usecSince(uint32_t startTime);
uint32_t SysTime_msecSince(uint32_t startTime);
uint32_t SysTime_secSince(uint32_t startTime);
uint32_t SysTime_minuteSince(uint32_t startTime);


void SysTime_init(void);
void SysTime_mainFunction_tick(void);
void SysTime_mainFunction_tickVariable(uint32_t nanoSecSincePreviousTick);
