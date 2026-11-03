#pragma once
namespace native_insertion {
// Native insertion writes through its explicit dispatch,not draw observers.
// Legacy depth observation and foreground replay still need those events.
constexpr bool needsDrawObservers(bool directGame,bool nativeGate,bool foreground){
 return directGame&&(!nativeGate||foreground);
}
}
