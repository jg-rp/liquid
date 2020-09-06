#include <string>
#include <algorithm>

#ifndef LIQUID_STRINGS_
#define LIQUID_STRINGS_
namespace liquid::strings
{
    bool notspace(int ch)
    {
        bool res = true;

        switch (ch)
        {
        case '\n':
        case ' ':
        case '\t':
        case '\r':
            res = false;
        }

        return res;
    }

    inline void lstrip(std::string *s)
    {
        auto end = std::find_if(s->begin(), s->end(), notspace);
        s->erase(s->begin(), end);
    }

    inline void rstrip(std::string *s)
    {
        auto start = std::find_if(s->rbegin(), s->rend(), notspace).base();
        s->erase(start, s->end());
    }

    inline void strip(std::string *s)
    {
        lstrip(s);
        rstrip(s);
    }
} // namespace liquid::strings
#endif // LIQUID_STRINGS_