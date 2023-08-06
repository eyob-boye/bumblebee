typedef enum {{
    BoardState_STARTUP_1OF3,
    BoardState_STARTUP_2OF3,
    BoardState_STARTUP_3OF3,
    BoardState_RUN,
    BoardState_SHUTDOWN_TO_BOOTLOADER,
    BoardState_SHUTDOWN_TO_OFF,
    BoardState_SHUTDOWN_TO_SLEEP,
    BoardState_WAKEUP_FROM_SLEEP
}} BoardState_t;

void BoardState_startup_1of3(void);
void BoardState_startup_2of3(void);
void BoardState_mainFunction(void);
BoardState_t BoardState_get(void);
