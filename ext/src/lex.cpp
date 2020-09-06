#include <iostream>
#include <iterator>

#include "lex.h"
#include "strings.h"

namespace liquid::lex
{
	State::State(const std::string &source)
		: source_{source},
		  it_{source.cbegin()},
		  begin_{source.cbegin()},
		  end_{source.cend()},
		  linenum_{1} {}

	unsigned int State::linenum() { return linenum_; }

	bool State::End() { return it_ == end_; }

	bool State::At(const std::string &str)
	{
		unsigned int pos = Position();
		return source_.rfind(str, pos) == pos;
	}

	unsigned int State::Position() { return std::distance(begin_, it_); }

	std::string State::ReadUntil(const std::regex &pattern, std::smatch *match)
	{
		int pos = Position();
		std::string result;

		bool matched = std::regex_search(it_, end_, *match, pattern);

		if (matched)
		{
			int length = match->prefix().length();
			result = source_.substr(pos, length);
			it_ += length;
		}
		else
		{
			// Read until end of string
			result = source_.substr(pos);
			it_ = end_;
		}

		linenum_ += std::count(result.begin(), result.end(), '\n');
		return result;
	}

	std::string State::Read(const std::regex &pattern, std::smatch *match)
	{
		int pos = Position();
		std::string result;

		bool matched = std::regex_search(it_, end_, *match, pattern);

		if (matched && match->position(0) == 0)
		{
			result = source_.substr(pos, match->length());
			it_ += match->length();
			linenum_ += std::count(result.begin(), result.end(), '\n');
		}

		return result;
	}

	void State::EatEnd(const std::regex &pattern, std::smatch *match, bool strip_tags)
	{
		std::string value = Read(pattern, match);
		if (strip_tags || value.find('-') != std::string::npos)
		{
			Read(re_whitespace, match);
		}
	}

	// TODO: Escape and compile regexes from strings.
	Lexer::Lexer(std::string statement_start,
				 std::string statement_end,
				 std::string tag_start,
				 std::string tag_end)
		: statement_start_{statement_start},
		  statement_end_{statement_end},
		  tag_start_{tag_start},
		  tag_end_{tag_end},
		  strip_tags_{false},
		  re_statement_start_{R"(\{\{-?\s*)"},
		  re_statement_end_{R"(\s*-?}})"},
		  re_tag_start_{R"(\{%-?\s*)"},
		  re_tag_end_{R"(\s*-?%})"},
		  re_literal_end_{R"(\{[\{%]-?)"},
		  re_name_end_{R"(\s|-?%})"} {}

	Lexer::Lexer()
	{
		statement_start_ = "{{";
		statement_end_ = "}}";
		tag_start_ = "{%";
		tag_end_ = "%}";
		strip_tags_ = false;
		re_statement_start_ = R"(\{\{-?\s*)";
		re_statement_end_ = R"(\s*-?}})";
		re_tag_start_ = R"(\{%-?\s*)";
		re_tag_end_ = R"(\s*-?%})";
		re_literal_end_ = R"(\{[\{%]-?)";
		re_name_end_ = R"(\s|-?%})";
	}

	stream_t Lexer::Tokenize(const std::string &source)
	{
		State state{source};
		stream_t tokens;
		std::string name;
		std::string value;
		unsigned int linenum;
		std::smatch match;

		while (!state.End())
		{
			if (state.At(statement_start_))
			{
				// The start of an output statement.
				//
				// Eat the start statement sequence (traditionally "{{") and any
				// whitespace control character. Preceding tokens will have read
				// ahead to inspect whitepsace control and right-stripped
				// accordingly.
				state.Read(re_statement_start_, &match);

				// Read the statement expression. That's everything up to the next
				// end statement sequence, including filters and filter arguments.
				// Expression lexing is left up to the `Statement` pseudo tag in its
				// `parse` method.
				linenum = state.linenum();
				value = state.ReadUntil(re_statement_end_, &match);
				tokens.push_back(Token{linenum, TOKEN_STATEMENT, value});

				// Eat the end statement sequence (traditionally "}}") and check to
				// see if someone forgot to end their output statement.`eat_end`
				// will strip upcoming whitespace if the control character is set.
				state.EatEnd(re_statement_end_, &match, strip_tags_);
			}
			else if (state.At(tag_start_))
			{
				// The start of a tag. Could be the start or end of a tag block, or
				// non-block tag.

				// Eat the start tag sequence (traditionally "{%") and any whitespace
				// control character.
				state.Read(re_tag_start_, &match);

				// Every tag starts with a name, terminated by whitespace or an end
				// tag sequence.
				linenum = state.linenum();
				name = state.ReadUntil(re_name_end_, &match);
				tokens.push_back(Token{linenum, TOKEN_TAG, name});

				// Everything between the tag name and end tag sequence is the tag's
				// expression, which is possibly empty. Lexing of tag expressions
				// happens in the `parse` method of the tag definition class.
				linenum = state.linenum();
				value = state.ReadUntil(re_tag_end_, &match);
				strings::strip(&value);
				if (!value.empty())
				{
					tokens.push_back(Token{linenum, TOKEN_EXPRESSION, value});
				}

				// Eat the end tag sequence (traditionally "%}") and check to see if
				// someone forgot to close their tag.
				state.EatEnd(re_tag_end_, &match, strip_tags_);

				// Special case for "raw" tags. Treat everything up to the next "ENDRAW"
				// tag as a template literal.
				if (name == "raw")
				{
					linenum = state.linenum();
					value = state.ReadUntil(re_endraw, &match);
					tokens.push_back(Token{linenum, TOKEN_LITERAL, value});
				}
			}
			else
			{
				// A template literal. Thats anything that is not inside an output
				// statement or tag. Other than controlling leading or trailing
				// whitespace, template literals are passed through unchanged.
				linenum = state.linenum();
				value = state.ReadUntil(re_literal_end_, &match);
				if (match.str(0).back() == '-')
				{
					strings::rstrip(&value);
				}
				tokens.push_back(Token{linenum, TOKEN_LITERAL, value});
			}
		}

		tokens.push_back(Token{state.linenum(), TOKEN_EOF, ""});
		return tokens;
	}
} // namespace liquid::lex

int main()
{
	std::string s = "<html><title>{{ product.title\n -}}\n</title>\n\n{%- if true %}hello{% endif %}</html>";
	liquid::lex::Lexer lexer;
	auto tokens = lexer.Tokenize(s);

	for (auto tok : tokens)
	{
		std::cout << "Token(linenum=" << tok.linenum << ", type='" << tok.type << "', value='" << tok.value << "')\n";
	}
}
