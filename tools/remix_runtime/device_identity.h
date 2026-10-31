#pragma once
#include <d3d11.h>
#include <wrl/client.h>
#include <stdexcept>
// Public private-data identity works through ReShade's device wrapper as well as
// native resource GetDevice. Setup only; no private unwrap API or pointer guesses.
class GraphicsDeviceIdentity {
 Microsoft::WRL::ComPtr<ID3D11Device> owner_;GUID tag_{};bool tagged_=false;
public:
 void initialize(ID3D11Device* d){if(tagged_||!d)throw std::runtime_error("Device identity initialization");
  owner_=d;const UINT value=0x53464744;
  if(FAILED(CoCreateGuid(&tag_))||FAILED(d->SetPrivateData(tag_,sizeof(value),&value)))throw std::runtime_error("Device identity tag");tagged_=true;}
 ~GraphicsDeviceIdentity(){if(tagged_)owner_->SetPrivateData(tag_,0,nullptr);}
 bool matches(ID3D11Device* d)const{UINT value=0,bytes=sizeof(value);return tagged_&&d&&
  SUCCEEDED(d->GetPrivateData(tag_,&bytes,&value))&&bytes==sizeof(value)&&value==0x53464744;}
};
