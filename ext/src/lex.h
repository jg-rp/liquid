#include <string>
#include <regex>
// #include <tuple>
#include <vector>

#ifndef LIQUID_LEX_
#define LIQUID_LEX_
namespace liquid
{
    const std::string TOKEN_ILLEGAL = "illegal";
    const std::string TOKEN_STATEMENT = "statement";
    const std::string TOKEN_TAG = "tag";
    const std::string TOKEN_EXPRESSION = "expression";
    const std::string TOKEN_LITERAL = "literal";
    const std::string TOKEN_EOF = "eof";

    const std::regex re_whitespace{R"(\s*)"};
    const std::regex re_endraw{R"(\{%-?\s*endraw\s*-?%})"};

    struct Token
    {
        unsigned int linenum;
        std::string type;
        std::string value;
    };

    // typedef std::tuple<unsigned int, std::string, std::string>
    typedef std::vector<Token> stream_t;

    namespace lex
    {
        class State
        {
        private:
            const std::string &source_;
            std::string::const_iterator it_;
            const std::string::const_iterator begin_;
            const std::string::const_iterator end_;

            unsigned int linenum_{0};
            unsigned int Position();

        public:
            State(const std::string &source);
            bool End();
            bool At(const std::string &str);
            bool At(const std::regex &pattern);
            std::string Read(const std::regex &pattern, std::smatch *match);
            std::string ReadUntil(const std::regex &pattern, std::smatch *match);
            void EatEnd(const std::regex &pattern, std::smatch *match, bool strip_tags);

            unsigned int linenum();
        };

        class Lexer
        {
        private:
            std::string statement_start_;
            std::string statement_end_;
            std::string tag_start_;
            std::string tag_end_;
            bool strip_tags_;
            std::regex re_statement_start_;
            std::regex re_statement_end_;
            std::regex re_tag_start_;
            std::regex re_tag_end_;
            std::regex re_literal_end_;
            std::regex re_name_end_;

        public:
            Lexer();
            Lexer(std::string statement_start,
                  std::string statement_end,
                  std::string tag_start,
                  std::string tag_end);

            stream_t Tokenize(const std::string &source);
        };

    } // namespace lex
} // namespace liquid
#endif // LIQUID_LEX_