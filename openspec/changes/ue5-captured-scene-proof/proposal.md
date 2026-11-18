# Packaged UE5 scene consumer

Build the sponsor-requested first UE5 proof from the qualified offline SFC-07
capture. The packaged application constructs the ship at runtime from captured
corner geometry and original texture bytes, then renders using the captured
SFC camera. It records source identity and compares output against the native
screen reference. This establishes the first UE consumer of the reusable
interface. Live transport and GPU return are subsequent increments.
