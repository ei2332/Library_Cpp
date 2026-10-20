//// @url https://github.com/ei2332/Library_Cpp/blob/main/src/debug.hpp
//// @name debug
#ifdef DEBUG_OUT
#include <iostream>
#include <string_view>
using namespace std;
template <class T>
concept Range = requires(const T &x) { begin(x); };
template <class T>
concept Tuple = requires { tuple_size<remove_cvref_t<T>>::value; };
template <class T>
concept Text = requires(const T &x) { string_view(x); };
template <class T>
void Dprint(const T &x) {
    if constexpr (Text<T>) {
        cerr << x;
    } else if constexpr (Range<T>) {
        cerr << '{';
        bool sep = 0;
        for (const auto &e : x) {
            if (sep) cerr << ",";
            Dprint(e);
            sep = 1;
        }
        cerr << '}';
    } else if constexpr (Tuple<T>) {
        cerr << '{';
        bool sep = 0;
        auto one = [&](const auto &e) {
            if (sep) cerr << ",";
            Dprint(e);
            sep = 1;
        };
        apply([&](const auto &...e) { (one(e), ...); }, x);
        cerr << '}';
    } else {
        cerr << x;
    }
}
template <class... T>
void print(int line, const T &...args) {
    cerr << '[' << line << "] ";
    size_t i = 0;
    auto one = [&](const auto &x) {
        if (i) cerr << ',';
        const bool color = i++ & 1;
        cerr << (color ? "\033[96m" : "");
        Dprint(x);
        cerr << (color ? "\033[0m" : "");
    };
    (one(args), ...);
    cerr << '\n';
}

#define debug(...) print(__LINE__, __VA_ARGS__)

#endif
