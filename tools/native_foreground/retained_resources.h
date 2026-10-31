#pragma once
#include <d3d11.h>
#include <wrl/client.h>
#include <array>
#include <cstdint>
#include <stdexcept>

// Resource-version primitive only. This is not authorization to replay an
// arbitrary native draw: pipeline, producer, coverage and depth still matter.
namespace native_foreground {
using Microsoft::WRL::ComPtr;
struct Identity {
    uint64_t session{}, frame{}, ownerEpoch{}, revision{};
    bool valid() const { return session && frame && ownerEpoch && revision; }
    bool operator==(const Identity& b) const {
        return session == b.session && frame == b.frame &&
            ownerEpoch == b.ownerEpoch && revision == b.revision;
    }
};
enum class State { free, recording, sealed, submitted };
class RetainedResources {
    struct Buffer {
        ComPtr<ID3D11Buffer> storage;
        UINT capacity{}, bytes{}, bind{};
    };
    struct Image {
        ComPtr<ID3D11Texture2D> storage;
        D3D11_TEXTURE2D_DESC desc{};
        bool written{};
    };
    // Slots are set up before observation, never grown by capture.
    std::array<Buffer, 18> buffers_{};
    std::array<Image, 3> images_{};
    ComPtr<ID3D11Query> completed_;
    ComPtr<ID3D11Device> device_;
    GUID deviceTag_{};
    bool tagged_{};
    State state_{State::free};
    Identity identity_{};
    bool failed_{};
    uint64_t allocated_{};
    static void check(HRESULT h) { if (FAILED(h)) throw std::runtime_error("foreground resource setup"); }
    bool contextMatches(ID3D11DeviceContext* c) const noexcept {
        if (!c || c->GetType() != D3D11_DEVICE_CONTEXT_IMMEDIATE) return false;
        ComPtr<ID3D11Device> d; c->GetDevice(&d); return sameDevice(d.Get());
    }
    bool resourceMatches(ID3D11Resource* r) const noexcept {
        if (!r) return false;
        ComPtr<ID3D11Device> d; r->GetDevice(&d); return sameDevice(d.Get());
    }
    bool sameDevice(ID3D11Device* d) const noexcept {
        if(!d||!tagged_)return false;
        // ReShade's GetDevice can return its proxy while get_native returns the
        // underlying device. Standard device private data reaches the same
        // native object through both. Never equate raw wrapper addresses.
        UINT value=0,bytes=sizeof(value);
        return SUCCEEDED(d->GetPrivateData(deviceTag_,&bytes,&value))&&bytes==sizeof(value)&&value==0x53464744;
    }
public:
    RetainedResources()=default;
    RetainedResources(const RetainedResources&)=delete;
    RetainedResources& operator=(const RetainedResources&)=delete;
    ~RetainedResources(){if(tagged_&&device_)device_->SetPrivateData(deviceTag_,0,nullptr);}
    static constexpr uint64_t limit = 4ull * 1024 * 1024;
    void initialize(ID3D11Device* d) {
        if (completed_) throw std::runtime_error("foreground already initialized");
        D3D11_QUERY_DESC q{D3D11_QUERY_EVENT, 0};
        check(d->CreateQuery(&q, &completed_));
        device_ = d;
        check(CoCreateGuid(&deviceTag_));const UINT value=0x53464744;
        check(d->SetPrivateData(deviceTag_,sizeof(value),&value));tagged_=true;
    }
    void prepareBuffer(ID3D11Device* d, unsigned slot, UINT bytes, UINT bind) {
        if (d != device_.Get() || state_ != State::free || slot >= buffers_.size() || buffers_[slot].storage ||
            !bytes || allocated_ + bytes > limit ||
            (bind != D3D11_BIND_VERTEX_BUFFER && bind != D3D11_BIND_INDEX_BUFFER &&
             bind != D3D11_BIND_CONSTANT_BUFFER) ||
            (bind == D3D11_BIND_CONSTANT_BUFFER && (bytes > 65536 || bytes % 16)))
            throw std::runtime_error("foreground buffer bounds");
        D3D11_BUFFER_DESC desc{}; desc.ByteWidth = bytes;
        desc.BindFlags = bind; desc.Usage = D3D11_USAGE_DEFAULT;
        auto& b = buffers_[slot]; check(d->CreateBuffer(&desc, nullptr, &b.storage));
        b.capacity = bytes; b.bind = bind; allocated_ += bytes;
    }
    void prepareImage(ID3D11Device* d, unsigned slot, const D3D11_TEXTURE2D_DESC& source) {
        // Exact layouts only. No resizing, mip synthesis or format conversion.
        const uint64_t bytes = uint64_t(source.Width) * source.Height * 4;
        if (d != device_.Get() || state_ != State::free || slot >= images_.size() || images_[slot].storage ||
            !source.Width || !source.Height || source.Width > 256 || source.Height > 256 ||
            source.MipLevels != 1 || source.ArraySize != 1 || source.SampleDesc.Count != 1 ||
            source.SampleDesc.Quality != 0 || source.MiscFlags || allocated_ + bytes > limit ||
            (source.Format != DXGI_FORMAT_R8G8B8A8_UNORM && source.Format != DXGI_FORMAT_R8G8B8A8_TYPELESS))
            throw std::runtime_error("foreground image layout unsupported");
        auto& im = images_[slot]; im.desc = source; im.desc.Usage = D3D11_USAGE_DEFAULT;
        im.desc.BindFlags = D3D11_BIND_SHADER_RESOURCE; im.desc.CPUAccessFlags = 0;
        check(d->CreateTexture2D(&im.desc, nullptr, &im.storage)); allocated_ += bytes;
    }
    bool begin(const Identity& id) noexcept {
        if (!completed_ || state_ != State::free || !id.valid()) return false;
        identity_ = id; failed_ = false;
        for (auto& b : buffers_) b.bytes = 0;
        for (auto& im : images_) im.written = false;
        state_ = State::recording; return true;
    }
    void prepareImageView(ID3D11Device* d,unsigned slot,const D3D11_SHADER_RESOURCE_VIEW_DESC& desc,
                          ID3D11ShaderResourceView** view) {
        if(d!=device_.Get()||state_!=State::free||slot>=images_.size()||!images_[slot].storage)
            throw std::runtime_error("foreground view setup state");
        check(d->CreateShaderResourceView(images_[slot].storage.Get(),&desc,view));
    }
    bool captureBuffer(ID3D11DeviceContext* c, unsigned slot, ID3D11Buffer* source) noexcept {
        if (state_ != State::recording) return false;
        if (slot >= buffers_.size() || !resourceMatches(source) || !contextMatches(c)) { failed_ = true; return false; }
        auto& b = buffers_[slot]; D3D11_BUFFER_DESC desc{}; source->GetDesc(&desc);
        if (!b.storage || b.bytes || desc.ByteWidth != b.capacity || desc.StructureByteStride ||
            desc.MiscFlags || !(desc.BindFlags & b.bind) || source == b.storage.Get()) {
            failed_ = true; return false;
        }
        c->CopyResource(b.storage.Get(), source); b.bytes = desc.ByteWidth; return true;
    }
    bool captureImage(ID3D11DeviceContext* c, unsigned slot, ID3D11Texture2D* source) noexcept {
        if (state_ != State::recording) return false;
        if (slot >= images_.size() || !resourceMatches(source) || !contextMatches(c)) { failed_ = true; return false; }
        auto& im = images_[slot]; D3D11_TEXTURE2D_DESC d{}; source->GetDesc(&d);
        if (!im.storage || im.written || d.Width != im.desc.Width || d.Height != im.desc.Height ||
            d.Format != im.desc.Format || d.MipLevels != 1 || d.ArraySize != 1 ||
            d.SampleDesc.Count != 1 || d.SampleDesc.Quality || d.MiscFlags || source == im.storage.Get()) {
            failed_ = true; return false;
        }
        c->CopyResource(im.storage.Get(), source); im.written = true; return true;
    }
    bool seal() noexcept {
        if (state_ != State::recording || failed_ || !allocated_) return false;
        // Every prepared slot is required. Partial capture cannot be replayed.
        for (const auto& b : buffers_) if (b.storage && !b.bytes) return false;
        for (const auto& im : images_) if (im.storage && !im.written) return false;
        state_ = State::sealed; return true;
    }
    ID3D11Buffer* buffer(unsigned slot, const Identity& id) const noexcept {
        return state_ == State::sealed && identity_ == id && slot < buffers_.size() &&
            buffers_[slot].bytes ? buffers_[slot].storage.Get() : nullptr;
    }
    ID3D11Texture2D* image(unsigned slot, const Identity& id) const noexcept {
        return state_ == State::sealed && identity_ == id && slot < images_.size() &&
            images_[slot].written ? images_[slot].storage.Get() : nullptr;
    }
    bool finish(ID3D11DeviceContext* c) noexcept {
        if (!contextMatches(c) || (state_ != State::sealed && state_ != State::recording)) return false;
        c->End(completed_.Get()); state_ = State::submitted; return true;
    }
    bool tryRecycle(ID3D11DeviceContext* c) noexcept {
        if (state_ != State::submitted || !contextMatches(c)) return false;
        BOOL done = FALSE;
        if (c->GetData(completed_.Get(), &done, sizeof(done), D3D11_ASYNC_GETDATA_DONOTFLUSH) != S_OK || !done)
            return false;
        state_ = State::free; identity_ = {}; return true;
    }
    uint64_t bytes() const noexcept { return allocated_; }
    bool available() const noexcept {return state_==State::free;}
};
} // namespace native_foreground
