#include "../tools/remix_runtime/remix_texture_coordinates.h"
#include <iostream>
static_assert(sfc_remix_adapter::textureV(0.0f)==1.0f);
static_assert(sfc_remix_adapter::textureV(1.0f)==0.0f);
static_assert(sfc_remix_adapter::textureV(0.25f)==0.75f);
static_assert(sfc_remix_adapter::textureV(-0.25f)==1.25f);
static_assert(sfc_remix_adapter::textureV(1.25f)==-0.25f);
int main(){
 // No clamping: preserve repeating/out-of-range coordinates. Applying twice
 // returns the source, so no second image-row conversion may be added.
 for(float v:{-1.0f,-0.25f,0.0f,0.25f,0.5f,0.75f,1.0f,1.25f,2.0f})
  if(sfc_remix_adapter::textureV(sfc_remix_adapter::textureV(v))!=v)return 1;
 std::cout<<"Remix-only texture origin PASS 14 checks\n";return 0;
}
