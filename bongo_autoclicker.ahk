#NoEnv
#SingleInstance Force
SetBatchLines, -1
SetKeyDelay, 15, 15
SetMouseDelay, 15

ToolTip, Bongo Cat Steam Clicker: Press F6 to Toggle
SetTimer, RemoveToolTip, 3000

F6::
Toggle := !Toggle
if (Toggle) {
    SoundBeep, 1200, 100
    SetTimer, BongoLoop, 30
} else {
    SoundBeep, 600, 100
    SetTimer, BongoLoop, Off
}
return

BongoLoop:
    SendEvent, {Space}
    SendEvent, {a}
    SendEvent, {d}
return

RemoveToolTip:
    ToolTip
    SetTimer, RemoveToolTip, Off
return

Esc::ExitApp
