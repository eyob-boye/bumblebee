/******************************************************************************
Overview: This file the application that needs to run on the board. This is
the place to intialize the tasks for rtos and kick start the kernel.

*******************************************************************************/

#include "scheduler.h"

int BoardApp_isInitialized = 0;

void BoardApp_init() 
{{
    Scheduler_init();
    BoardApp_isInitialized = 1;
}}

void BoardApp_mainFunction()
{{
    Scheduler_mainFunction_background();
}}
