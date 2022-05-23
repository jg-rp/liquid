(function liquidPrism(Prism) {
  Prism.languages.liquid = {
    "comment-tag": {
      pattern:
        /(^\{%-?\s*comment\s*-?%\})[\s\S]+(?=\{%-?\s*endcomment\s*-?%\}$)/,
      lookbehind: true,
      alias: "comment",
    },
    "alt-comment": {
      pattern: /^\{#[\s\S]*?#\}$/,
      alias: "comment",
    },
    "inline-comment-tag": {
      pattern: /(^\{%-?\s*)#.*?(?=-?%\})/s,
      lookbehind: true,
      inside: {
        comment: {
          pattern: /(^\s*)#.*?(?=\n|$)/m,
          lookbehind: true,
        },
      },
    },
    "liquid-tag": {
      pattern: /(\{%-?\s*liquid)\s+.*?(?=-?%\})/s,
      greedy: true,
      lookbehind: true,
      inside: {
        comment: {
          pattern: /(\n\s*)#.*?$/ms,
          lookbehind: true,
        },
        tag: {
          pattern: /(\n\s*)\w+/,
          lookbehind: true,
          alias: "keyword",
        },
      },
    },
    tag: {
      pattern: /(^\{%-?\s*)\w+/,
      lookbehind: true,
      alias: "keyword",
    },
    string: {
      pattern: /"[^"]*"|'[^']*'/,
      greedy: true,
    },
    delimiter: {
      pattern: /^\{[{%]-?|-?[}%]\}$/,
      alias: "punctuation",
    },
    filter: {
      pattern: /(\|\s*)\w+/,
      lookbehind: true,
      alias: "function",
    },
    operator: /!?=|<=?|>=?|<>|\.\./,
    keyword:
      /\b(?:and|contains|in|limit|offset|or|reversed|with|empty|blank)\b/,
    builtin: {
      pattern: /(\b\.)(?:first|last|size)\b/,
      lookbehind: true,
    },
    number: /\b\d+(?:\.\d+)?\b/,
    boolean: /\b(?:false|nil|true)\b/,
    "attr-name": /\b\w+(?=\s*:)/,
    variable: /\b\w+\b/,
    punctuation: /[[\](),.:]/,
  };

  const liquid_tag = Prism.languages.liquid["liquid-tag"];
  liquid_tag.inside.string = Prism.languages.liquid.string;
  liquid_tag.inside.filter = Prism.languages.liquid.filter;
  liquid_tag.inside.operator = Prism.languages.liquid.operator;
  liquid_tag.inside.keyword = Prism.languages.liquid.keyword;
  liquid_tag.inside.builtin = Prism.languages.liquid.builtin;
  liquid_tag.inside.number = Prism.languages.liquid.number;
  liquid_tag.inside.boolean = Prism.languages.liquid.boolean;
  liquid_tag.inside["attr-name"] = Prism.languages.liquid["attr-name"];
  liquid_tag.inside.variable = Prism.languages.liquid.variable;
  liquid_tag.inside.punctuation = Prism.languages.liquid.punctuation;

  const pattern =
    /\{%?-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}|\{\{.*?\}\}|\{%.*?%\}|\{#.*?#\}/gs;
  const markupTemplating = Prism.languages["markup-templating"];
  let insideRaw = false;

  Prism.hooks.add("before-tokenize", function (env) {
    markupTemplating.buildPlaceholders(
      env,
      "liquid",
      pattern,
      function (match) {
        let tagMatch = /^\{%-?\s*(\w+)/.exec(match);
        if (tagMatch) {
          let tag = tagMatch[1];
          if (tag === "raw" && !insideRaw) {
            insideRaw = true;
            return true;
          } else if (tag === "endraw") {
            insideRaw = false;
            return true;
          }
        }

        return !insideRaw;
      }
    );
  });
  Prism.hooks.add("after-tokenize", function (env) {
    markupTemplating.tokenizePlaceholders(env, "liquid");
  });
})(Prism);
