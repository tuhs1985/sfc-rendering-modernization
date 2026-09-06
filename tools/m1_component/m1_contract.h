#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace sfc_m1 {

template <typename UInt>
inline bool should_sample_geometry(UInt frame, UInt& sample_frame,
                                   UInt& samples_in_frame, UInt limit) {
    if (!limit) return false;
    if (sample_frame != frame) {
        sample_frame = frame;
        samples_in_frame = 0;
    }
    if (samples_in_frame >= limit) return false;
    ++samples_in_frame;
    return true;
}

struct OwnerObservation {
    std::uint32_t id = 0;
    bool first_seen = false;
    bool overflow = false;
};

template <std::size_t Capacity>
class OwnerTable {
public:
    struct Slot {
        std::uintptr_t ship = 0;
        std::uintptr_t visual = 0;
        std::uint32_t id = 0;
        std::uint32_t last_frame = 0;
        bool active = false;
    };

    OwnerObservation observe(std::uintptr_t ship, std::uintptr_t visual,
                             std::uint32_t frame) {
        if (!ship) return {};
        for (Slot& slot : slots_) {
            if (slot.active && slot.ship == ship) {
                slot.visual = visual;
                slot.last_frame = frame;
                return {slot.id, false, false};
            }
        }
        Slot* candidate = nullptr;
        for (Slot& slot : slots_) {
            if (!slot.active && slot.ship == ship) {
                candidate = &slot;
                break;
            }
            if (!candidate && !slot.active) candidate = &slot;
        }
        if (!candidate) return {0, false, true};
        candidate->ship = ship;
        candidate->visual = visual;
        candidate->id = next_id_++;
        candidate->last_frame = frame;
        candidate->active = true;
        return {candidate->id, true, false};
    }

    std::uint32_t find_by_visual(std::uintptr_t visual) const {
        for (const Slot& slot : slots_) {
            if (slot.active && slot.visual == visual) return slot.id;
        }
        return 0;
    }

    std::uint32_t find_by_ship(std::uintptr_t ship) const {
        for (const Slot& slot : slots_) {
            if (slot.active && slot.ship == ship) return slot.id;
        }
        return 0;
    }

    Slot* find_by_id(std::uint32_t id) {
        for (Slot& slot : slots_) {
            if (slot.active && slot.id == id) return &slot;
        }
        return nullptr;
    }

    template <typename RetireCallback>
    void retire_before(std::uint32_t oldest_live_frame, RetireCallback callback) {
        for (Slot& slot : slots_) {
            if (slot.active && slot.last_frame < oldest_live_frame) {
                callback(slot);
                slot.active = false;
            }
        }
    }

    std::size_t active_count() const {
        std::size_t count = 0;
        for (const Slot& slot : slots_) if (slot.active) ++count;
        return count;
    }

    const std::array<Slot, Capacity>& slots() const { return slots_; }

private:
    std::array<Slot, Capacity> slots_{};
    std::uint32_t next_id_ = 1;
};

template <typename T, std::size_t Capacity>
class BoundedBuffer {
public:
    bool push(const T& value) {
        if (size_ >= Capacity) {
            saturated_ = true;
            return false;
        }
        values_[size_++] = value;
        return true;
    }

    std::size_t size() const { return size_; }
    constexpr std::size_t capacity() const { return Capacity; }
    bool saturated() const { return saturated_; }
    const T& operator[](std::size_t index) const { return values_[index]; }

private:
    std::array<T, Capacity> values_{};
    std::size_t size_ = 0;
    bool saturated_ = false;
};

}  // namespace sfc_m1
