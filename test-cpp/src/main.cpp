#include <iostream>
#include <vector>
#include <unordered_map>
#include <string>
#include <boost/hana.hpp>

template <typename K>
class hetero_map
{

  public:
    template <typename T>
    const T &get(K id)
    {
        return internal_<T>[this].at(id);
    }
    template <typename T>
    void get_to(K id, T &t)
    {
        t = internal_<T>[this].at(id);
    }
    template <typename T>
    void put(K id, T &&t)
    {
        internal_<T>[this].emplace(id, std::forward<T>(t));
    }

  private:
    template <typename T>
    static std::unordered_map<const hetero_map<K> *, std::unordered_map<K, T>> internal_;
};

template <typename K>
template <typename T>
std::unordered_map<const hetero_map<K> *, std::unordered_map<K, T>> hetero_map<K>::internal_;

int main()
{
    using namespace std::string_literals;
    hetero_map<int> hmap;
    hmap.put(10, "123"s);
    hmap.put(1, 123);

    std::cout << hmap.get<std::string>(10) << std::endl;
    std::cout << hmap.get<int>(1) << std::endl;

    hetero_map<std::string> hmap2;
    hmap2.put("10"s, 123);
    hmap2.put("1"s, "123"s);
    std::cout << hmap2.get<int>("10"s) << std::endl;
    std::cout << hmap2.get<std::string>("1"s) << std::endl;
}