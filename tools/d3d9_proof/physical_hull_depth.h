// Adapter-owned physical first-hit depth for qualified opaque rigid meshes.
// Remix PSR depth describes reflected/refracted surfaces, not hull coverage.
// Worker only: immutable cached geometry, fixed 32-instance submission array.
#pragma once
struct PhysicalHullDepth {
 struct Mesh {ComPtr<ID3D11Buffer> vertices,indices;UINT count=0;uint64_t bytes=0;};
 struct Submission {const Mesh* mesh=nullptr;Frame frame{};};
 ComPtr<ID3D11Device> device;ComPtr<ID3D11RenderTargetView> target;
 ComPtr<ID3D11DepthStencilView> depth;ComPtr<ID3D11VertexShader> vertex;
 ComPtr<ID3D11PixelShader> pixel;ComPtr<ID3D11InputLayout> layout;
 ComPtr<ID3D11Buffer> constants;ComPtr<ID3D11RasterizerState> raster;
 ComPtr<ID3D11DepthStencilState> zstate;ComPtr<ID3D11BlendState> opaque;
 std::array<Submission,32> submissions{};unsigned count=0;UINT width=0,height=0;
 bool enabled=false;uint64_t batches=0,draws=0,geometryBytes=0;
 void start(ID3D11Device* d,ID3D11Texture2D* output,bool active){
  enabled=active;if(!enabled)return;device=d;D3D11_TEXTURE2D_DESC desc{};output->GetDesc(&desc);
  require(desc.Format==DXGI_FORMAT_R32_FLOAT&&desc.SampleDesc.Count==1&&desc.ArraySize==1&&desc.MipLevels==1,"physical hull output layout");
  width=desc.Width;height=desc.Height;
  // Existing replacement surfaces consume 15 four-byte planes; this DSV adds
  // one. At 1920x1080 the complete controlled pool stays below 128 MiB.
  require(uint64_t(width)*height*4*16<=128ull*1024*1024,"physical hull total output128MiB cap");
  ok(d->CreateRenderTargetView(output,nullptr,&target),"physical hull output");
  desc.Format=DXGI_FORMAT_D32_FLOAT;desc.BindFlags=D3D11_BIND_DEPTH_STENCIL;desc.MiscFlags=0;
  ComPtr<ID3D11Texture2D> buffer;ok(d->CreateTexture2D(&desc,nullptr,&buffer),"physical hull Z");
  ok(d->CreateDepthStencilView(buffer.Get(),nullptr,&depth),"physical hull DSV");
  const char* vs=R"(cbuffer M:register(b0){row_major float4x4 model;row_major float4x4 view;row_major float4x4 projection;};
float4 main(float3 p:POSITION):SV_Position{return mul(projection,mul(view,mul(model,float4(p,1))));})";
  const char* ps="float main(float4 p:SV_Position):SV_Target{return p.z;}";
  ComPtr<ID3DBlob> v,p;ok(D3DCompile(vs,strlen(vs),nullptr,nullptr,nullptr,"main","vs_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&v,nullptr),"physical hull VS compile");
  ok(D3DCompile(ps,strlen(ps),nullptr,nullptr,nullptr,"main","ps_4_1",D3DCOMPILE_ENABLE_STRICTNESS,0,&p,nullptr),"physical hull PS compile");
  ok(d->CreateVertexShader(v->GetBufferPointer(),v->GetBufferSize(),nullptr,&vertex),"physical hull VS");
  ok(d->CreatePixelShader(p->GetBufferPointer(),p->GetBufferSize(),nullptr,&pixel),"physical hull PS");
  D3D11_INPUT_ELEMENT_DESC input{"POSITION",0,DXGI_FORMAT_R32G32B32_FLOAT,0,0,D3D11_INPUT_PER_VERTEX_DATA,0};
  ok(d->CreateInputLayout(&input,1,v->GetBufferPointer(),v->GetBufferSize(),&layout),"physical hull layout");
  D3D11_BUFFER_DESC cb{};cb.ByteWidth=sizeof(float)*48;cb.BindFlags=D3D11_BIND_CONSTANT_BUFFER;
  ok(d->CreateBuffer(&cb,nullptr,&constants),"physical hull transforms");
  D3D11_RASTERIZER_DESC r{};r.FillMode=D3D11_FILL_SOLID;r.CullMode=D3D11_CULL_NONE;r.DepthClipEnable=TRUE;
  ok(d->CreateRasterizerState(&r,&raster),"physical hull raster");
  D3D11_DEPTH_STENCIL_DESC z{};z.DepthEnable=TRUE;z.DepthWriteMask=D3D11_DEPTH_WRITE_MASK_ALL;z.DepthFunc=D3D11_COMPARISON_LESS_EQUAL;
  ok(d->CreateDepthStencilState(&z,&zstate),"physical hull Z state");
  D3D11_BLEND_DESC b{};b.RenderTarget[0].RenderTargetWriteMask=D3D11_COLOR_WRITE_ENABLE_ALL;
  ok(d->CreateBlendState(&b,&opaque),"physical hull opaque");
  std::cout<<"PHYSICAL_HULL_DEPTH enabled=1 reflected_depth_used=0 scratch_bytes="<<uint64_t(width)*height*4<<'\n';
 }
 Mesh prepare(const Scene& scene){
  Mesh m;if(!enabled)return m;
  require(!scene.vertices.empty()&&!scene.indices.empty()&&scene.vertices.size()<=32768&&scene.indices.size()<=32768,"physical hull geometry bounds");
  // Same vertex and index arrays as ordinary D3D9. No geometry,UV or normal edits.
  D3D11_BUFFER_DESC b{};b.ByteWidth=static_cast<UINT>(scene.vertices.size()*sizeof(Vertex));b.BindFlags=D3D11_BIND_VERTEX_BUFFER;b.Usage=D3D11_USAGE_IMMUTABLE;
  D3D11_SUBRESOURCE_DATA data{};data.pSysMem=scene.vertices.data();ok(device->CreateBuffer(&b,&data,&m.vertices),"physical hull cached vertices");
  m.bytes=b.ByteWidth;b.ByteWidth=static_cast<UINT>(scene.indices.size()*sizeof(uint32_t));b.BindFlags=D3D11_BIND_INDEX_BUFFER;data.pSysMem=scene.indices.data();
  ok(device->CreateBuffer(&b,&data,&m.indices),"physical hull cached indices");m.bytes+=b.ByteWidth;m.count=static_cast<UINT>(scene.indices.size());geometryBytes+=m.bytes;return m;
 }
 void begin(){count=0;}
 void submit(const Mesh& mesh,const Frame& frame){
  if(!enabled||!frame.active)return;require(count<submissions.size()&&mesh.vertices&&mesh.indices&&mesh.count,"physical hull bounded submission");
  submissions[count++]={&mesh,frame};
 }
 void draw(ID3D11DeviceContext* c){
  if(!enabled)return;c->ClearState();const float background[4]={-1234,0,0,0};c->ClearRenderTargetView(target.Get(),background);c->ClearDepthStencilView(depth.Get(),D3D11_CLEAR_DEPTH,1,0);
  auto* rt=target.Get();c->OMSetRenderTargets(1,&rt,depth.Get());c->OMSetDepthStencilState(zstate.Get(),0);c->OMSetBlendState(opaque.Get(),nullptr,0xffffffff);
  c->RSSetState(raster.Get());c->IASetInputLayout(layout.Get());c->IASetPrimitiveTopology(D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);
  c->VSSetShader(vertex.Get(),nullptr,0);c->PSSetShader(pixel.Get(),nullptr,0);auto* cb=constants.Get();c->VSSetConstantBuffers(0,1,&cb);
  for(unsigned i=0;i<count;++i){const auto& s=submissions[i];const auto& f=s.frame;
   float matrices[48];memcpy(matrices,f.model,64);memcpy(matrices+16,f.view,64);memcpy(matrices+32,f.projection,64);c->UpdateSubresource(constants.Get(),0,nullptr,matrices,0,0);
   // Remix's returned ray-traced image spans the full output target. The
   // receiver maps it into SFC's tactical viewport once, for colour AND depth.
   // Applying the native viewport here again misregisters hull and colour.
   const D3D11_VIEWPORT viewport{0,0,static_cast<float>(width),static_cast<float>(height),0,1};c->RSSetViewports(1,&viewport);
   auto* vb=s.mesh->vertices.Get();const UINT stride=sizeof(Vertex),offset=0;c->IASetVertexBuffers(0,1,&vb,&stride,&offset);c->IASetIndexBuffer(s.mesh->indices.Get(),DXGI_FORMAT_R32_UINT,0);
   c->DrawIndexed(s.mesh->count,0,0);++draws;
  }++batches;c->ClearState();
 }
 ~PhysicalHullDepth(){if(enabled)std::cout<<"PHYSICAL_HULL_SUMMARY batches="<<batches<<" draws="<<draws<<" uploaded_bytes="<<geometryBytes<<'\n';}
};
