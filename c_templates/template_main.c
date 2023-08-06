#include "board_state.h"
#include "board_app.h"


int main(int argc, char*argv[])
{{
    BoardState_startup_1of3();
    BoardState_startup_2of3();

    BoardApp_init();
    BoardApp_mainFunction(); //This function should not return

    while(1) {{}}           //If we reach here, don't let main() end
    //return 0;
}}

