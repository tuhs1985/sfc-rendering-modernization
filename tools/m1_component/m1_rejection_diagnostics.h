#pragma once
#include <array>
#include <cstdint>
#include <ostream>

namespace sfc_m1 {
// Fixed storage, caller holds recorder lock; no reads of game memory or hook I/O.
struct RejectionSample {
    std::uint32_t phase=0, elapsed=0, kind=0, reason=0, caller=0, thread=0;
    std::uint32_t ship=0, visual=0, model=0, source=0, owner=0;
    std::uint32_t ship_vtable=0, visual_vtable=0, model_vtable=0;
    std::uint32_t ship_match=0, visual_match=0;
};
struct RejectionBucket {
    RejectionSample first{}, last{};
    std::uint64_t count=0;
};
struct RejectionDiagnostics {
    std::array<std::array<std::array<std::uint64_t,13>,4>,4> counts{};
    std::array<RejectionBucket,32> buckets{};
    std::array<RejectionSample,64> examples{};
    std::uint64_t total=0, signature_overflow=0;
    std::uint32_t bucket_count=0;
    void record(const RejectionSample& s) {
        ++total; ++counts[s.phase][s.kind][s.reason];
        // First32 and last32 examples; overwritten middle samples explicitly counted.
        const auto index = total <= 32 ? total-1 : 32+(total-33)%32;
        examples[static_cast<std::size_t>(index)] = s;
        std::uint32_t i=0;
        for (;i<bucket_count;++i) {
            const auto& f=buckets[i].first;
            if(f.kind==s.kind && f.reason==s.reason && f.caller==s.caller &&
               f.ship_vtable==s.ship_vtable && f.visual_vtable==s.visual_vtable &&
               f.model_vtable==s.model_vtable) break;
        }
        if(i==bucket_count) {
            if(bucket_count==buckets.size()) { ++signature_overflow; return; }
            buckets[i].first=s; ++bucket_count;
        }
        buckets[i].last=s; ++buckets[i].count;
    }
    static void sample(std::ostream& out,const RejectionSample& s) {
        out << '[' << s.phase << ',' << s.elapsed << ',' << s.kind << ',' << s.reason
            << ',' << s.caller << ',' << s.thread << ',' << s.ship << ',' << s.visual
            << ',' << s.model << ',' << s.source << ',' << s.owner << ',' << s.ship_vtable
            << ',' << s.visual_vtable << ',' << s.model_vtable << ',' << s.ship_match
            << ',' << s.visual_match << ']';
    }
    void write(std::ostream& out) const {
        out << "{\"schema\":\"m1.rejections.v1\",\"total\":" << total
            << ",\"signature_overflow\":" << signature_overflow
            << ",\"example_omitted\":" << (total>64?total-64:0) << ",\"counts\":[";
        for(std::size_t p=0;p<4;++p) {out << (p?",[":"[");
            for(std::size_t k=0;k<4;++k) {out << (k?",[":"[");
                for(std::size_t r=0;r<13;++r) out << (r?",":"") << counts[p][k][r]; out << ']';}
            out << ']';}
        out << "],\"buckets\":[";
        for(std::uint32_t i=0;i<bucket_count;++i) {out << (i?",{":"{") << "\"count\":" << buckets[i].count << ",\"first\":";
            sample(out,buckets[i].first);out << ",\"last\":";sample(out,buckets[i].last);out << '}';}
        out << "],\"examples\":[";
        const auto n=total<64?static_cast<std::uint32_t>(total):64;
        for(std::uint32_t i=0;i<n;++i) {if(i)out << ',';sample(out,examples[i]);}
        out << "]}";
    }
};
} // namespace sfc_m1
